# -*- coding: utf-8 -*-

import pandas
import md5
from datetime import datetime

from core.behavior import *
from core.utils import *
from utils.log import *

def machine_id(_str):
    return md5.md5(_str).hexdigest()

def pickup_md5(_str):
    return _str.split('=')[1]

class SysmonData(object):
    def process_create_process(self, eid, mid, props):
        return ProcessBehavior({
                'parent': {
                    'image': props[19],
                    'cmdline': props[20],
                    'guid': props[17],
                },
                'current': {
                    'guid': props[2],
                    'image': props[4],
                    'cmdline': props[9],
                    'user': props[11],
                },
                'file': {
                    'hash': pickup_md5(props[16]),
                    'sig': props[8],
                    'path': props[10],
                },
                'datetime': datetime.strptime(props[1].split('.')[0], '%Y-%m-%d %H:%M:%S').isoformat(),
                'endpoint': {
                    'uuid': mid,
                },
                'relation': 'create',
            })

    def process_timestomp(self, eid, mid, props):
        return FileBehavior({
                'process': {
                    'guid': props[2],
                    'image': props[4],
                },
                'file': {
                    'path': props[5],
                },
                'datetime': datetime.strptime(props[1].split('.')[0], '%Y-%m-%d %H:%M:%S').isoformat(),
                'endpoint': {
                    'uuid': mid,
                },
                'relation': 'timestomp',
            })

    def process_network(self, eid, mid, props):
        return NetworkBehavior({
                'process': {
                    'image': props[4],
                    'user': props[5],
                    'guid': props[2],
                },
                'network': {
                    'protocol': props[6],
                    'clientip': props[9],
                    'clientport': props[11],
                    'rip': props[13],
                    'rhost': props[14],
                    'rport': props[15],
                },
                'file': {
                    'path': props[4],
                },
                'datetime': datetime.strptime(props[1].split('.')[0], '%Y-%m-%d %H:%M:%S').isoformat(),
                'endpoint': {
                    'uuid': mid,
                    'ip': props[9],
                },
                'relation': 'socket',
            })

    def process_driver(self, eid, mid, props):
        return FileBehavior({
                'process': {
                    'image': props[2],
                },
                'file': {
                    'path': props[2],
                    'hash': pickup_md5(props[3]),
                    'sig': props[5],
                    'type': 'driver',
                },
                'datetime': datetime.strptime(props[1].split('.')[0], '%Y-%m-%d %H:%M:%S').isoformat(),
                'endpoint': {
                    'uuid': mid,
                },
                'relation': 'load',
            })

    def process_imageload(self, eid, mid, props):
        return FileBehavior({
                'process': {
                    'image': props[4],
                    'guid': props[2],
                },
                'file': {
                    'path': props[5],
                    'hash': pickup_md5(props[10]),
                    'sig': props[12],
                    'type': 'image',
                },
                'datetime': datetime.strptime(props[1].split('.')[0], '%Y-%m-%d %H:%M:%S').isoformat(),
                'endpoint': {
                    'uuid': mid,
                },
                'relation': 'load',
            })

    def process_remotethread(self, eid, mid, props):
        return ProcessBehavior({
                'parent': {
                    'image': props[4],
                    'guid': props[2],
                },
                'current': {
                    'image': props[7],
                    'guid': props[5],
                    'calltrace': '{}!{}'.format(props[10], props[11])
                },
                'file': {
                    'path': props[7],
                },
                'datetime': datetime.strptime(props[1].split('.')[0], '%Y-%m-%d %H:%M:%S').isoformat(),
                'endpoint': {
                    'uuid': mid,
                },
                'relation': 'inject',
            })

    def process_readfile(self, eid, mid, props):
        return FileBehavior({
                'process': {
                    'image': props[4],
                    'guid': props[2],
                },
                'file': {
                    'path': props[5],
                },
                'datetime': datetime.strptime(props[1].split('.')[0], '%Y-%m-%d %H:%M:%S').isoformat(),
                'endpoint': {
                    'uuid': mid,
                },
                'relation': 'read',
            })

    def process_access_process(self, eid, mid, props):
        return ProcessBehavior({
                'parent': {
                    'image': props[5],
                    'guid': props[2],
                },
                'current': {
                    'image': props[8],
                    'guid': props[6],
                    'calltrace': props[10],
                },
                'file': {
                    'path': props[5],
                },
                'datetime': datetime.strptime(props[1].split('.')[0], '%Y-%m-%d %H:%M:%S').isoformat(),
                'endpoint': {
                    'uuid': mid,
                },
                'relation': 'access',
            })

    def process_create_file(self, eid, mid, props):
        _data = {
            'process': {
                'image': props[4],
                'guid': props[2],
            },
            'file': {
                'path': props[5],
            },
            'datetime': datetime.strptime(props[1].split('.')[0], '%Y-%m-%d %H:%M:%S').isoformat(),
            'endpoint': {
                'uuid': mid,
            },
            'relation': 'create',
        }
        if eid == '15':
            _data['file']['type'] = 'stream'
            _data['file']['hash'] = pickup_md5(props[7])

        return FileBehavior(_data)

    def process_reg(self, eid, mid, props):
        _data = {
            'process': {
                'image': props[5],
                'guid': props[3],
            },
            'reg': {
                'path': props[6],
            },
            'file': {
                'path': props[5],
            },
            'datetime': datetime.strptime(props[2].split('.')[0], '%Y-%m-%d %H:%M:%S').isoformat(),
            'endpoint': {
                'uuid': mid,
            },
        }

        if eid == '12':
            _data['relation'] = 'open'
        elif eid == '13':
            _data['relation'] = 'update'
            _data['reg']['key'] = props[7]
        else:
            _data['relation'] = 'rename'
            _data['reg']['key'] = props[7]

        return RegistryBehavior(_data)

    def process_pipe(self, eid, mid, props):
        _data = {
            'process': {
                'image': props[5],
                'guid': props[2],
            },
            'file': {
                'path': props[4],
                'type': 'pipe',
            },
            'datetime': datetime.strptime(props[1].split('.')[0], '%Y-%m-%d %H:%M:%S').isoformat(),
            'endpoint': {
                'uuid': mid,
            },
        }
        if eid == '17':
            _data['relation'] = 'create'
        else:
            _data['relation'] = 'communicate'

        return FileBehavior(_data)

    def process_wmi(self, eid, mid, props):
        return None


    def from_csv(self, _csv):
        raw_data = pandas.DataFrame.from_csv(_csv)
        behavior_list = []

        for _, e in raw_data.iterrows():
            try:
                eid = str(int(e['EventID']))
                props = e['Strings'].split('|')
                mid = machine_id(e['ComputerName'])
                func = self.eventid_behavior_mappings(eid)
                if func:
                    behavior_list.append(func(eid, mid, props))
            except Exception as e:
                log_error('Error: {} {}-{}'.format(e, eid, repr(props)))
                    
        return behavior_list

    def from_winlogbeat(self, _es, _index, startdate, enddate):
        ts_tr = format_daterange((startdate, enddate))
        qstr = '@timestamp:[{} TO {}]'.format(ts_tr[0], ts_tr[1])
        raw_data = _es.query(_index, 'doc', qstr)
        behavior_list = []

        for _, e in raw_data.iterrows():
            eid = str(e['winlog']['event_id'])
            func = self.eventid_behavior_mappings(eid)

            if func:
                try:
                    props = [en.split(': ')[1] for en in e['message'].split('\n')[1:]]
                    mid = machine_id(e['winlog']['computer_name'])
                    behav = func(eid, mid, props)
                    behavior_list.append(behav)
                except Exception as e:
                    log_error('Error: {} {}-{}'.format(e, eid, repr(props)))
                    
        return behavior_list

    def eventid_behavior_mappings(self, eid):
        mappings = {
            '1': self.process_create_process,
            '2': self.process_timestomp,
            '3': self.process_network,
            '6': self.process_driver,
            '7': self.process_imageload,
            '8': self.process_remotethread,
            '9': self.process_readfile,
            '10': self.process_access_process,
            '11': self.process_create_file,
            '12': self.process_reg,
            '13': self.process_reg,
            '14': self.process_reg,
            '15': self.process_create_file,
            '17': self.process_pipe,
            '18': self.process_pipe,
            '19': self.process_wmi,
            '20': self.process_wmi,
            '21': self.process_wmi,
        }
        if eid in mappings.keys():
            return mappings[eid]
        else:
            return None
