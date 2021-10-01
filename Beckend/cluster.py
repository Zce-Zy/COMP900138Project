from datetime import time
from numpy.lib.type_check import mintypecode
import pandas as pd
import couchdb
from scipy.sparse import data
from sklearn.cluster import DBSCAN
import os
import serve

##link to our couchdb
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
    except:
        try:
            couch = couchdb.Server(serve.getserve()[2])
            dbt = couch['tweet']
            dby = couch['youtube']
            dbf = couch['flickr']
        except Exception as e:
            print("Can not access to the database! \n Please Check your internet.")

#use local data to try
path = os.getcwd()

#Clustering Part 10,000 sample
tweet = pd.read_json(path + '/exdata/after_data.json')
#filckr with 10000 samples
flickr = pd.read_json(path + '/exdata/flickrcluster.json')

def flickrpoints():
    return flickr.T.to_json()

def tweetpoints():
    return tweet.T.to_json()

def flickrcluster(time1 = 0, time2 = 24):
    data = flickr.copy()
    data = data[(data['time'] <= time2) & (data['time'] >= time1)][['Latitude','Longitude']]
    X = data[['Latitude','Longitude']]
    minp = 30
    if time1 != 0:
            time2 = time1 + 1
    if time1 == 0 and time2 == 24:
        minp = 100
    points = DBSCAN(eps=0.01, min_samples=minp).fit(X)
    label = points.labels_
    data['cluster'] = label
    data1 = data.groupby('cluster').mean().reset_index(drop=False)
    return data1.T.to_json()

def twitterluster(time1 = 0, time2 = 24):
    data = flickr.copy()
    data = data[(data['time'] <= time2) & (data['time'] >= time1)][['Latitude','Longitude']]
    X = data[['Latitude','Longitude']]
    minp = 30
    if time1 != 0:
        time2 = time1 + 1
    if time1 == 0 and time2 == 24:
        minp = 100
    points = DBSCAN(eps=0.01, min_samples=minp).fit(X)
    label = points.labels_
    data['cluster'] = label
    data1 = data.groupby('cluster').mean().reset_index(drop=False)
    return data1.T.to_json()

