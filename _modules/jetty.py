# -*- coding: utf-8 -*-
from __future__ import absolute_import
import glob
import os
import logging
import urllib2
import commands
import re
import time

#log = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def __home():
    locations = ['/tools/jetty*','/usr/local/jetty*']
    for location in locations:
        folders = glob.glob(location)
        if folders:
            for jetty_home in folders:
                if os.path.isdir(jetty_home + '/bin'):
                    return jetty_home
    return False

def signal(signal=None):
    jetty_pid = '{0}/run/jetty.pid'.format(__home())
    valid_signal = {
        'start':'start',
        'stop':'stop',
        'restart':'restart',
        'run':'run',
        'status':'status'
    }

    if signal not in valid_signal:
        return
    cmd = '{0}/bin/jetty.sh {1}'.format(__home(),valid_signal[signal])
    out = __salt__['cmd.run_all'](cmd)
    if signal == 'stop':
        if os.path.exists(jetty_pid):
            cmd = 'kill -9 $(ps -ef |grep jetty|awk \'!/grep/{print $2}\')'
            os.system(cmd)
            os.remove(jetty_pid)
            time.sleep(1)
        ret = 'Stopping Jetty: OK'
    if out['stdout']:
        ret = out['stdout'].strip()
    elif out['stderr']:
        ret = out['stderr'].strip()
    else:
        ret = 'Command: "{0}" completed successfully!'.format(cmd)

    return ret

def version():
    vfile = '{0}/VERSION.txt'.format(__home())
    f = open(vfile,'r')
    file = f.readline()
    f.close()
    ret = file.split()[0]
    return ret

def port():  
    confile = '{0}/etc/jetty.xml'.format(__home())
    script = '{0}/bin/jetty.sh'.format(__home())

    f = open(script,'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        match = re.search('JETTY_PORT=[\d]+',line)
        nomatch = re.search('^([\s]*|[\s]+)#',line)
        if match and not nomatch:
            jetty_port = re.findall(r"[\d]+",line)[0]
            return jetty_port

    f = open(confile,'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        match = re.search('jetty.port',line)
        if match:
            jetty_port = re.findall(r"[\d]+",line)[0]
            return jetty_port

    return 'Jetty port is not found'
