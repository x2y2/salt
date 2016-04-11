# -*- coding: utf-8 -*-
# wangpei
from __future__ import absolute_import
import commands
import subprocess
import shlex
import os


def __operation(signal,name):
    if signal == 'query':
        cmd = 'rpm -q {0}'.format(name)
    else:
        cmd = 'yum {0} -y {1}'.format(signal,name)

    (out_put,err_put) = subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT).communicate()
    return out_put
    
def signal(signal,name):
    ret = []
    valid_signals = ('query','install','update','remove','info','list')
    if signal not in valid_signals:
        return
    src_host = '172.17.202.8'
    repo_path = '/etc/yum.repos.d/Bestpay-local.repo'
    if not os.path.exists(repo_path):
        cmd = 'wget http://{0}/{1} -O {2}'.format(src_host,os.path.basename(repo_path),repo_path)
        (out_put,err_put) = subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT).communicate()
        ret.append(out_put)

    ret.append(__operation(signal,name))

    return ret

