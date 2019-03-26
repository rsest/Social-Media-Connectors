import praw
import os

client_id = str(os.environ.get('reddit_client_id', ''))
client_secret = str(os.environ.get('reddit_client_secret', ''))
password = str(os.environ.get('reddit_password', ''))
user_agent = str(os.environ.get('reddit_user_agent', ''))
username = str(os.environ.get('reddit_username', ''))

# https://www.reddit.com/dev/api
reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,
                     password=password, user_agent=user_agent,
                     username=username)

all = reddit.subreddit("all")
for i in all.search("yellow car", limit=5):
    print(i.title)

cars = reddit.subreddit("cars")
for i in cars.search("yellow car", sort='new', limit=5):
    print(i.title)

    for comment in i.comments.list():
        print(comment.body)

subreddit = reddit.subreddit('all').hot()
for post in subreddit:
    print(post.title)
    print(post.url)
    print(post.media)
    print(post.media_embed)
