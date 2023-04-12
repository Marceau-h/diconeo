import json
from pathlib import Path

music_dir = Path(__file__).parent / "Lyrics_all"

artists_det = {file.stem.split("_", 1)[1].lower(): file for file in music_dir.glob("Lyrics_*.json")}


class Artiste:
    dictart = artists_det

    def __init__(self, name):
        if name.lower() not in self.dictart:
            raise ValueError(
                f"Artiste {name} non trouvé, pour la liste des artistes, voir la variable de classe 'dictart'")

        self.name = name
        self.file = self.dictart[name.lower()]

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

    def process_songs(self, songs):
        self.songs = {Song(song) for song in songs}

    def process_albums(self):
        self.albums = {song.album for song in self.songs}


class Song:
    def __init__(self, song_dict: dict):
        self.description = song_dict["description"]["plain"]
        self.full_title = song_dict["full_title"]
        self.state = song_dict["lyrics_state"]
        self.release_date = song_dict["release_date"]
        self.release_date_for_display = song_dict["release_date_for_display"]
        self.stats = song_dict["stats"]
        self.title_with_featured = song_dict["title_with_featured"]
        self.url = song_dict["url"]
        self.title = song_dict["title"]
        self.paroles = song_dict["lyrics"]

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
        return self.paroles


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


if __name__ == '__main__':
    nom = "Vald"
    artiste = Artiste(nom)
    print(artiste.name)
    print()
    print(artiste.albums)
    print()
    print(artiste.songs)

    paroles, pas_paroles = 0, 0
    for song in artiste.songs:
        if song.paroles:
            paroles += 1
        else:
            pas_paroles += 1

    print( f"Nombre de chansons avec paroles: {paroles}, sans paroles: {pas_paroles}")c
