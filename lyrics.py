import json
import re
from pathlib import Path
from datetime import datetime
import langid
from numpy import mean, nan
from pandas import NaT

import SPARQL

music_dir = Path(__file__).parent / "Lyrics_all"

artists_det = {file.stem.split("_", 1)[1].lower(): file for file in music_dir.glob("Lyrics_*.json")}


class Artiste:
    dictart = artists_det
    name_parser = re.compile(r"[A-ZÀ-ÿ]+[a-zà-ÿ]*")  # re.compile(r"(\d+)|([A-ZÀ-ÿ]+[a-zà-ÿ]*)(?:\.?)")

    def __init__(self, name):
        self.dates = None
        self.date = None
        if isinstance(name, Path):
            name = name.stem.split("_", 1)[1]

        if name.lower() not in self.dictart:
            raise ValueError(
                f"Artiste {name} non trouvé, pour la liste des artistes, voir la variable de classe 'dictart'")

        self.file = self.dictart[name.lower()]
        if name.islower():
            self.name = name.title()
        elif name.isupper():
            self.name = name
        elif name.istitle():
            self.name = name
        elif name.isdigit():
            self.name = name
        else:
            self.parsed = re.findall(self.name_parser, name)

            try:
                self.name = "_".join(e for e in self.parsed)
            except Exception as e:
                print(self.parsed)
                raise e

        try:
            self.genres = SPARQL.get_genres(self.name)
        except Exception as e:
            print(self.name)
            print(self.file)
            raise e

        self.alternate_names = []
        self.api_path = None
        self.description = None
        self.id = None
        self.is_verified = None
        self.url = None

        self.albums = set()
        self.songs = set()

        self._load()

    def _load(self):
        with open(self.file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.alternate_names = data["alternate_names"]
        self.api_path = data["api_path"]
        self.description = data["description"]
        self.id = data["id"]
        self.is_verified = data["is_verified"]
        self.url = data["url"]

        self.process_songs(data["songs"])
        self.process_albums()

        self.process_date()

    def process_songs(self, songs):
        self.songs = {Song(song) for song in songs}

    def process_albums(self):
        self.albums = {song.album for song in self.songs}

    def process_date(self):
        if not self.songs:
            return

        self.dates = [song.release_date for song in self.songs]
        if not self.dates:
            return

        dates = [datetime.timestamp(date) for date in self.dates if date is not None]

        if not dates:
            # print(f"{self.name} : all None")
            return

        # print(f"{self.name} : {dates}")

        try:
            date = datetime.fromtimestamp(mean(dates))

        except TypeError as e:
            print(self.name)
            print(self.file)
            print(self.dates)
            raise e
        except ValueError as e:
            print(self.name)
            print(self.file)
            print(self.dates)
            raise e

        if date in (NaT, nan):
            return None
        elif date.year == 1970:
            return None

        # print(f"{self.name} : {date}")
        self.date = date

    def __dict__(self):
        return {
            "name": self.name,
            "genres": self.genres,
            "albums": self.albums,
            "songs": self.songs,
            "file": self.file,
            "date": self.date,
        }


class Song:
    def __init__(self, song_dict: dict):
        self.description = song_dict["description"]["plain"]
        self.full_title = song_dict["full_title"]
        self.state = song_dict["lyrics_state"]
        self.stats = song_dict["stats"]
        self.title_with_featured = song_dict["title_with_featured"]
        self.url = song_dict["url"]
        self.title = song_dict["title"]
        self.paroles = song_dict["lyrics"]
        if self.paroles is not None:
            self.lang = langid.classify(self.paroles)[0]
        else:
            self.lang = None

        date = song_dict["release_date"]
        self.release_date = datetime.strptime(date, "%Y-%m-%d") if ((date is not None) and (date != nan)) else None

        self.release_date_for_display = song_dict["release_date_for_display"]

        try:
            self.album = Album(song_dict["album"])

        except ValueError:
            self.album = None

    def __hash__(self):
        return hash(self.full_title)

    def __eq__(self, other):
        return self.full_title == other.full_title

    def __repr__(self):
        return f"<Song {self.full_title}>"

    def __str__(self):
        return self.paroles or ""

    def __lt__(self, other):
        if self.release_date is None:
            if other.release_date is None:
                pass
            else:
                return False

        elif other.release_date is None:
            return True

        else:
            if self.release_date != other.release_date:
                return self.release_date < other.release_date

        return self.full_title < other.full_title

    def __gt__(self, other):
        return not self.__lt__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, item):
        return item in self.paroles


class Album:
    def __init__(self, album_dict: dict):
        if album_dict is None:
            raise ValueError("Album non trouvé")
        self.api_path = album_dict["api_path"]
        self.full_title = album_dict["full_title"]
        self.id = album_dict["id"]
        self.name = album_dict["name"]
        self.url = album_dict["url"]

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url

    def __repr__(self):
        return f"<Album {self.full_title}>"

    def __str__(self):
        return self.full_title

    def __lt__(self, other):
        return self.id < other.id

    def __gt__(self, other):
        return not self.__lt__(other)

    def __le__(self, other):
        return self.id <= other.id

    def __ge__(self, other):
        return not self.__le__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, song: Song):
        return song.album == self


if __name__ == '__main__':
    nom = "Vald"

    artiste = Artiste(nom)
    print(artiste.name)
    print()
    print(artiste.albums)
    print()
    print(artiste.songs)
    print()
    print(artiste.dates)
    print()
    print(artiste.date)

    paroles, pas_paroles = 0, 0
    for song in artiste.songs:
        if song.paroles:
            paroles += 1
        else:
            pas_paroles += 1

    total = len(artiste.songs)

    print(
        f"\nNombre de chansons {total}\navec paroles: {paroles} ({paroles / total * 100:.2f}%)\nsans paroles: {pas_paroles} ({pas_paroles / total * 100:.2f}%)")
