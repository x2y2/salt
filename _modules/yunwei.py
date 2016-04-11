# _*_ coding: utf-8 _*_
"""
Created on 16/3/11
@author: liusonghui
"""
from __future__ import absolute_import
import threading
import socket
import salt
import salt.utils
import os
import time
import logging
import subprocess
import urllib2

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

try:
    import pwd
except ImportError:
    pass

__virtualname__ = 'yunwei'

SERVICE = 1
APP = 2


def __virtual__():
    return __virtualname__


class __myThread(threading.Thread):
    def __init__(self, host, port, ret):
        threading.Thread.__init__(self)
        self._host = host
        self._port = port
        self._ret = ret

    def run(self):
        mutex = threading.Lock()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        try:
            s.connect((self._host, self._port))
            mutex.acquire()
            self._ret.append('{0}: Success'.format(self._port))
        except Exception:
            mutex.acquire()
            self._ret.append('{0}: Failed'.format(self._port))
        finally:
            s.close()
            mutex.release()


def port_health(ports, host='127.0.0.1'):
    ret = []
    threads = []
    string = ''
    try:
        for port in ports.split(','):
            threads.append(__myThread(host, int(port), ret))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    except Exception, e:
        ret.append('{0}'.format(e))
    for a in ret:
        string += a + '\n'
    return string


def app_health(host='127.0.0.1:8030'):
    url = 'http://{0}/healthcheck/status.html'.format(host)
    try:
        data = urllib2.urlopen(url).read().splitlines()
        if 'success' in data[0] or 'ok' in data[0]:
            ret = 'App is health'
        else:
            ret = 'App is not health'
    except:
        ret = 'Connection Refused'
    return ret


def __service_check(server_name):
    servers = {"jetty": "/tools/jetty/bin/jetty.sh"}
    service_dir = '/tools/apps'
    if servers.get(server_name):
        return (SERVICE, servers.get(server_name))
    elif os.path.isfile(os.path.join(service_dir, server_name)):
        return (APP, os.path.join(service_dir, server_name))


def __getpid(process_name):
    try:
        p = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
        s = subprocess.Popen(['grep', '-i', process_name], stdin=p.stdout, stdout=subprocess.PIPE)
        pid = subprocess.Popen(['awk', '!/(grep|salt)/{print $2}'], stdin=s.stdout, stdout=subprocess.PIPE)
        return pid.communicate()[0]
    except Exception, e:
        return


def start(service_names, args=None):
    output = ''
    for service_name in service_names.split(','):
        if __service_check(service_name):
            (_form, service_path) = __service_check(service_name)
        else:
            output += '{0} Error: not found\n'.format(service_name)
            continue
        if not os.path.isfile(service_path):
            output += '{0} Error\n'.format(service_name)
            continue
        if _form == SERVICE:
            cmdline = '{0} start'.format(service_path)
        elif _form == APP:
            cmdline = 'java -jar {0} {1}'.format(service_name, args)
        else:
            cmdline = 'echo {0} failed.'.format(service_name)
        try:
            output += __salt__['cmd.run'](cmdline)
            output += '\n'
            time.sleep(1)
        except Exception, e:
            output += '{0} Error: {1}\n'.format(service_name, e)
    return output


def stop(service_names):
    output = ''
    for service_name in service_names.split(','):
        if __service_check(service_name):
            (_form, service_path) = __service_check(service_name)
        else:
            output += '{0} Error: not found\n'.format(service_name)
            continue
        if not os.path.isfile(service_path):
            output += '{0} Error\n'.format(service_name)
            continue

        pid = int(__getpid(service_name))
        if _form == SERVICE:
            cmdline = '{0} stop'.format(service_path)
        elif _form == APP:
            cmdline = 'kill -9 {0}'.format(pid)
        else:
            cmdline = 'echo {0} Failed'.format(service_name)
        try:
            output += str(__salt__['cmd.run'](cmdline))
            output += '\n'
            time.sleep(1)
            if os.system('ps -ef | grep {0} | grep -v grep'.format(pid)):
                output += '{0} Stop Failed\n'.format(service_name)
            else:
                output += '{0} Stop Success\n'.format(service_name)
        except Exception, e:
            output += '{0} Error: {1}\n'.format(service_name, e)
    return output


def status(service_names):
    output = ''
    for service_name in service_names.split(','):
        if __service_check(service_name):
            (_form, service_path) = __service_check(service_name)
        else:
            output += '{0} Error: not found\n'.format(service_name)
            continue
        if not os.path.isfile(service_path):
            output += '{0} Error\n'.format(service_name)
            continue
        pid = __getpid(service_name)
        if pid:
            output += '{0} is running, pid:\n{1}'.format(service_name, pid)
        else:
            output += '{0} is not running.\n'.format(service_name)
    return output


if __name__ == '__main__':
    pass

