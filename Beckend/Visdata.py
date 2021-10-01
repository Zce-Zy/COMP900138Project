#Get the data to visulization
import json
import pandas as pd
import couchdb
import os
import serve

path = os.getcwd()


try:
    couch = couchdb.Server(serve.getserve()[0])
    db = couch['tweet']
except:
    try:
        couch = couchdb.Server(serve.getserve()[1])
        db = couch['tweet']
    except:
        try:
            couch = couchdb.Server(serve.getserve()[2])
            db = couch['tweet']
        except Exception as e:
            print("Can not access to the database! \n Please Check your internet.")



def flickrdata():
    db = couch['flickr']
    day_total = {'00':0,'01':0, '02':0, '03':0, '04':0, '05':0, '06': 0, '07':0, '08':0,
             '09':0, '10':0, '11':0, '12':0, '13':0, '14':0, '15':0, '16':0,
             '17':0, '18':0, '19':0, '20':0, '21':0, '22':0, '23':0}
    for item in db.view('CountData/Count_ByH', group=True,stale = "update_after"):
        day_total[item['key'][0]]=item['value']
    total = sum(day_total.values())
    for key, value in day_total.items():
        day_total[key] = day_total[key]/total   
    tweet_count = []
    for key, value in day_total.items():
        tweet_count.append(value)
    return(tweet_count)


def varishow():
    with open(path + '/exdata/platdata.json') as f:
        data = json.load(f)
    
    flickr = flickrdata()
    flickr = pd.DataFrame(flickr)
    new_flickr = flickr.rename(columns = {0:'flickr'}).to_dict()
    data['flickr'] = new_flickr['flickr']
    return data

##Vic_total
def summary_vic():
    dic = { 2014: {},2015: {}, 2016: {}, 2017: {}, 2018: {}, 2019: {}, 2020: {}}
    for item in db.view('Sentiment/SentimentScoreStat_BylgaNameTime', group_level=2,stale = "update_after"):
        for i in range(2014,2021):
            if item['key'][1] == i:
                try:
                    dic[i]['sum'] += item['value']['sum']
                except Exception as e:
                    dic[i]['sum'] = item['value']['sum']
                try:
                    dic[i]['count'] += item['value']['count']
                except Exception as e:
                    dic[i]['count'] = item['value']['count']
    for key,value in dic.items():
        dic[key] = value['sum']/value['count']
    return dic

def lga_year():
    yeardata = []
    for item in db.view('Sentiment/SentimentScoreStat_BylgaNameTime', group_level=2,stale = "update_after"):
        lis = [item["key"][0].strip('\\t'), item["key"][1],item["value"]['sum']/item["value"]['count']]
        yeardata.append(lis)
    dic = {}
    for i in range(2015,2021):
        dic[i] = []
        for element in yeardata:
            dic1={}
            if element[1] == i:
                dic1[element[0]] = element[2]
                dic[i].append(dic1)
    return dic
    