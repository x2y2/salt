# _*_ coding: utf-8 _*_
from __future__ import absolute_import
import yaml
import ast
import os


def create(appname,sch_id,minion_id='all'):
    ret = []
    data = {'schedule':{sch_id: {'function': 'cmd.run', 'seconds': 5, 'args': ['date >>/tmp/log8']}}}
    #_data = ast.literal_eval(data)
    _dir = '/srv/pillar/schedules'
    try:
        if not os.path.isdir(_dir):
            os.makedirs(_dir)
        _file = os.path.join(_dir, '{0}-{1}-{2}.sls'.format(minion_id,appname,sch_id))
        
        top_file = '/srv/pillar/top.sls'
        with open(top_file,'r') as f:
            top_data = yaml.load(f)
        f.close()

        if minion_id == 'all':
            if not top_data['base']['*']:
                top_data['base']['*'] = ['schedules.{0}-{1}-{2}'.format(minion_id,appname,sch_id)]
            else:
                top_data['base']['*'].append('schedules.{0}-{1}-{2}'.format(minion_id,appname,sch_id))
        else:
            if minion_id not in top_data.values()[0].keys():
                top_data['base'][minion_id] = ['schedules.{0}-{1}-{2}'.format(minion_id,appname,sch_id)]
            else:
                top_data['base'][minion_id].append('schedules.{0}-{1}-{2}'.format(minion_id,appname,sch_id))
        
        with open(top_file,'w') as f:
            yaml.safe_dump(top_data,f,default_flow_style=False)
        f.close()

        with open(_file, 'w') as f:
            yaml.safe_dump(data,f,default_flow_style=False)
        f.close()

        with open(_file,'r') as f:
            _test_data = yaml.safe_load(f) 
        f.close()

        if cmp(data, _test_data):
            ret.append('failed')
        else:
            ret.append('ok')
    except Exception, e:
        ret.append(e)
    
    return ret
    

if __name__ == '__main__':
    pass

