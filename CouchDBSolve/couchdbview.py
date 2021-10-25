import os
import couchdb
import json


#Youtube and Flikr to get some view to do data process
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
dbt = get_database(couchServer, 'tweet')
dby = get_database(couchServer, 'youtube')
dbf = get_database(couchServer, 'flickr')



with open(path+'/alldb.json') as f:
    view_1 = json.load(f)
    #dbt.save(view_1)
    #dby.save(view_1)
    dbf.save(view_1)

with open(path+'/Justtweet.json') as f:
    view_2 = json.load(f)
    #dbt.save(view_2)
