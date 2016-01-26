#-*- coding: utf-8 -*-
import commands,urllib
import time,sys
import hashlib

class Token():
    def __init__(self):
        self.now_time = time.strftime('%Y-%m-%d-%H',time.localtime(time.time())) 
    def getToken(self,key):
        md5 = hashlib.md5()
        md5.update(self.now_time+key)
        return md5.hexdigest()
    def authToken(self,one_token,two_token):
        if one_token == two_token:
            return True
        else:
            return False

now_time = time.strftime('%Y-%m-%d-%H',time.localtime(time.time()))
key = 'aaa'
md5 = hashlib.md5()
md5.update(now_time+key)
token = md5.hexdigest()

para_dict={
    "tgt":"*",
    "fun":"cmd.run",
    "args":"uptime",
    "expr_form":"list",
    "token":token
}

api_url = "http://172.17.162.230:8000/api"
post_para = urllib.urlencode(para_dict)
api_info = urllib.urlopen(api_url,post_para).read()
print "Now Token: %s" % token
print api_info
