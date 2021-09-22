import couchdb
import json


##link to our couchdb
try:
    couch = couchdb.Server('http://user:pass@127.0.0.1:5984')
    dbt = couch['tweet']
    dby = couch['youtube']
    dbf = couch['flickr']
except:
    try:
        couch = couchdb.Server('http://user:pass@172.26.131.22:5984')
        dbt = couch['tweet']
        dby = couch['youtube']
        dbf = couch['flickr']
    except:
        try:
            couch = couchdb.Server('http://user:pass@172.26.133.132:5984')
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

#Get data by hour