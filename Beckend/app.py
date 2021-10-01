#Flask
#User Ziyang Zhang
#Restful-API
#2020/05/11


from flask import Flask, render_template
from flask_restful import abort, Api, Resource
import Visdata
import plot2
import scater
import place
import cluster
from importlib import reload

app = Flask(__name__)
app.config["DEBUG"] = True
api = Api(app)

# render the index.html
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/api', methods=['GET'], endpoint = "overview")


class dailyview(Resource):
    def get(self, date):
        reload(plot2)
        data = plot2.get_dayview(date)
        return data


class visplatform(Resource):
    def get(self):
        reload(Visdata)
        data = Visdata.varishow()
        return data


##Scater part
class allscater(Resource):
    def get(self):
        reload(scater)
        data = scater.get_allthree()
        return data

class dayscater(Resource):
    def get(self,date):
        reload(scater)
        data = scater.get_daypoint(date)
        return data

class hourscater(Resource):
    def get(self,date):
        reload(scater)
        data = scater.get_hourpoint(date)
        return data

class flickr(Resource):
    def get(self):
        reload(cluster)
        data = cluster.flickrpoints()
        return data

class twitter(Resource):
    def get(self):
        reload(cluster)
        data = cluster.tweetpoints()
        return data

class twittercluster(Resource):
    def get(self):
        reload(cluster)
        data = cluster.twitterluster()
        return data
class twitterclusterh(Resource):
    def get(self,time1):
        reload(cluster)
        data = cluster.twitterluster(int(time1))
        return data

class flickrcluster(Resource):
    def get(self):
        reload(cluster)
        data = cluster.flickrcluster()
        return data
class flickrclusterh(Resource):
    def get(self,time1):
        reload(cluster)
        data = cluster.flickrcluster(int(time1))
        return data

class tenplace(Resource):
    def get(self):
        reload(place)
        data = place.quicktest1()
        return data

class tenplace_hour(Resource):
    def get(self,name):
        reload(place)
        data = place.quicktest2(name)
        return data

class Vic(Resource):
    def get(self):
        reload(Visdata)
        data = Visdata.summary_vic()
        return data

class Lga_senti(Resource):
    def get(self):
        reload(Visdata)
        data = Visdata.lga_year()
        return data


#every day change plot
#date is [2021,7,21]
#data format is testdailyview.json
api.add_resource(dailyview, '/api/dailyview/<date>')

#all platform change sample shows in platdata
#Line graph with diferent platform
#data format is platdata.json
api.add_resource(visplatform, '/api/showvar')



###########scater plot for all data
#all scater show sample shows in allscater
#data format is allscater.json not important 
api.add_resource(allscater, '/api/scater/all')
#show all points by day  date = [2021,7,21]
api.add_resource(dayscater, '/api/scater/day/<date>')
#show all points by hour date = [2021,7,21,1]
api.add_resource(hourscater, '/api/scater/hour/<date>')

###########################################
#4.1.2cluster part
#add twitter sample points
api.add_resource(twitter, '/api/tweetsample')
#add twitter cluster 
api.add_resource(twittercluster, '/api/tweetcluster')
#add twitter cluster by hour
api.add_resource(twitterclusterh, '/api/tweetcluster/<time1>')
#add flickr sample points
api.add_resource(flickr, '/api/flickrsample')
#add twitter cluster 
api.add_resource(flickrcluster, '/api/flickrcluster')
#add twitter cluster by hour
api.add_resource(flickrclusterh, '/api/flickrclusterh/<time1>')


#4.2.1 NLP Process
#10 place whole day sample shows 10place_oneday
api.add_resource(tenplace, '/api/tenplace/all')

#10 place in hour sample shows 10place_hour
api.add_resource(tenplace_hour, '/api/tenplace/hour/<name>')

#Vic sentiment score
api.add_resource(Vic, '/api/Vic')
#Vic sentiment score
api.add_resource(Lga_senti, '/api/Lga_senti')


if __name__ == '__main__':
    app.run(debug=True, port=8080)