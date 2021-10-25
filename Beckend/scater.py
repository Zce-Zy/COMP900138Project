import couchdb
import serve
import ast

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

#Get all scater plot in to a dictionary
def get_allthree():
    data_t = []
    data_y = []
    data_f = []
    data_all = []
    ##get tweet points
    for item in dbt.view('CountData/Cor_ByYMDH',stale = "update_after",start_key = [2017,1]):
        data_t.append([float(item['value'][0]),float(item['value'][1])])
    ##get flickr points
    for item in dbf.view('CountData/Cor_ByYMDH',stale = "update_after"):
        data_f.append([float(item['value'][0]),float(item['value'][1])])
    ##get youtube points
    for item in dby.view('CountData/Cor_ByYMDH',stale = "update_after"):
        data_y.append([float(item['value'][0]),float(item['value'][1])])
    data_all = data_t + data_y + data_f
    dic = {}
    dic['total'] = data_all
    dic['twitter'] = data_t
    dic['youtube'] = data_y
    dic['flickr'] = data_f
    return dic


#get all_points in a single day 
#shows the text,coordinates and sentimentscore
#datetype = [2021,9,20]
def get_daypoint(date):
    ##reduce search time
    date = ast.literal_eval(date)
    date = [int(n) for n in date]
    dateend = date.copy()
    dateend[2] += 1
    tweet = []
    flickr = []
    youtube = []
    for item in dbt.view('CountData/Cor_ByYMDH', stale = "update_after",include_docs=True,start_key = date, end_key = dateend):
        point = []
        point.append(item['doc']['text'])
        point.append(item['value'])
        point.append(item['doc']['sentiment_score'])
        tweet.append(point)
    for item in dbf.view('CountData/Cor_ByYMDH', stale = "update_after",include_docs=True,start_key = date, end_key = dateend):
        point = []
        point.append(item['doc']['text'])
        point.append(item['value'])
        point.append(0)
        flickr.append(point)
    for item in dby.view('CountData/Cor_ByYMDH', stale = "update_after",include_docs=True,start_key = date, end_key = dateend):
        point = []
        point.append(item['doc']['text'])
        point.append(item['value'])
        point.append(0)
        youtube.append(point)
    alldata = {}
    alldata['twitter'] = tweet
    alldata['flickr'] = flickr
    alldata['youtube'] = youtube
    return alldata

#get all_points in a hour
#shows the text,coordinates and sentimentscore
#datetype = [2021,9,20,h]
#Time change
def get_hourpoint(date):
    ##reduce search time
    date = ast.literal_eval(date)
    date = [int(n) for n in date]
    tweet = []
    flickr = []
    youtube = []
    date[-1] = date[-1]-14
    if date[-1] < 0:
        date[-1] += date[-1] + 24
    dateend = date.copy()
    dateend[-1] += 1
    date[-1] = str(date[-1])
    dateend[-1] = str(dateend[-1])
    print(date)
    print(dateend)
    for item in dbt.view('CountData/Cor_ByYMDH', stale = "update_after",include_docs=True,start_key = date, end_key = dateend):
        if int(item['key'][-1]) == int(date[-1]):
            point = []
            point.append(item['doc']['text'])
            point.append(item['value'])
            point.append(item['doc']['sentiment_score'])
            tweet.append(point)
    for item in dbf.view('CountData/Cor_ByYMDH', stale = "update_after",include_docs=True,start_key = date, end_key = dateend):
        if int(item['key'][-1]) == int(date[-1]):
            point = []
            point.append(item['doc']['text'])
            point.append([float(item['value'][0]),float(item['value'][1])])
            point.append(0)
            flickr.append(point)
    for item in dby.view('CountData/Cor_ByYMDH', stale = "update_after",include_docs=True,start_key = date, end_key = dateend):
        if int(item['key'][-1]) == int(date[-1]):
            point = []
            point.append(item['doc']['text'])
            point.append(item['value'])
            point.append(0)
            youtube.append(point)
    alldata = {}
    alldata['twitter'] = tweet
    alldata['flickr'] = flickr
    alldata['youtube'] = youtube
    return alldata