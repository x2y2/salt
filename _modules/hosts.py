# -*- coding: utf-8 -*-
import re
import commands

def ipconfig():
    cmd = '/sbin/ifconfig eth0|grep "inet addr:"'
    str = commands.getoutput(cmd)
    ip = re.split('[ :]+',str)[3:4]
    return ip
