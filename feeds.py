news_rss_url = "https://www.yahoo.com/news/rss/science/"
import ssl

import feedparser

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

info = feedparser.parse(news_rss_url)
for entry in info.entries:
    print(entry.title)
