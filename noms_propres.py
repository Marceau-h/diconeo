import pandas as pd
from collections import Counter

def get_neo_freq(neo):
    return Counter(neo)


toremove = set()
tolower = []

df_artistes_neo_fr = pd.read_pickle("df_artistes_neo_fr.pkl")

df_artistes_neo_fr["neo_freq"] = df_artistes_neo_fr["neologismes"].apply(get_neo_freq)

allfreq = df_artistes_neo_fr["neo_freq"].sum()

notlower = [(word, freq) for word, freq in allfreq.items() if not word[0].islower()]

for word, freq in notlower:
    if word.lower() in allfreq:
        if (freq / (allfreq[word.lower()]+freq)) > 0.75:
            toremove.add(word)
            # print(word, freq, allfreq[word.lower()])
        else:
            tolower.append((word, freq))
    else:
        toremove.add(word)

for word in toremove:
    del allfreq[word]

for word, freq in tolower:
    allfreq[word.lower()] += freq
    del allfreq[word]

# On aurait pu factoriser les tolower et toremove, mais c'est plus clair comme ça
df_artistes_neo_fr["all_len"] = df_artistes_neo_fr["neologismes"].apply(len)
df_artistes_neo_fr["neologismes"] = df_artistes_neo_fr["neologismes"].apply(lambda x: [word for word in x if word in allfreq])
df_artistes_neo_fr["nompropre_len"] = df_artistes_neo_fr["all_len"] - df_artistes_neo_fr["neologismes"].apply(len)
df_artistes_neo_fr["neo_len"] = df_artistes_neo_fr["neologismes"].apply(len)
df_artistes_neo_fr["neo_freq"] = df_artistes_neo_fr["neo_freq"].apply(lambda x: {word: freq for word, freq in x.items() if word in allfreq})

df_artistes_neo_fr.to_pickle("df_artistes_neo_fr_no_names.pkl")

print(allfreq.most_common(100))
