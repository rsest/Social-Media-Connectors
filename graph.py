import requests
import os

API_KEY = str(os.environ.get('google_graph_API_KEY', ''))
URL = 'https://kgsearch.googleapis.com/v1/entities:search'


def google_searh(query: str, ids: str = "", languages: str = "en", limit: int = 10):
    if ids == "":
        key = 'query'
        value = query
    else:
        key = 'ids'
        value = ids

    params = {
        key: value,
        'limit': limit,
        'indent': True,
        'key': API_KEY,
        'languages': languages
    }
    r = requests.get(URL, params=params)
    return r.json()


print(google_searh("", ids="/g/11bxf4crlf", languages="en", limit=10))
print(google_searh("soccer", ids="", languages="en", limit=10))
