##Twitter Haverster Vic level
import tweepy
import json
from textblob import TextBlob
import time
import couchdb
import json
import pandas as pd
from http.client import IncompleteRead as http_incompleteRead
from urllib3.exceptions import IncompleteRead as urllib3_incompleteRead
import os
path = os.getcwd()
# import sys


# from datetime import datetime

#connect to couchDB
def collect_server(user, password):
    try:
        couchServer = couchdb.Server('http://%s:%s@45.113.234.122:5984/' % (user, password))
        print('Couchdb is conllected')
        return couchServer
    except Exception as e:
        print(e)

def get_database(server_name, database_name):
    if database_name in server_name:
        db = server_name[database_name]
        print('get database: %s' % database_name)
        return db
    else:
        #create new database
        db = server_name.create(database_name)
        print('Database: %s not found. Created database' % database_name)
        return db


user = 'admin'
password = 'zse4ZSE'

couchServer = collect_server(user, password)
db = get_database(couchServer, 'tweet')


# tweeter key
consumer_key = 'syvBAqd7spC9PbV622K3UNaB6'
consumer_secret = 'IPcGyK1Op8MH1etJeVlmxOnaNg6t5zYoifSr1bOb0lxI179n3z'
access_token = '1385155978996322307-63mBdQYfKG6KEOElbh3HiPmW0XOyMH'
access_token_secret = 'BNy1fEx2I4TpKkVra491uNm5W2dlqxAhYgxnVO6UQZW89'

# authorization of tweet API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

Month={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,
"Sep":9,"Oct":10,"Nov":11,"Dec":12}
def get_time(stringdata):
    data = stringdata['created_at']
    data = stringdata['created_at']
    split=data.split(' ')
    year = split[5]
    month = Month[split[1]]
    day = split[2]
    time_split = split[3].split(':')
    hours = time_split[0]
    return year,month,day,hours

sa4_data = pd.read_csv(path + '/city_LGA.csv')
def match_lgaLocation(city_name):
    sa4_location = sa4_data[sa4_data['city_name']==city_name]['LGA_name']
    if len(sa4_location) == 0:
        sa4_location = 'Unknown'
    else:
        sa4_location = sa4_location.to_string(index = False)
    return(sa4_location)

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

def get_info(tweets_v1):
    tweet_list = []
    for tweet in tweets_v1:
        string = tweet._json
        try:
            if string['place']['place_type'] == 'city':
                tweet_dic = {}
                tweet_dic['id'] = string['id_str']
                tweet_time = get_time(string)
                tweet_dic['year'] = int(tweet_time[0])
                tweet_dic['month'] = tweet_time[1]
                tweet_dic['day'] = int(tweet_time[2])
                tweet_dic['hours'] = tweet_time[3]
                city_name = string['place']['name']
                tweet_dic['city_name'] = city_name
                tweet_dic['lga_name'] = match_lgaLocation(city_name)
                tweet_dic['city_name'] = city_name.lower()
                text_string = string['text']
                info = sentiment_score(text_string)
                tweet_dic['sentiment_type'] = info[2]  # type_sentiment
                tweet_dic['sentiment_score'] = info[0]  # sentiment_score
                tweet_dic['subjectivity_score'] = info[1]
                tweet_dic['text'] = text_string
                tweet_dic['coordinates'] = None
                if string['coordinates'] != None:
                    tweet_dic['coordinates'] = [string['coordinates']['coordinates'][1],string['coordinates']['coordinates'][0]]    
                tweet_list.append(tweet_dic)
            else:
                pass
        except TypeError:
            pass
    return tweet_list

    
id_list = []
max_id = 9999999999999999999999
while True:
    try:
        tweets_v1 = api.search(q='place:0ec0c4fcacbd0083 lang:en', max_id=max_id)
        tweet_dic = get_info(tweets_v1)
        for element in tweet_dic:
            if len(element) == 0:
                print('empty dic. pass')
                pass
            elif element['lga_name'] == 'Unknown':
                print('Unknown lga_name. pass.')
                pass
            else:
                new_tweet_id = element['id']
                id_list.append(new_tweet_id)
                match = None
                if new_tweet_id not in db:
                    db.save(element)
                try:
                    length = len(id_list)-1
                    current_id = int(id_list[length]) - 1
                    if current_id == max_id:
                        print("no more request:reach 7 days with current_id: ", current_id)
                        time.sleep(20 * 60)
                        max_id = 9999999999999999999
                        continue
                    max_id = current_id
                    time.sleep(5)
                except IndexError:
                    print('Index error. No record')
                break
        # handle rate limit
    except tweepy.RateLimitError as e:
        print(e)
        print('exceed limit :( sleep more than 15 mins to restart')
        # sleep 15 minutes
        time.sleep(16 * 60)
        print('sleep ended :)')
        continue
    except BaseException as e:
        print(e)
        time.sleep(15)
        continue
    except http_incompleteRead as e:
        print(e)
        print('http.client incomplete read')
        time.sleep(15)
        continue
    except urllib3_incompleteRead as e:
        print(e)
        print('urllib3 incomplete read')
        time.sleep(15)
        continue

    except couchdb.http.ResourceConflict as e:
        print(e)
        time.sleep(10)
        continue

    except Exception as e:
        print(e)
        print('sleep 15 mins to restart :(')
        time.sleep(15 * 60)
        print('sleep end :)')
        continue
