import pytumblr
import os

apikey = str(os.environ.get('tumblr_apikey', ''))
# Authenticate via API Key
client = pytumblr.TumblrRestClient(apikey)

blogName = "cafe"
params = {}

client.blog_info(blogName)  # get information about a blog
client.posts(blogName, **params)  # get posts for a blog
client.avatar(blogName)  # get the avatar for a blog
client.blog_likes(blogName)  # get the likes on a blog
client.followers(blogName)  # get the followers of a blog
client.blog_following(blogName)  # get the publicly exposed blogs that [blogName] follows
client.queue(blogName)  # get the queue for a given blog
client.submission(blogName)  # get the submissions for a given blog

# Make the request
client.posts('staff', limit=2000, offset=0, reblog_info=True, notes_info=True, filter='html')
# print out into a .txt file
with open('out.txt', 'w') as f:
    print(f, client.posts('staff', limit=2000, offset=0, reblog_info=True, notes_info=True, filter='html'))


def getAllPosts(client, blog):
    offset = 0
    while True:
        posts = client.posts(blog, limit=20, offset=offset)
        if not posts:
            return

        for post in posts:
            yield post

        offset += 20


blog = ('staff')
