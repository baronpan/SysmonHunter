
from core.utils import *

def esapi_epid_behavior_by_range(es, _index, tr, epid):
    ts_tr = format_daterange(tr)
    qstr = 'endpoint.uuid:{} AND timestamp:["{}" TO "{}"]'.format(epid, ts_tr[0], ts_tr[1])
    index = _index
    return es.query(index, 'behavior', qstr)
    
def esapi_behavior_by_range(es, _index, tr):
    ts_tr = format_daterange(tr)
    qstr = 'timestamp:["{}" TO "{}"]'.format(ts_tr[0], ts_tr[1])
    index = _index
    return es.query(index, 'behavior', qstr)

def esapi_mid_behavior(es, _index, epid):
    qstr = 'endpoint.uuid:{}'.format(epid)
    index = _index
    return es.query(index, 'behavior', qstr)

def esapi_propconds_by_range(es, _index, tr, propconds):
    ts_tr = format_daterange(tr)
    cond_list = [' {}: "{}" '.format(k, v) for k, v in propconds.iteritems()]
    qstr = ' AND '.join(cond_list) + ' AND timestamp:["{}" TO "{}"]'.format(ts_tr[0], ts_tr[1])
    return es.query(_index, 'behavior', qstr)