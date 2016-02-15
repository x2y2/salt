# -*- coding: utf-8 -*-
from __future__ import absolute_import
import glob
import os
import logging
import urllib
import urllib2
import commands
import re
import time
import shutil
import json
import ftplib
import sys
from pwd import getpwnam

def __ftp():
    ftp_host = '172.17.192.32'
    ftp_port = 21
    ftp_user = 'night'
    ftp_password = 'asd!23'
    ftp = ftplib.FTP()
    ftp.connect(ftp_host,ftp_port)
    ftp.login(ftp_user,ftp_password)
    return ftp

def version():
    url = 'http://localhost:8080/version.html'
    header = {'Accept':'application/json'} 
    data = None
    req = urllib2.Request(url,data,header)
    response = urllib2.urlopen(req)
    page = response.read()
    jdata = json.loads(page)
    return jdata

def status(url='http://localhost:8080/checkpreload.html'):
    try:
        data = urllib2.urlopen(url).read().splitlines()
        if 'ok' in data[0]:
            ret = 'App is health'
        else:
            ret = 'App is not health'
    except:
        ret = 'Connection Refused'
    return ret


def upload(*args):
    arg = args[:]
    localpath = '/data/{0}/target'.format(arg[0],arg[1])
    remotepath = '/production/{0}/{1}'.format(arg[0],arg[1])
    ftp = __ftp()
    for key in range(1,len(remotepath.split('/'))):
        try:
            ftp.cwd(remotepath.split('/')[key])
        except:
            ftp.mkd(remotepath.split('/')[key])
            ftp.cwd(remotepath.split('/')[key])
    
    buffersize = 1024
    file_handler = open(os.path.join(localpath,arg[0] + '.war'),'rb')
    try:
        ftp.storbinary('STOR ' + arg[0] + '.war',file_handler,buffersize)
    except ftplib.error_perm:
        ret = 'permission deny'
    ret = '{0} upload successfully'.format(arg[0] + '.war')
    file_handler.close()
    ftp.quit()
    return ret

def __download(app_path,*args):
    arg = args[:]
    ftp_path = '/production/{0}/{1}'.format(arg[0],arg[1])
    ftp = __ftp()
    try:
        ftp.cwd(ftp_path)
    except Exception,e:
        return e
    file_handler = open(arg[0] + '.war','wb')
    os.chdir(os.path.join(app_path,arg[0]))
    buffersize = 1024
    try:
        ftp.retrbinary('RETR ' + arg[0] + '.war',file_handler.write,buffersize)
    except Exception,e:
        return e
    file_handler.close()
    ftp.close()

def backup(appname):
    curtime = time.strftime('%Y%m%d%H%M',time.localtime())
    appbak_path = '/data/appbak/{0}'.format(curtime)
    app_path = '/tools/apps/{0}'.format(appname)
    uid = getpwnam('bestpay')[2]
    gid = getpwnam('bestpay')[3]

    if not os.path.exists(app_path):
        return 'appname is not found'
    if not os.path.exists(appbak_path):
        os.makedirs(appbak_path)
        os.system('chown -R bestpay.bestpay ' + appbak_path.split('/')[1])
    try:
        shutil.copytree(app_path,os.path.join(appbak_path,appname))
        os.chown(os.path.join(appbak_path,appname),uid,gid)
        ret = '{0} backup successfully'.format(appname)
    except:
        ret = '{0} backup failed'.format(appname)

    return ret

def deploy(*args):
    arg = args[:]
    if len(arg) < 2:
        return '2 arguments at least'
    app_path = '/tools/apps'
    if not os.path.exists(os.path.join(app_path,arg[0])):
        os.makedirs(os.path.join(app_path,arg[0]))
    #clean app
    os.chdir(os.path.join(app_path,arg[0]))
    os.system('rm -rf {0}/*'.format(os.path.join(app_path,arg[0])))
    #return 'aa'
    #download .war from ftp
    try:
        __download(app_path,*args)
    except:
        return 'download {0} error'.format(arg[0])
    os.chdir(os.path.join(app_path,arg[0]))
    os.system('unzip {0}'.format(arg[0] + '.war'))
    os.system('rm -f {0}'.format(os.path.join(app_path,arg[0],arg[0] + '.war')))
    try:
        os.system('chown -R bestpay.bestpay ' + os.path.join(app_path,arg[0]))
        ret = 'deploy {0} successfully'.format(arg[0])
    except:
        ret = 'deploy {0} failed'.format(arg[0])

    return ret
