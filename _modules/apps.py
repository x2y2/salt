# -*- coding: utf-8 -*-
# wangpei
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
    if len(arg) < 2:
        return '2 arguments at least'
    appname = arg[0]
    version = arg[1]
    localpath = arg[2]
    #localpath = '/data/{0}/target'.format(arg[0],arg[1])
    remotepath = '/production/{0}/{1}'.format(appname,version)
    ftp = __ftp()
    for key in range(1,len(remotepath.split('/'))):
        try:
            ftp.cwd(remotepath.split('/')[key])
        except:
            ftp.mkd(remotepath.split('/')[key])
            ftp.cwd(remotepath.split('/')[key])
    
    buffersize = 1024
    file_handler = open(localpath,'rb')
    try:
        ftp.storbinary('STOR ' + appname + '.war',file_handler,buffersize)
    except ftplib.error_perm:
        return 'permission deny'
    files = ftp.nlst(os.path.join('/production',appname,version))
    if files[0].split('/')[-1] == '{0}.war'.format(appname):
        ret = '{0} upload successfully'.format(appname + '.war')
    else:
        ret = '{0} upload failed'.format(appname + '.war')
    file_handler.close()
    ftp.close()
    return ret

def __download(app_path,*args):
    arg = args[:]
    if len(arg) < 2:
        return '2 arguments at least'
    appname = arg[0]
    version = arg[1]
    ftp_path = '/production/{0}/{1}'.format(appname,version)
    ftp = __ftp()
    try:
        ftp.cwd(ftp_path)
    except Exception,e:
        return e
    file_handler = open(appname + '.war','wb')
    #remote_file = os.path.join(app_path,appname,appname + '.war')
    buffersize = 1024
    try:
        ftp.retrbinary('RETR ' + appname + '.war',file_handler.write,buffersize)
    except Exception,e:
        return e
    file_handler.close()
    ftp.close()


def pull_code(*args):
    ret = []
    arg = args[:]
    if len(arg) < 3:
        return '3 arguments at least'
    match = re.search('[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}',arg[0])
    if match:
        url = arg[0]
        appname = arg[1]
        version = arg[2]
        branch = arg[3]
        path = '/data/{0}'.format(appname)
    else:
        url = None
        appname = arg[0]
        version = arg[1]
        branch = arg[2]
        path = '/data/{0}'.format(appname)
    
    if not os.path.exists(path):
        if url:
            os.chdir(path.split('/')[1])
 
            cmd = 'git clone {0}'.format(appname)
            (status,output) = commands.getstatusoutput(cmd)
            ret.append(output)
            try:
                os.chdir(path)
            except:
                return '{0} is not exist'.format(path)
            cmd = 'git checkout {0}'.format(branch)
            (status,output) = commands.getstatusoutput(cmd)
            ret.append(output)

            cmd = 'git pull'
            (status,output) = commands.getstatusoutput(cmd)
            ret.append(output)
        else:
            ret.append('input git address') 
    else:
        os.chdir(path)
        cmd = 'git pull'
        (status,output) = commands.getstatusoutput(cmd)
        ret.append(output)
        cmd = 'git checkout {0}'.format(branch)
        (status,output) = commands.getstatusoutput(cmd)
        ret.append(output)
        cmd = 'git pull'
        (status,output) = commands.getstatusoutput(cmd)
        ret.append(output)

    try: 
        os.chdir(path)
    except:
        ret.append('{0} is not exist'.format(path))
        return ret

    (status,output) = commands.getstatusoutput('git log -1')
    ver = output.split('\n')[0][-4:]

    if version != ver:
        ret.append('{0} is not match {1}'.format(ver,version))
    else:
        ret.append('pull code completed,version is {0}'.format(ver))

    return ret


def make_package(*args):
    ret = []
    arg = args[:]
    if len(arg) < 2:
        return '2 arguments at least'
    appname = arg[0]
    config_file = arg[1]
    path = '/data/{0}'.format(appname)
    #update config file
    autoconfig_path = '/data/autoconfig-release'
    os.chdir(autoconfig_path)
    cmd = 'git pull'
    (status,output) = commands.getstatusoutput(cmd)
    ret.append(output)

    os.chdir(path)
    #config_file = '/data/autoconfig-release/{0}/{0}/product.properties'.format(appname)
    cmd = 'nohup /tools/maven/bin/mvn clean package \
                -Dautoconfig.userProperties={0} \
                -Dmaven.test.skip=true'.format(config_file)
    (status,output) = commands.getstatusoutput(cmd)
    ret.append(output)
    #files = '/data/{0}/web/target/{0}.war'.format(arg[0])
    #if os.path.isfile(files):
    #    ret.append('make package {0} successfully'.format(arg[0] + '.war'))
    #else:
    #    ret.append('make package {0} failed'.format(arg[0] + '.war'))

    return ret



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
    ret = []
    arg = args[:]
    if len(arg) < 2:
        return '2 arguments at least'
    appname = arg[0]
    version = arg[1]
    app_path = '/tools/apps'
    if os.path.exists(os.path.join(app_path,appname)):
        #clean app
        os.chdir(os.path.join(app_path,appname))
        cmd = 'rm -rf {0}/*'.format(os.path.join(app_path,appname))
        (status,output) = commands.getstatusoutput(cmd)
        ret.append(output)
    else:
        os.makedirs(os.path.join(app_path,appname))
        os.chdir(os.path.join(app_path,appname))
    #download .war from ftp
    ftp = __ftp()
    files = ftp.nlst(os.path.join('/production',appname,version))
    ftp.close()
    if not files:
        ftp_file = os.path.join('ftp://xxx/production',appname,version,appname+'.war')
        return '{0} is not exist'.format(ftp_file)

    try:
        __download(app_path,*args)
    except:
        return 'download {0} error'.format(appname)

    #unpackage war
    os.chdir(os.path.join(app_path,appname))
    cmd = 'unzip {0}'.format(appname + '.war')
    try:
        (status,output) = commands.getstatusoutput(cmd)
        ret.append(output)
    except:
        return '{0} is not found'.format(os.path.join(app_path,appname,appname + '.war'))
 
    cmd = os.path.join(app_path,appname,appname + '.war')
    try:
        os.remove(cmd)
        ret.append('remove {0}'.format(cmd))
    except:
        return '{0} is not exist'.format(os.path.join(app_path,appname,appname + '.war'))

    try:
        os.system('chown -R bestpay.bestpay ' + os.path.join(app_path,appname))
        ret.append('deploy {0} successfully'.format(appname))
    except:
        ret.append('deploy {0} failed'.format(appname))

    return ret


def rollback(*args):
    arg = args[:]
    if len(arg) < 2:
        return '2 arguments at least'
    appname = arg[0]
    version = arg[1]
    app_path = '/tools/apps'
    appbak_path = '/data/appbak/{0}/{1}'.format(appname,version)
    #clean app
    os.chdir(app_path)
    os.system('rm -rf {0}'.format(appname))
    if not os.path.exists(appbak_path):
        return '{0} is not found'.format(appbak_path)
    try:
        shutil.copytree(os.path.join(appbak_path,appname),os.path.join(app_path,appname))
        os.system('chown -R bestpay.bestpay {0}'.format(os.path.join(app_path,appname)))
        ret = '{0} rollback successfully'.format(appname)
    except:
        ret = '{0} rollback failed'.format(appname)

    return ret
