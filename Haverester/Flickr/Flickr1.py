#Central Melbourne


import flickrapi
import xml.etree.ElementTree as ET
import json
import time

api_key='68711bd3d6fb9fe8050c3c6f1c6c4588'
key1='0c266a97a4c31e3e82b2ef0901eb18bb'
api_secret ='f6c6e36410960388'
secret1='1e8fde5ff8d87693'
flickr = flickrapi.FlickrAPI(key1,secret=secret1)


import couchdb
import json
import pandas as pd
from http.client import IncompleteRead as http_incompleteRead
from urllib3.exceptions import IncompleteRead as urllib3_incompleteRead
import os

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
db = get_database(couchServer, 'flickr')


#Take care the view 
i=1
while True:
    try:
        r = flickr.photos_search(has_geo="1", per_page='500', min_taken_date ='2015-06-01 00:00:00',
                         lat='-37.840935',lon='144.946457',radius='10',accuracy="11",extras="geo,date_taken",page = i)
        for element in r:
            for data in element:
                value = True
                dic = {}
                dic['id'] = data.attrib['id']
                dic['year'] = int(data.attrib['datetaken'].split(' ')[0].split('-')[0])
                dic['month'] = int(data.attrib['datetaken'].split(' ')[0].split('-')[1])
                dic['day'] = int(data.attrib['datetaken'].split(' ')[0].split('-')[2])
                dic['hours'] = data.attrib['datetaken'].split(' ')[1].split(':')[0]
                dic['text'] = data.attrib['title']
                dic['coordinates'] = [float(data.attrib['latitude']),float(data.attrib['longitude'])]
                dtm = True
                for element in db.view("CountData/CountID"):
                    if int(dic['id'])== int(element['key']):
                        dtm = False
                        break
                if dtm:
                    db.save(dic)
                    print(dic)
                dtm=True
            if i < 10:
                i+=1
            else:
                time.sleep(60)
                i=1
        time.sleep(60*60)
        
    except Exception as e:
        print(e)
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