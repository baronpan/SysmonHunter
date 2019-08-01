import sys

sys.path.append('./')

from data import sysmon
from db import es
from utils.common import *
from core import attck
from core import rule

def test_csv(csvfile, rulefile):
    csvfile = csvfile
    behavs = sysmon.SysmonData().from_csv(csvfile)
    attck_techs = attck.load_attcks(rulefile)
    for behav in behavs:
        if len(rule.match(behav, attck_techs)) > 0:
            print behav

def test_winlogbeat(conffile, rulefile):
    conf = parse_conf(conffile)
    _es = es.ES(conf)

    behavs = sysmon.SysmonData().from_winlogbeat(_es, 'winlogbeat-*', '2019-07-15', '2019-07-16')

    attck_techs = attck.load_attcks(rulefile)

    #matched_ids = ['T1003']
    #matched_attck_techs = {k: v for k, v in attck_techs.iteritems() if k in matched_ids}

    for behav in behavs:
        if len(rule.match(behav, attck_techs)) > 0:
            print behav

if __name__ == '__main__':
    test_csv(sys.argv[1], sys.argv[2])