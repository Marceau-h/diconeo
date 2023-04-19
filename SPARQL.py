from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import EndPointNotFound
from urllib.error import URLError
from time import sleep


def sparkles(query, ret_format=JSON):
    """Prend en entrée une requête SPARQL, renvoie un json sous forme de dictionnaire avec le résultat"""

    sparql = SPARQLWrapper("http://fr.dbpedia.org/sparql")  # http://dbpedia.org/sparql endpoint anglais NUL
    sparql.setReturnFormat(f"{ret_format}")
    sparql.setQuery(query)
    try:
        return sparql.queryAndConvert()
    except (EndPointNotFound, URLError):
        sleep(5)
        return sparql.queryAndConvert()
#


def get_genres(name):
    start = """
    select distinct ?g1 where {
    ?s1 rdf:type ?t1 .
    ?s1 rdfs:label ?o1 . 
    ?o1 bif:contains \'\""""
    end = """\"\' .
    ?s1 dbo:genre ?g1 .
    FILTER (?t1 IN (dbo:Band, schema:MusicGroup, schema:Person, dbo:Singer))
    }
    """
    mid = '\" AND \"'.join([e.strip() for e in name.split("_")])

    query = start + mid + end
    query.replace("\n", " ").replace("  ", " ")

    # print(query)

    res = sparkles(query)

    # print(res)

    return [e["g1"]["value"].split("/")[-1] for e in res["results"]["bindings"]]


if __name__ == '__main__':
    name = "Sheryfa_Luna"

    print(get_genres(name))



#
# def get_artist(name):
#     query = f"""
#     select distinct * where {{
#     ?s1 rdf:type ?t1 .
#     ?s1 rdfs:label ?o1 .
#     ?o1 bif:contains  "{name}" .
#     ?s1 dbo:genre ?g1 .
#     FILTER (?t1 IN (dbo:Band, schema:MusicGroup, schema:Person, dbo:Singer))
#     }}
#     LIMIT 100
#     """.replace("\n", " ")
#     return sparkles(query)
