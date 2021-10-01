#Get every day every hour count percentage
#type:data = [2021,1,1]
import couchdb
import serve
import os


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

#Average post number per hour
def get_day_average():
    totalday=0
    for item in db.view('CountData/Count_ByYMDH',group_level=3,stale = "update_after"):
        totalday+=1
    day_average = {'00':0,'01':0, '02':0, '03':0, '04':0, '05':0, '06': 0, '07':0, '08':0,
             '09':0, '10':0, '11':0, '12':0, '13':0, '14':0, '15':0, '16':0,
             '17':0, '18':0, '19':0, '20':0, '21':0, '22':0, '23':0}
    for item in db.view('CountData/Count_ByH', group=True,stale = "update_after"):
        day_average[item['key'][0]] = int(item['value']/totalday+1)
    total = sum(day_average.values())
    for key, value in day_average.items():
        day_average[key] = day_average[key]/total
    return day_average

#Max post number per hour
def get_day_max():
    day_max = {'00':0,'01':0, '02':0, '03':0, '04':0, '05':0, '06': 0, '07':0, '08':0,
             '09':0, '10':0, '11':0, '12':0, '13':0, '14':0, '15':0, '16':0,
             '17':0, '18':0, '19':0, '20':0, '21':0, '22':0, '23':0, '23':0}
    for item in db.view('CountData/Count_ByYMDH', group=True,stale = "update_after"):
        if item['value']['sum']>day_max[item['key'][-1]]:
            day_max[item['key'][-1]] = item['value']['sum']
    total = sum(day_max.values())
    for key, value in day_max.items():
        day_max[key] = day_max[key]/total
    return day_max


#Return every day need data [datalist]
def get_dayview(date):
    date = date
    day_total = {'00':0,'01':0, '02':0, '03':0, '04':0, '05':0, '06': 0, '07':0, '08':0,
             '09':0, '10':0, '11':0, '12':0, '13':0, '14':0, '15':0, '16':0,
             '17':0, '18':0, '19':0, '20':0, '21':0, '22':0, '23':0}
    for item in db.view('CountData/Count_ByYMDH', group=True,stale = "update_after"):
        if item['key'][:-1]==date:
            day_total[item['key'][-1]]=item['value']['sum']
    total = sum(day_total.values()) + 1 ##in case of devison
    for key, value in day_total.items():
        day_total[key] = day_total[key]/total
    day_average=get_day_average()
    day_max=get_day_max()
    dataList=[]
    time=['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16',
          '17','18','19','20','21','22','23']
    for item in time:
        dic={}
        dic['total']=day_total[item]
        dic['max']=day_max[item]
        dic['avg']=day_average[item]
        dataList.append(dic)
    for i in range(10):
        dataList.insert(0,dataList.pop())
    return {'dataList': dataList}