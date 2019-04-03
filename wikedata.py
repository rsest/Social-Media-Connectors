import ssl

import requests
from wikidata.client import Client

URL = 'https://query.wikidata.org/sparql'

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


def get_entity(entity: str):
    client = Client()  # doctest: +SKIP
    entity = client.get(entity, load=True)
    return entity


def get_freebase(id: str, type: str = "wdt:P646"):
    # wdt:P2671
    # wdt:P646

    query = """
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wikibase: <http://wikiba.se/ontology#>
    
    SELECT   ?sLabel  WHERE {
    
     ?s """ + type + """ '""" + id + """' 
       SERVICE wikibase:label {
        bd:serviceParam wikibase:language 'en' .
       }
     }
    """
    r = requests.get(URL, params={'format': 'json', 'query': query})
    if r.status_code == 200 and len(r.json()["results"]["bindings"]) > 0:
        return r.json()["results"]["bindings"][0]["sLabel"]["value"]
    return None


print(get_freebase("/g/11bxf4crlf", type="wdt:P2671"))
print(get_freebase("/m/04wzr", type="wdt:P646"))
