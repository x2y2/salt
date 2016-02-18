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
    ftp.close()
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

def mkpack(url=None,*args):
    arg = args[:]
    if len(arg) < 2:
        return '2 arguments at least'
    path = '/data/{0}'.format(arg[0])
    if not os.path.exists(path):
        try:
            git clone url
        except Exception,e:
            return e
    else:
        os.chdir(path)
        git pull
    (status,output) = commands.getstatusoutput('git log -1')
    version = output.split('\n')[0][-4:]
    if arg[1] != version:
        return 'version is not match'
    os.chdir(path)
    autoconfig_path = '/home/jenkins/autoconfig-release/{0}/product.properties'.format(arg[0])
    cmd = 'clean install \
          -Dautoconfig.userProperties={0} \
          -Dmaven.test.skip=true -U'.format(autoconfig_path)
    os.system(cmd)
    if os.path.isfile('/data/{0}/target/{0}.war').format(arg[0]):
        return 'make package {0} successfully'.format(arg[0] + '.war')
    else:
        return 'make package {0} failed'.format(arg[0] + '.war')


def backup(*args):
    arg = args[:]
    if len(arg) < 2:
        return '2 arguments at least'
    app_path = '/tools/apps/{0}'.format(arg[0])
    appbak_path = '/data/appbak/{0}/{1}'.format(arg[0],arg[1])

    if not os.path.exists(app_path):
        return '{0} is not found'.format(arg[0])

    if not os.path.exists(appbak_path):
        os.makedirs(appbak_path)
        os.system('chown -R bestpay.bestpay ' + appbak_path.split('/')[1])

    try:
        shutil.copytree(app_path,os.path.join(appbak_path,arg[0]))
        os.system('chown -R bestpay.bestpay {0}'.format(appbak_path))
        ret = '{0} backup successfully'.format(arg[0])
    except:
        ret = '{0} has already backuped'.format(arg[0])

    return ret

def deploy(*args):
    arg = args[:]
    if len(arg) < 2:
        return '2 arguments at least'
    app_path = '/tools/apps'
    if os.path.exists(os.path.join(app_path,arg[0])):
        #clean app
        os.chdir(os.path.join(app_path,arg[0]))
        os.system('rm -rf {0}/*'.format(os.path.join(app_path,arg[0])))
    else:
        os.makedirs(os.path.join(app_path,arg[0]))
    #download .war from ftp
    ftp = __ftp()
    files = ftp.nlst(os.path.join('/production',arg[0],arg[1]))
    ftp.close()
    if not files:
        return '{0} is not exist'.format(os.path.join('ftp://xxx/production',arg[0],arg[1],arg[0]+'.war'))

    try:
        __download(app_path,*args)
    except:
        return 'download {0} error'.format(arg[0])

    #unpackage war
    os.chdir(os.path.join(app_path,arg[0]))
    try:
        os.system('unzip {0}'.format(arg[0] + '.war'))
    except:
        return '{0} is not found'.format(os.path.join(app_path,arg[0 + '.war']))

    try:
        os.remove(os.path.join(app_path,arg[0],arg[0] + '.war'))
    except:
        return '{0} is not exist'.format(os.path.join(app_path,arg[0],arg[0] + '.war'))

    try:
        os.system('chown -R bestpay.bestpay ' + os.path.join(app_path,arg[0]))
        ret = 'deploy {0} successfully'.format(arg[0])
    except:
        ret = 'deploy {0} failed'.format(arg[0])

    return ret


def rollback(*args):
    arg = args[:]
    if len(arg) < 2:
        return '2 arguments at least'
    app_path = '/tools/apps'
    appbak_path = '/data/appbak/{0}/{1}'.format(arg[0],arg[1])
    #clean app
    os.chdir(app_path)
    os.system('rm -rf {0}'.format(arg[0]))
    if not os.path.exists(appbak_path):
        return '{0} is not found'.format(appbak_path)
    try:
        shutil.copytree(os.path.join(appbak_path,arg[0]),os.path.join(app_path,arg[0]))
        os.system('chown -R bestpay.bestpay {0}'.format(os.path.join(app_path,arg[0])))
        ret = '{0} rollback successfully'.format(arg[0])
    except:
        ret = '{0} rollback failed'.format(arg[0])

    return ret
