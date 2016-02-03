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
from pwd import getpwnam

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


def upload(appname,version):
    localpath = '/data/{0}/target'.format(appname)
    remotepath = '/production/{0}/{1}'.format(appname,version)
    ftp_host = '172.17.192.32'
    ftp_port = 21
    ftp_user = 'night'
    ftp_password = 'xxx'
    buffersize = 1024
    ftp = ftplib.FTP()
    ftp.connect(ftp_host,ftp_port)
    ftp.login(ftp_user,ftp_password)
    for key in range(1,len(remotepath.split('/'))):
        try:
            ftp.cwd(remotepath.split('/')[key])
        except:
            ftp.mkd(remotepath.split('/')[key])
            ftp.cwd(remotepath.split('/')[key])

    file_handler = open(os.path.join(localpath,appname + '.war'),'rb')
    try:
        ftp.storbinary('STOR ' + appname + '.war',file_handler,buffersize)
    except ftplib.error_perm:
        ret = 'permission deny'
    ret = '{0} upload successfully'.format(appname + '.war')
    file_handler.close()
    ftp.quit()
    return ret


def back(appname):
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

def deploy(appname,version):
    app_path = '/tools/apps'
    if not appname or not version:
        return '2 argument at least'
    if not os.path.exists(os.path.join(app_path,appname)):
        os.makedirs(os.path.join(app_path,appname))
    #clean app
    os.chdir(os.path.join(app_path,appname))
    os.system('rm -rf {0}/*'.format(os.path.join(app_path,appname)))
    #download .war from ftp
    ftp_path = os.path.join('production',appname,str(version))
    ftp_host = '172.17.192.32'
    ftp_port = 21
    ftp_user = 'night'
    ftp_password = 'xxx'
    buffersize = 1024
    ftp = ftplib.FTP()
    ftp.connect(ftp_host,ftp_port)
    ftp.login(ftp_user,ftp_password)
    try:
        ftp.cwd(ftp_path)
    except Exception,e:
        return e
    file_handler = open(appname + '.war','wb')
    os.chdir(os.path.join(app_path,appname))
    try:
        ftp.retrbinary('RETR ' + appname + '.war',file_handler.write,buffersize)
    except Exception,e:
        return e
    file_handler.close()
    ftp.close()
    #unpackage war
    os.chdir(os.path.join(app_path,appname))
    try:
        os.system('jar -xf ' + appname + '.war')
        os.remove(os.path.join(app_path,appname,appname + '.war'))
    except:
        return 'unpackage war failed'
    os.system('chown -R bestpay.bestpay ' + os.path.join(app_path,appname))
    #file = open(os.path.join(app_path,appname,version.html),'r')
    #ver = file.readline()
    #file.close()
    #if ver == version:
    return 'deploy successfully'
    #else:
    #    return 'deploy failed'

