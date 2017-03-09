# _*_ coding: utf-8 _*_
"""
Created on 16/3/14
@author: wangpei
"""
from __future__ import absolute_import
import yaml
import ast
import os
import salt
import salt.utils

__virtualname__ = 'vmconfig'

def __virtual__():
    return __virtualname__


def create(data):
    _data = ast.literal_eval(data)
    _dir = '/etc/salt/cloud.profiles.d'
    try:
        if not os.path.isdir(_dir):
            os.makedirs(_dir)
        _file = os.path.join(_dir, 'vmware.conf')
        with open(_file, 'wb+') as f:
            yaml.safe_dump(_data, f)
            _test_data = yaml.safe_load(f)
            if cmp(_data, _test_data):
                return 'OK'
            else:
                return 'Failed'
    except Exception, e:
        return e


if __name__ == '__main__':
    pass

