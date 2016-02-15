#coding: utf-8
import sys
def hello(*args):
    a = args[:]
    return a[0] + ' ' + a[1] +' '+args[2]
