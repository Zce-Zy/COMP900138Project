import couchdb
import json
import os
# from datetime import datetime
path = os.getcwd()
#connect to couchDB
def collect_server(user, password):
    try:
        couchServer = couchdb.Server('http://%s:%s@45.113.233.215:5984/' % (user, password))
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


old_tweet_file_1 = path + '/data1.json'
from tqdm import tqdm

with open(old_tweet_file_1) as f:
    data = json.load(f)
    print('start upload tweets')
    for i in range(0, len(data['docs'])):
        index = i
        string = data['docs'][index]
        db.save(string)
        
print('finished upload process. end :)')
