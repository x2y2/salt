# -*- coding: utf-8 -*-
from __future__ import absolute_import
import glob
import os
import logging
import urllib2
import commands
import re

def status(url='http://localhost:8080/index.jsp'):
    data = {
        'msg': []
    }

    try:
        data['msg'] = urllib2.urlopen(url).read().splitlines()
        if data['msg'][0].startswith('ok'):
            ret = 'App is health'
        else:
            ret = 'App is not health'
    except:
        ret = 'Connection Refused'
    return ret