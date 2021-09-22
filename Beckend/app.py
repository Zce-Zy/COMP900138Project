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

class allscater(Resource):
    def get(self):
        reload(scater)
        data = scater.get_allthree()
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
api.add_resource(dailyview, '/api/dailyview/<date>')

#all platform change sample shows in platdata
api.add_resource(visplatform, '/api/showvar')

#all scater show sample shows in allscater ##这个不行改一下 几月几日让他是所有的所有年几月几日
api.add_resource(allscater, '/api/scater/all')

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