import os
import facebook

token = str(os.environ.get('facebook_token', ''))
graph = facebook.GraphAPI(access_token=token, version=3.2)

g = facebook.GraphAPI(access_token=token, version=3.2)

friends = graph.get_connections(id='me', connection_name='friends')

places = graph.search(type='place',
                      center='37.4845306,-122.1498183',
                      fields='name,location',
                      q="cafe")

for place in places['data']:
    print('%s %s' % (place['name'].encode(), place['location'].get('zip')))
