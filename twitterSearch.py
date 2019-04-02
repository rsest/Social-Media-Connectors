import json
import os

import tweepy

consumer_key = str(os.environ.get('twitter_consumer_key', ''))
consumer_secret = str(os.environ.get('twitter_consumer_secret', ''))
access_token = str(os.environ.get('twitter_access_token', ''))
access_token_secret = str(os.environ.get('twitter_access_token_secret', ''))
save_places = False

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

if save_places:
    places = api.trends_available()
    with open('twitter_places.json', 'w') as outfile:
        json.dump(places, outfile, indent=2)
        # api.reverse_geocode()
        # https: // developer.twitter.com / en / docs / geo / places - near - location / api - reference / get - geo - reverse_geocode
trends = api.trends_place(116545)
print(json.dumps(trends[0], indent=4))
pos = api.geo_search(lat=19.4326,long=-99.1332)

search_results = api.search(q="klar", geocode='19.4326,-99.133,30mi', count=30, include_entities=True)
search_hashtag = tweepy.Cursor(api.search, q="klar", geocode='19.4326,-99.133,200mi', include_entities=True).items(5000)
for tweet in search_hashtag:
    print(tweet.text)
    print(tweet.entities['urls'])
    if 'media' in tweet.entities:
        for image in tweet.entities['media']:
            print(image['media_url'])


public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)
