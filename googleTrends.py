from pytrends.request import TrendReq
import json
import pandas as pd

pytrend = TrendReq()
category = False

pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', 800)

# Real Time
realtimeTrends = pytrend.trending_realtime(cat='all', geo='US')
print(realtimeTrends.to_string())

# Treding daily
dailyTrends = pytrend.top_daily(geo='US')
print(dailyTrends.to_string())


# Create payload and capture API tokens. Extract You Tube trends from last 30 days
pytrend = TrendReq()
pytrend.build_payload(kw_list=[], gprop='youtube', timeframe='today 1-m')

# Related Topics, returns a dictionary of dataframes
related_topics_dict = pytrend.related_topics()
print(related_topics_dict)

# Related Queries, returns a dictionary of dataframes
related_queries_dict = pytrend.related_queries()
print(related_queries_dict)



# Create payload and capture API tokens. Only needed for interest_over_time(), interest_by_region() & related_queries()
pytrend = TrendReq()
keys = ["the top"]
pytrend.build_payload(kw_list=keys, cat=0, geo='', timeframe='now 7-d')
if category:
    categories = pytrend.categories()
    with open('categories.json', 'w') as outfile:
        json.dump(categories, outfile, indent=2)





interest_by_region_df = pytrend.interest_by_region(resolution="COUNTRY")
print(interest_by_region_df.sort_values(keys[0], ascending=False).head(5))

# Related Topics, returns a dictionary of dataframes
related_topics_dict = pytrend.related_topics()
print(related_topics_dict[keys[0]]["top"].to_string())
print(related_topics_dict[keys[0]]["rising"].to_string())

# Related Queries, returns a dictionary of dataframes
related_queries_dict = pytrend.related_queries()
print(related_queries_dict[keys[0]]["top"].to_string())
print(related_queries_dict[keys[0]]["rising"].to_string())


#historical interest
hist = pytrend.get_historical_interest(keys, year_start=2019)
print(hist.to_string())

# Get Google Keyword Suggestions
suggestions_dict = pytrend.suggestions(keyword="Pacers vs Celtics")
print(suggestions_dict)


pytrend.build_payload(kw_list=[], cat=1072, geo='', gprop="youtube", timeframe='today 1-m')

# Related Topics, returns a dictionary of dataframes
related_topics_dict = pytrend.related_topics()
print(related_topics_dict[list(related_topics_dict)[0]]["top"])
print(related_topics_dict[list(related_topics_dict)[0]]["rising"])

# Related Queries, returns a dictionary of dataframes
related_queries_dict = pytrend.related_queries()
print(related_queries_dict[list(related_queries_dict)[0]]["top"])
print(related_queries_dict[list(related_queries_dict)[0]]["rising"])