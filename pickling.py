import re

import lyrics as ly
import json
from pathlib import Path
import pandas as pd

from spacy.lang.fr import French

regles = re.compile(r"""(([A-zÄ-ÿ])(\2)+)|((-"?\w+)|(\w+"?-))|([^A-zÄ-ÿ]+)|(('+)|(\++))|([A-ZÄ-Ÿ]{2,})|(((o|O)+u*h*)+)|(((a|A)+h*)+)|(([eEéÉ]+u*h*)+)|(((o|O)u?l?)+)|(((B|b)r+)+)|((la)+)|(((\\x)|(\\u)|(\\n)|(x?\d+)).*)""")
def tokenize(chaine):
    temp = [token.text for token in tokenizer(chaine)]
    # Permet de découper sur les apostrophes, les tirets, etc. Utile pour les abréviations, les mots composés, etc.
    return [s for e in temp for s in re.split(r"(\W)", e) if s]


def preclean(chaine):
    chaine = chaine.replace(u"\xa0", " ")
    chaine = chaine.replace(u"\u2009", " ")
    chaine = chaine.replace(u"\u200b", " ")
    chaine = chaine.replace(u"\u200c", " ")
    return chaine.replace(u"\u200d", " ")


def clean_word(word):
    """Nettoie les mots pour ne garder que les mots qui pourraient être des néologismes
    :param word: mot à "nettoyer"
    :return: mot nettoyé, None si ce n'est pas un mot qui pourrait être un néologisme
    Les regex présentes ici sont la version non compilée, laissées pour la compréhension
    cependant elles ne seront jamais utilisées (apres un if False) pour des raisons de performances
    On utilise une regex compilée, rassemblant toutes les regex ci-dessous
    """

    try:
        word = word.strip()  # on enlève les espaces
        word = word.strip(".,;“…’:!”?\"()[]{}«»×*")  # on enlève les signes bizarres
    except:
        print(word)  # pour voir ce qui pose problème, normalement que les "None"
        return

    # On vire les chaînes bizarres que l'on a pu trouver dans les paroles + les "refrain", "couplet", etc.
    if word in {
        '"-"',
        "à-ç",
        "Outro",
        "Intro",
        "Refrain",
        "Couplet",
        "Pont",
        "Outro",
        "Pré-refrain",
        "Pré-refrain",
        "Kèskizon",
        "Kèskifon",
        "Sékoidon",
        "Waouuum",
        "Wouuum",
        "Tralalilala",
        "Ayayay",
        "Wouah",
        "Troop",
        "Pête",
        "Beep",
        "Décidemment",
        "Aujourd",
        "aujourd",
        "hui",
        "released",
        "mmh",
        "capuché",
        "Capuché",
    }:
        return
    if re.fullmatch(regles, word):  # Bruit
        return
    if False:
        # Mots en majuscules = acronyme donc pas néologisme, par contre si minuscules après, on garde
        if re.fullmatch(r"[A-ZÄ-Ÿ]{2,}", word):
            return
        # les mots qui commencent ou finissent par un tiret, abréviations,
        # lors de la retranscription des paroles, donc pas néologismes
        if re.fullmatch('(-"?\w+)|(\w+"?-)', word):
            return
        # pas de lettres donc pas néologismes, on rappelle que fullmatch cherche à faire correspondre toute la chaîne
        if re.fullmatch(r"[^A-zÄ-ÿ]+", word):
            return
        if re.fullmatch(r"('+)|(\++)", word):  # Bruit
            return
        if re.fullmatch(r"([A-zÄ-ÿ])(\1)+", word):  # qu'une seule lettre répétée plusieurs fois donc pas néologisme
            return
        # Tous ceux là sont des bruits retranscrits donc pas néologismes, ce qui nous intéresse
        # en tout cas c'est ce qui est produit par le chanteur
        if re.fullmatch(r"((o|O)+u*h*)+", word):  # Ooooh, Oh, etc. Bruit
            return
        if re.fullmatch(r"((a|A)+h*)+", word):
            return
        if re.fullmatch(r"([eEéÉ]+u*h*)+", word):
            return
        if re.fullmatch(r"((o|O)u?l?)+", word):
            return
        if re.fullmatch(r"((B|b)r+)+", word):
            return
        if re.fullmatch(r"(la)+", word):
            return
        if re.fullmatch(r"((\\x)|(\\u)|(\\n)|(x?\d+)).*", word):  # symboles d'échappement donc pas néologismes
            return

    return word


def only_letters(word):
    if not (word and re.fullmatch(r"[A-zÄ-ÿ]+", word)): return
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
