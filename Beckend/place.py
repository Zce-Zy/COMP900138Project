#show 10 places data
import couchdb
import json
import os
import string
import re
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
import pandas as pd
from wordcloud import WordCloud
import io
import base64
import pandas as pd
import wordcloud
from shapely.geometry import shape, Point, Polygon


chad = Point(-37.886736, 145.083133).buffer(0.005)
stkilda = Polygon([(-37.833419, 144.972735),(-37.867016, 144.978720),(-37.873430, 144.939447),(-37.840406, 144.931522)])
qvmarket = Point(-37.807655, 144.958094).buffer(0.0025)
unimelb = Point(-37.797123, 144.961023).buffer(0.004)
central = Point(-37.812182, 144.962607).buffer(0.003)
rmit = Point(-37.808032, 144.963114).buffer(0.008)
marvel = Point(-37.816518, 144.947723).buffer(0.002)
monash = Point(-37.876269, 145.042363).buffer(0.002)
cricket = Point(-37.819937, 144.984092).buffer(0.003)
gallery = Point(-37.822126, 144.968837).buffer(0.003)

ten_place = [chad,stkilda,qvmarket,unimelb,central,rmit,marvel,monash,cricket,gallery]
place_name = ['chad','stkilda','qvmarket','unimelb','central','rmit','marvel','monash','cricket','gallery']


try:
    couch = couchdb.Server('http://user:pass@127.0.0.1:5984')
    db = couch['tweet']
except:
    try:
        couch = couchdb.Server('http://user:pass@172.26.131.22:5984')
        db = couch['tweet']
    except:
        try:
            couch = couchdb.Server('http://user:pass@172.26.133.132:5984')
            db = couch['tweet']
        except Exception as e:
            print("Can not access to the database! \n Please Check your internet.")

##Solve tweet text
def tweet_clean(tweet):
    engstop = set(stopwords.words('english'))
    sent_no_tickers=re.sub(r'\$\w*','',tweet)
    tknzr = TweetTokenizer(strip_handles=True, reduce_len=True)
    temp_tw_list = tknzr.tokenize(sent_no_tickers)
    # Remove stopwords
    list_no_stopwords=[i for i in temp_tw_list if i.lower() not in engstop]
    # Remove hyperlinks
    list_no_hyperlinks=[re.sub(r'https?:\/\/.*\/\w*','',i) for i in list_no_stopwords]
    # Remove hashtags
    list_no_hashtags=[re.sub(r'#', '', i) for i in list_no_hyperlinks]
    # Remove Punctuation and split 's, 't, 've with a space for filter
    list_no_punctuation=[re.sub(r'['+string.punctuation+']+', ' ', i) for i in list_no_hashtags]
    # Remove multiple whitespace
    new_sent = ' '.join(list_no_punctuation)
    # Remove characters beyond Basic Multilingual Plane (BMP) of Unicode:
    tweet_no_emojis = ''.join(c for c in new_sent if c <= '\uFFFF') # Apart from emojis (plane 1), this also removes historic scripts an
    # Remove any words with 2 or fewer letters
    filtered_list = tknzr.tokenize(tweet_no_emojis)
    list_filtered = [re.sub(r'^\w\w?$', '', i) for i in filtered_list]
    ##Delete some Garbled and make sure have only number and english.
    list_filtered =[i for i in list_filtered if i.isalnum()]
    filtered_sent =' '.join(list_filtered)
    clean_sent=re.sub(r'\s\s+', ' ', filtered_sent)
    #Remove any whitespace at the front of the sentence
    clean_sent=clean_sent.lstrip(' ')
    return clean_sent

#Get high frequency
def word_count(str):
    counts = dict()
    words = str.split()

    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
    high = dict(sorted(counts.items(), key=lambda item: item[1],reverse=True))
    
    return high
def changetime(dic):
    changetime=[]
    for key, value in dic.items():
        changetime.append(value)
    for i in range(10):
        changetime.insert(0,changetime.pop())
    dic1 = {}
    for i in range(0,24):
        dic1[i] = changetime[i]
    return dic1


#encode wordcloud
def get_word_cloud(text):
    try:
        pil_img = WordCloud(width=800, height=300, background_color="white").generate(text=text).to_image()
        img = io.BytesIO()
        pil_img.save(img, "PNG")
        img.seek(0)
        img_base64 = base64.b64encode(img.getvalue()).decode()
    except Exception as e:
        img_base64 = None
    return img_base64

##spend to much time, run once and get the answer,put in to benkhand
def quicktest1():
    path = os.getcwd()
    with open( path + '/exdata/10place_oneday.json') as f:
        data = json.load(f)
    return data

def quicktest2(name):
    path = os.getcwd()
    with open( path + '/exdata/10place_hour.json') as f:
        data = json.load(f)
    return data[name]

def get_place_info(place):
    allinfo = {}
    point = []
    Text = ""
    for item in db.view('Sentiment/Coordinates',stale = "update_after"):
        if place.contains(Point(item['value'])):
            point.append(item['value'])
            Text += tweet_clean(item['key'][1])
    wordpic = get_word_cloud(Text)
    freq = word_count(Text)
    allinfo['points'] = point
    allinfo['pic'] = wordpic
    allinfo['word'] = freq
    return allinfo


def get_hour_place(place):
    point = {}
    text = {}
    pic = {}
    word = {}
    for i in range(0,24):
        point[i] = []
        text[i] = ""
    for item in db.view('Sentiment/Coordinates',stale = "update_after"):
        if place.contains(Point(item['value'])):
            for i in range(0,24):
                if int(item['key'][0]) == i:
                    point[i].append(item['value'])
                    text[i] += tweet_clean(item['key'][1])
                    break
    for i in range(0,24):
        pic[i] = get_word_cloud(text[i])
        word[i] = word_count(text[i])
        
    
    output = {}
    output['point'] = changetime(point)
    output['pic'] = changetime(pic)
    output['word'] = changetime(word)
    return output

def day_place():
    all_data = {}
    for i in range(10):
        all_data[place_name[i]] = get_place_info(ten_place[i])
    return all_data

def hour_place():
    all_data = {}
    for i in range(10):
        all_data[place_name[i]] = get_hour_place(ten_place[i])
    return all_data
