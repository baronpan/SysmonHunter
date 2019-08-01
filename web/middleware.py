import pandas

import server
from data.sysmon import SysmonData
from core import rule
from core.behavior import *

from db import esapi
import analyst.statistic as ast
from core.attck import *

def daterange_format(d):
    start = d.split(' - ')[0]
    end = d.split(' - ')[1]
    start_date = '{}-{}-{}'.format(start.split('/')[2], start.split('/')[0], start.split('/')[1])
    end_date = '{}-{}-{}'.format(end.split('/')[2], end.split('/')[0], end.split('/')[1])
    return (start_date, end_date)

def get_event(event_type, behav_type, timerange, callfunc, **kwargs):
    _tr = daterange_format(timerange)

    behavs = []
    if behav_type == 'All':
        for behav_cls in BEHAVIOR_SETS:
            behavs.extend(get_behaviors(event_type + behav_cls.__name__.lower(), _tr, callfunc, **kwargs))
    else:
        behavs = get_behaviors(event_type + behav_type.lower(), _tr, callfunc, **kwargs)
    result = []
    for behav in behavs:
        result.append({
            'epid': behav.endpoint['uuid'],
            'timestamp': behav.date,
            'behavior': behav.getname(),
            'attck': '{}\t{}'.format(behav.attck_ids, get_attcks_name(behav.attck_ids, server.ATTCK_TECHS)),
            'value': behav.get_value(),
        })
    return result

def get_behaviors(_index, timerange, callfunc, **kwargs):
    _es = server.ES_INSTANCE
    data = callfunc(_es, _index, timerange, **kwargs)
    data.drop_duplicates(subset=['timestamp', 'value'])
    behavs = []
    for _, en in data.iterrows():
        behavs.append(BaseBehavior.deserialize(en))
        
    return behavs
        
def get_statistic_data(event_type, behav_type, timerange, st_func, **kwargs):
    _es = server.ES_INSTANCE
    data = esapi.esapi_behavior_by_range(_es, event_type + behav_type.lower(), daterange_format(timerange))

    if data.shape[0] == 0:
        return []

    stdata = st_func(data, **kwargs)
    return ast.st_output(stdata)

def get_st_details_data(event_type, behav_type, timerange, conds):
    _es = server.ES_INSTANCE
    data = esapi.esapi_propconds_by_range(_es, event_type + behav_type.lower(), daterange_format(timerange), conds)

    if data.shape[0] == 0:
        return []

    result = []
    for k, en in data.iterrows():
        result.append({
            'epid': en['endpoint.uuid'],
            'timestamp': en['timestamp'],
            'behavior': en['behaviortype'],
            'attck': '{}\t{}'.format(en['attckids'], get_attcks_name(en['attckids'], server.ATTCK_TECHS)),
            'value': en['value'],
        })
        
    return result