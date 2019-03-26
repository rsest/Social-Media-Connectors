import sys

sys.path.append('/home/spnichol/Dropbox/youtube_tutorial/')
from youtube import youtube_videos

test = youtube_videos.youtube_search("spinners", location="40.730610, -73.935242", location_radius="50km")

geo_test = youtube_videos.geo_query('r2GYzQvfARo')

location_dict = {"youID": [], "lat": [], "lon": []}
for video in test[1]:
    location_dict['youID'].append((video['id']['videoId']))
    geo = youtube_videos.geo_query(video['id']['videoId'])
    location_dict['lat'].append(geo['items'][0]['recordingDetails']['location']['latitude'])
    location_dict['lon'].append(geo['items'][0]['recordingDetails']['location']['longitude'])

print(location_dict)
