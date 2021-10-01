from sklearn import tree
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from shapely.geometry import shape, Point, Polygon
from collections import Counter
import re, json
import serve
import couchdb
import pandas as pd
import os

try:
    couch = couchdb.Server('http://user:pass@127.0.0.1:5984')
    dbt = couch['tweet']
    dby = couch['youtube']
    dbf = couch['flickr']
except:
    try:
        couch = couchdb.Server(serve.getserve()[1])
        dbt = couch['tweet']
        dby = couch['youtube']
        dbf = couch['flickr']
    except:
        try:
            couch = couchdb.Server(serve.getserve()[2])
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
