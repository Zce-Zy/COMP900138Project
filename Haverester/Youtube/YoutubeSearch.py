
import argparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time
import couchdb

#one key only 10 search 
youtubekey1 = 'AIzaSyCqt9_xMtRRhn8Cze_dRYa7V5uVTiovsO4'
youtubekey2 = 'AIzaSyBiSZAigwjoxGObnesHyxNzuud8cJVtS1g'
youtubekey3 = 'AIzaSyAvMuwlvYWGPcGHY9o_NFa1mKIFrQUZfKI'
keys = [youtubekey1,youtubekey2,youtubekey3]




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
db = get_database(couchServer, 'youtube')




def timeGenerate(date):
    year = int(date.split('T')[0].split('-')[0])
    month = int(date.split('T')[0].split('-')[1])
    day = int(date.split('T')[0].split('-')[2])
    hour = date.split('T')[1].split(':')[0]
    return year,month,day,hour
#just multipage
def youtube_search(options):
    youtube = build('youtube','v3',developerKey=youtubekey)
    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
    #q=options.q,
    type='video',
    location=options.location,
    locationRadius=options.location_radius,
    part='id,snippet',
    maxResults=options.max_results
   ).execute()
    
    #Find if have next page
    try:
        nextPageToken = search_response['nextPageToken']
    except KeyError:
        nextPageToken = None
        

    search_videos = []
    youtube_result = []
    ##Merge video ids
    for search_result in search_response.get('items',[]):
        search_videos.append(search_result['id']['videoId'])
    video_ids = ','.join(search_videos)
    
    #retrieve location details for each video
    video_response = youtube.videos().list(
    id=video_ids,
    part='snippet, recordingDetails'
  ).execute()
    
    videos = []
    
      # Add each result to the list, and then display the list of matching videos.
    for video_result in video_response.get('items', []):
        youtube_dic = {}
        youtube_dic['id'] = video_result['id']
        youtube_dic['year'] = timeGenerate(video_result['snippet']['publishedAt'])[0]
        youtube_dic['month'] = timeGenerate(video_result['snippet']['publishedAt'])[1]
        youtube_dic['day'] = timeGenerate(video_result['snippet']['publishedAt'])[2]
        youtube_dic['hours'] = timeGenerate(video_result['snippet']['publishedAt'])[3]
        youtube_dic['text'] = video_result['snippet']['title']
        youtube_dic['coordinates'] = [video_result['recordingDetails']['location']['latitude'],video_result['recordingDetails']['location']['longitude']]
        youtube_result.append(youtube_dic)
    
    i = 0
    while (nextPageToken) and i < 10:
            search_response = youtube.search().list(
                pageToken = nextPageToken,
                #q=options.q,
                type='video',
                location=options.location,
                locationRadius=options.location_radius,
                part='id,snippet',
                maxResults=options.max_results
            ).execute()
            
            search_videos = []
                ##Merge video ids
            for search_result in search_response.get('items',[]):
                search_videos.append(search_result['id']['videoId'])
                video_ids = ','.join(search_videos)
            #retrieve location details for each video
            video_response = youtube.videos().list(
                id=video_ids,
                part='snippet, recordingDetails'
            ).execute()
            for video_result in video_response.get('items', []):
                youtube_dic = {}
                youtube_dic['id'] = video_result['id']
                youtube_dic['year'] = timeGenerate(video_result['snippet']['publishedAt'])[0]
                youtube_dic['month'] = timeGenerate(video_result['snippet']['publishedAt'])[1]
                youtube_dic['day'] = timeGenerate(video_result['snippet']['publishedAt'])[2]
                youtube_dic['hours'] = timeGenerate(video_result['snippet']['publishedAt'])[3]
                youtube_dic['text'] = video_result['snippet']['title']
                youtube_dic['coordinates'] = [video_result['recordingDetails']['location']['latitude'],video_result['recordingDetails']['location']['longitude']]
                youtube_result.append(youtube_dic)
            i += 1
            try:
                nextPageToken = search_response['nextPageToken']
            except KeyError:
                break
    
    return youtube_result

parser = argparse.ArgumentParser()
#parser.add_argument('--q', help='Search term', default='')
parser.add_argument('--location', help='Location', default='-37.840935,144.946457')
parser.add_argument('--location-radius', help='Location radius', default='20km')
parser.add_argument('--max-results', help='Max results', default=500)
args = parser.parse_args(args=[])



while True:
    for key in keys:
        youtubekey = key
        try:
            youtube_result = youtube_search(args)
            for dic in youtube_result:
                dtm = True
                for element in db.view("CountData/CountID"):
                    if dic['id']== element['key']:
                        dtm = False
                        break
                if dtm:
                    db.save(dic)
        except HttpError as e:
            print(e)
            time.sleep(60*60)