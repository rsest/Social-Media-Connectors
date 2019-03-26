from pytrends.request import TrendReq
import json
import pandas as pd

# Login to Google. Only need to run this once, the rest of requests will use the same session.
pytrend = TrendReq()
category = False

# Create payload and capture API tokens. Only needed for interest_over_time(), interest_by_region() & related_queries()
keys = ["the top"]
pytrend.build_payload(kw_list=keys, cat=1072, geo='', timeframe='now 7-d')
if category:
    categories = pytrend.categories()
    with open('categories.json', 'w') as outfile:
        json.dump(categories, outfile, indent=2)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', 800)

# Real Time
realtimeTrends = pytrend.trending_realtime(cat='all', geo='US')
print(realtimeTrends.to_string())

# Real Time
dailyTrends = pytrend.top_daily(geo='US')
print(dailyTrends.to_string())

# Interest by Region
interest_by_region_df = pytrend.interest_by_region(resolution="COUNTRY")
print(interest_by_region_df.sort_values(keys[0], ascending=False))

# Related Queries, returns a dictionary of dataframes
related_queries_dict = pytrend.related_queries()

print(related_queries_dict[keys[0]]["top"])
print(related_queries_dict[keys[0]]["rising"])

hist = pytrend.get_historical_interest(keys, year_start=2019)
print(hist)
# Get Google Keyword Suggestions
suggestions_dict = pytrend.suggestions(keyword="queen victoria")
print(suggestions_dict)
