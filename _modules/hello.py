#coding: utf-8
import sys
def hello(*args):
    a = args[:]
    return a[1] +' '+args[2]
#if __name__ == '__main__':
#  args = sys.argv[:]
#  hello(*args)
