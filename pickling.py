import re

import lyrics as ly
import json
from pathlib import Path
import pandas as pd

from spacy.lang.fr import French


def tokenize(chaine):
    return [token.text for token in tokenizer(chaine)]


def preclean(chaine):
    chaine = chaine.replace(u"\xa0", " ")
    chaine = chaine.replace(u"\u2009", " ")
    chaine = chaine.replace(u"\u200b", " ")
    chaine = chaine.replace(u"\u200c", " ")
    return chaine.replace(u"\u200d", " ")


def clean_word(word):
    try:
        word = word.strip()
    except:
        print(word)
        return
    word = word.strip(".,;“…’:!”?\"()[]{}«»×*")
    if re.fullmatch(r"((\\x)|(\\u)|(\\n)|(x?\d+)).*", word):
        return
    if '"-"' in word:
        return
    if word == 'à-ç':
        return
    if re.fullmatch('(-"?\w+)|(\w+"?-)', word):
        return
    if re.fullmatch(r"[^A-zÄ-ÿ]+", word):
        return
    if re.fullmatch(r"('+)|(\++)", word):
        return
    return word


def only_letters(word):
    if not (word and re.fullmatch(r"[A-zÄ-ÿ]+", word)) : return
    return word


def find_neo(songs):
    neologismes = set()

    for song in songs:
        if song.paroles:
            paroles = tokenize(preclean(song.paroles))
            for word in paroles:
                word = only_letters(clean_word(word))
                if word:
                    if word.lower() not in lexique_ultime:
                        neologismes.add(word)

    return neologismes


def songs_and_neo(artiste: str | Path | ly.Artiste) -> tuple:
    if isinstance(artiste, str | Path):
        artiste = ly.Artiste(artiste)

    name = artiste.name
    songs = artiste.songs
    neologismes = find_neo(songs)
    genres = artiste.genres
    date = artiste.date

    return songs, neologismes, genres, date, name,


################################
neo = 50
fr_songs = 20
################################

nlp = French()

tokenizer = nlp.tokenizer

lexiques = Path("lexiques").glob("*.json")

dict_lexiques = {
    fic.stem: set(json.load(fic.open(encoding="utf-8")))
    for fic in lexiques
}

lexique_ultime = set.union(*dict_lexiques.values())

artistes_files = Path("Lyrics_all").glob("*.json")
artistes_files = sorted(artistes_files)

print(f"Nombre d'artistes au total : {len(artistes_files)}")

dict_artistes = {
    e: songs_and_neo(e)
    for e in artistes_files
}

print("dict_artistes créé")

df = pd.DataFrame(dict_artistes).T
df.to_pickle("df_artistes_raw.pkl")

neover = df[df[1].apply(lambda x: len(x) > neo)]
neover.to_pickle("df_artistes_neo.pkl")
print(f"Nombre d'artistes avec au moins {neo} néologismes : {len(neover)}")

frver = df[df[0].apply(lambda x: len([e for e in x if e.lang == "fr"]) > fr_songs)]
frver.to_pickle("df_artistes_fr.pkl")
print(f"Nombre d'artistes avec au moins {fr_songs} chansons en français : {len(frver)}")

bothver = frver[frver.index.isin(neover.index)]
bothver.columns = ["songs", "neologismes", "genres", "date", "noms"]
bothver.to_pickle("df_artistes_neo_fr.pkl")
bothver.to_csv("df_artistes_neo_fr.csv", sep=";", encoding="utf-8", header=True)
bothver.to_json("df_artistes_neo_fr.json", indent=4, force_ascii=False)
print(f"Nombre d'artistes avec au moins {fr_songs} chansons en français et au moins {neo} néologismes : {len(bothver)}")
