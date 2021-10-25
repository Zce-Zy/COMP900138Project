from sklearn import tree
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from shapely.geometry import shape, Point, Polygon
import re, json
from collections import Counter
import serve
import couchdb
from nltk.tokenize import TweetTokenizer
import string
import pandas as pd
import os
import ast

try:
    couch = couchdb.Server('http://user:pass@127.0.0.1:5984')
    dbt = couch['tweet']
    dby = couch['youtube']
    dbf = couch['flickr']
except:
    try:
        couch = couchdb.Server(serve.getserve()[0])
        dbt = couch['tweet']
        dby = couch['youtube']
        dbf = couch['flickr']
    except:
        try:
            couch = couchdb.Server(serve.getserve()[1])
            dbt = couch['tweet']
            dby = couch['youtube']
            dbf = couch['flickr']
        except Exception as e:
            print("Can not access to the database! \n Please Check your internet.")


path = os.getcwd()

regex = re.compile('[^a-zA-Z ]')
stops = stopwords.words("english")
lemmatizer = WordNetLemmatizer()

##Places to check prediction

unimelbburnley = Point(-37.8285632,145.0207942).buffer(0.003)
rmit = Point(-37.808032, 144.963114).buffer(0.002)
unimelb = Point(-37.797123, 144.961023).buffer(0.004)
carlton = Point(-37.806332, 144.971204).buffer(0.001238)
albert = Polygon([(-37.842048, 144.958999),(-37.834353, 144.972602),(-37.856771, 144.982184),(-37.859224, 144.978155)
        ,(-37.850783, 144.966673)])
stkildabatch = Point(-37.865126, 144.972736).buffer(0.001150)
royalmelbournehospital = Point(-37.798892, 144.956195).buffer(0.00098)
vc = Point(-37.807316, 144.975151).buffer(0.0013)
botanical = Point(-37.829178, 144.976798).buffer(0.005281)
brighten = Polygon([(-37.900346, 144.979629),(-37.900129, 144.987167),(-37.927154, 144.987695),(-37.926745, 144.983320)])


names = ['unimelbburnley','rmit','unimelb','carlton',
'albert','stkildabatch','royalmelbournehospital','vc','botanical','brighten']
real_location = [unimelbburnley,rmit,unimelb,carlton,
albert,stkildabatch,royalmelbournehospital,vc,botanical,brighten]


#Show the score
def show_score():
    score_data = pd.read_json(path + '/exdata/simscore.json').to_json()
    return score_data





# Load training dataset and train model
X=[]
Y=[]
with open(path + '/exdata/eterm.txt') as data_file:
    for line in data_file:
        data = line.split(',')
        X.append(list(map(int,data[:4])))
        Y.append(data[4].strip())
clf = tree.DecisionTreeClassifier()
clf = clf.fit(X,Y)



hospital = wn.synset('hospital.n.01')
park = wn.synset('park.n.01')
beach = wn.synset('beach.n.01')
school = wn.synset('school.n.01')

def get_locationdata(location):
    data = []
    for item in dbt.view('CountData/Cor_ByYMDH',stale = "update_after",include_docs = True,start_key = [2018,1]):
        df = []
        df.append(item['doc']['text'])
        df.append(item['doc']['sentiment_score'])
        Box = location
        Lat = float(item['value'][0])
        Lon = float(item['value'][1])
        if Box.contains(Point(Lat,Lon)):
            df.append(float(item['value'][0]))
            df.append(float(item['value'][1]))
            time = item['doc']['hours']
            time = int(time) -10
            if time < 0:
                time += 24
            df.append(time)
            data.append(df)
    dtf = pd.DataFrame(data).rename(columns={0:"text",1:"sentiment_score",2:'Latitude',3:'Longitude',4:'time'})
    dataframe = dtf
    return dataframe


def get_ranks(data):
    text = data
    text = regex.sub('', text)
    text = re.sub( '\s+', ' ', text ).strip()
    filtered_text = [word for word in text.split(' ') if word not in stops]
    lemmatized_text = [lemmatizer.lemmatize(word)  for word in filtered_text]
    if len(text) > 0:
        ranks = [0.00,0.00,0.00,0.00]
        for word in lemmatized_text:
            try:
                test = wn.synset(word.lower() + '.n.01')
                f = beach.path_similarity(test)
                s = school.path_similarity(test)
                b = hospital.path_similarity(test)
                d = park.path_similarity(test)
                if f > 0.14:
                    ranks[0] = ranks[0] + f
                if s > 0.14:
                    ranks[1] = ranks[1] + s
                if b > 0.14:
                    ranks[2] = ranks[2] + b
                if d > 0.14:
                    ranks[3] = ranks[3] + d
            except Exception as e:
                pass
        ranks = [i * 10 for i in ranks]
        ranks = [int(i) for i in ranks]
        
        if any(i != 0 for i in ranks[:3]):
            return ranks


def prelocation(rank):
    if len(rank) > 0:
        prediction = clf.predict(rank)
        result = Counter(prediction).most_common()
        return result[0][0]
    else:
        return "not enough data"
def areas(tweet):
    alldata = []
    for index, row in tweet.iterrows():
        score = get_ranks(row['text'])
        if score is not None:
            alldata.append(score)
    return prelocation(alldata)


def predict_result(places):
    for i in range(10):
        if names[i] == places:
            location = real_location[i]
            data = get_locationdata(location)
            return areas(data)



def get_hashtag(date):
    wordlist = []
    date = ast.literal_eval(date)
    date = [int(n) for n in date]
    date1 = date.copy()
    date1[2] = date[2] +1
    Text = ""
    for item in dbt.view('CountData/text',start_key = date,end_key = date1,stale = "update_after",include_docs = True):
        Text += item['doc']['text']
    freq = re.findall(r"#(\w+)", Text)
    result = dict(sorted(Counter(freq).items(), key=lambda item: item[1],reverse=True))
    for key, value in result.items():
        record = {}
        record['name'] = key
        record['value'] = value
        wordlist.append(record)
    return wordlist


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
    #list_no_hashtags=[re.sub(r'#', '', i) for i in list_no_hyperlinks]
    # Remove Punctuation and split 's, 't, 've with a space for filter
    list_no_punctuation=[re.sub(r'['+string.punctuation+']+', ' ', i) for i in list_no_hyperlinks]
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


#Show topwords
def get_frequent_words(date):
    wordlist = []
    date = ast.literal_eval(date)
    date = [int(n) for n in date]
    date1 = date.copy()
    date1[2] = date[2] +1
    Text = ""
    for item in dbt.view('CountData/text',start_key = date,end_key = date1,stale = "update_after",include_docs = True):
        Text += tweet_clean(item['doc']['text'])
    freq = word_count(Text)
    for key, value in freq.items():
        record = {}
        record['name'] = key
        record['value'] = value
        wordlist.append(record)
    return wordlist


def overview(date):
    year = int(date.split(',')[0])
    month = int(date.split(',')[1])
    total = {}
    twitter = []
    flickr = []
    youtube = []
    
    for i in range(1,32):
        day = {}
        day['date'] = str(year)+','+ str(month)+','+str(i)
        day['value'] = 0
        twitter.append(day.copy())
        flickr.append(day.copy())
        youtube.append(day.copy())
    
    
    for element1 in dbt.view('CountData/Count_ByYMDH', group_level=3,stale = "update_after"):
        if element1['key'][0] == year and element1['key'][1] == month:
            date1 = element1['key'][2]
            count1 = element1['value']['sum']
            for dicta1 in twitter:
                if int(dicta1['date'].split(',')[-1]) == date1:
                    dicta1['value'] = count1
    for element2 in dbf.view('CountData/Count_ByYMDH', group_level=3,stale = "update_after"):
        if element2['key'][0] == year and element2['key'][1] == month:
            date2 = element2['key'][2]
            count2 = element2['value']['sum']
            for dicta2 in flickr:
                if int(dicta2['date'].split(',')[-1]) == date2:
                    dicta2['value'] = count2
    for element3 in dby.view('CountData/Count_ByYMDH', group_level=3,stale = "update_after"):
        if element3['key'][0] == year and element3['key'][1] == month:
            date3 = element3['key'][2]
            count3 = element3['value']['sum']
            for dicta3 in youtube:
                if int(dicta3['date'].split(',')[-1]) == date3:
                    dicta3['value'] = count3
    total['twitter'] = twitter
    total['flickr'] = flickr
    total['youtube'] = youtube
    return total

def overview(date):
    year = int(date.split(',')[0])
    month = int(date.split(',')[1])
    total = {}
    twitter = []
    flickr = []
    youtube = []
    
    for i in range(1,32):
        day = {}
        day['date'] = str(year)+','+ str(month)+','+str(i)
        day['value'] = 0
        twitter.append(day.copy())
        flickr.append(day.copy())
        youtube.append(day.copy())
    
    
    for element1 in dbt.view('CountData/Count_ByYMDH', group_level=3,stale = "update_after"):
        if element1['key'][0] == year and element1['key'][1] == month:
            date1 = element1['key'][2]
            count1 = element1['value']['sum']
            for dicta1 in twitter:
                if int(dicta1['date'].split(',')[-1]) == date1:
                    dicta1['value'] = count1
    for element2 in dbf.view('CountData/Count_ByYMDH', group_level=3,stale = "update_after"):
        if element2['key'][0] == year and element2['key'][1] == month:
            date2 = element2['key'][2]
            count2 = element2['value']['sum']
            for dicta2 in flickr:
                if int(dicta2['date'].split(',')[-1]) == date2:
                    dicta2['value'] = count2
    for element3 in dby.view('CountData/Count_ByYMDH', group_level=3,stale = "update_after"):
        if element3['key'][0] == year and element3['key'][1] == month:
            date3 = element3['key'][2]
            count3 = element3['value']['sum']
            for dicta3 in youtube:
                if int(dicta3['date'].split(',')[-1]) == date3:
                    dicta3['value'] = count3
    total['twitter'] = twitter
    total['flickr'] = flickr
    total['youtube'] = youtube
    return total


import gensim
from string import digits
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



def preprocess(text):
    result = []
    for word in text.split(' '):
        result.append(word)
    return result

def topic_date(date):
    LDA_list = {}
    i = 0
    wordlist = []
    date = ast.literal_eval(date)
    date = [int(n) for n in date]
    date1 = date.copy()
    date1[2] = date[2] +1
    for item in dbt.view('CountData/text',start_key = date,end_key = date1,stale = "update_after",include_docs = True):
        if len(tweet_clean(item['doc']['text']).split(' ')) >2:
            LDA_list[i] = tweet_clean(item['doc']['text'])
            i+=1
            
    Solve = pd.DataFrame(LDA_list,index=[0]).T
    Solve['index'] = Solve.index
    sample = Solve[0].map(preprocess)
    dictionary = gensim.corpora.Dictionary(sample)
    bow_corpus = [dictionary.doc2bow(doc) for doc in sample]
    lda_model = gensim.models.LdaMulticore(bow_corpus,num_topics=10,id2word=dictionary,workers=2)
    
    topic_list = []
    for idx, topic in lda_model.print_topics()[0:3]:
        remove_digits = str.maketrans('', '', digits)
        res = topic.translate(remove_digits)
        res = res.replace('.*"','')
        res = res.replace('" +','')
        res = res.replace('"', '')
        topic_list.append(res)
    return topic_list

def topic_location(location):
    LDA_list = {}
    i = 0
    for item in dbt.view('CountData/Cor_ByYMDH',start_key = [2021,1,1], stale = "update_after",include_docs = True):
        if ten_place[place_name.index(location)].contains(Point(item['value'])) and len(tweet_clean(item['doc']['text']).split(' ')) >2:
            LDA_list[i] = tweet_clean(item['doc']['text'])
            i+=1
            
    Solve = pd.DataFrame(LDA_list,index=[0]).T
    Solve['index'] = Solve.index
    sample = Solve[0].map(preprocess)
    dictionary = gensim.corpora.Dictionary(sample)
    bow_corpus = [dictionary.doc2bow(doc) for doc in sample]
    lda_model = gensim.models.LdaMulticore(bow_corpus,num_topics=10,id2word=dictionary,workers=2)
    
    topic_list = []
    for idx, topic in lda_model.print_topics()[0:3]:
        remove_digits = str.maketrans('', '', digits)
        res = topic.translate(remove_digits)
        res = res.replace('.*"','')
        res = res.replace('" +','')
        res = res.replace('"', '')
        topic_list.append(res)
    return topic_list