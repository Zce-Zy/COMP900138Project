import json
import pandas as pd
from textblob import TextBlob

twitter = pd.read_json("draft1.json")

def sentiment_score(text_string):
    analysis = TextBlob(text_string)
    score_polarity = analysis.sentiment.polarity
    score_subjectivity = analysis.sentiment.subjectivity
    type_sentiment = 'neutral'
    if score_polarity > 0:
        type_sentiment = 'positive'
    elif score_polarity < 0:
        type_sentiment = 'negative'
    return score_polarity, score_subjectivity, type_sentiment

import pandas as pd
sa4_data = pd.read_csv('city_LGA.csv')
def match_lgaLocation(city_name):
    sa4_location = sa4_data[sa4_data['city_name'].str.lower()==city_name]['LGA_name']
    if len(sa4_location) == 0:
        sa4_location = 'Unknown'
    else:
        sa4_location = sa4_location.to_string(index = False)
    return(sa4_location)

tweet_all_dic = {}
datalist = []
for index, row in twitter.iterrows():
    data = {}
    text_string=row[2]['doc']['text']
    score_polarity, score_subjectivity, type_sentiment = sentiment_score(text_string)
    data['id'] =row[2]['id']
    data['year']=row[2]['key'][1]
    data['month']=row[2]['key'][2]
    data['day'] = row[2]['key'][3]
    data['hours'] = row[2]['doc']['created_at'].split(' ')[3].split(':')[0]
    data['city_name'] = row[2]['key'][0]
    data['lga_name'] = match_lgaLocation(row[2]['key'][0])
    data['sentiment_type'] = type_sentiment
    data['sentiment_score'] = score_polarity
    data['subjectivity_score'] = score_subjectivity
    data['text'] = row[2]['doc']['text']
    data['coordinates'] = None
    if data['lga_name'] == "Unknown":
        pass
    else:
        datalist.append(data)

tweet_all_dic['docs'] = datalist

print(tweet_all_dic)

with open('no1.json', 'w') as f:
    json.dump(tweet_all_dic, f, indent=2)
print('All tweet saved :)')