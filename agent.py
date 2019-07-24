# -*- coding: utf-8 -*-
import argparse

from utils.common import *
from data import sysmon
from db import es, graph
from core import attck
from core import rule

def process_csv(conf, csv_file):
    behavs = sysmon.SysmonData().from_csv(csv_file)
    _es = es.ES(conf)
    _es.insert_behaviors('raw', behavs)
    attck_techs = attck.load_attcks(conf['attck_yaml'])

    abnormals = rule.filter_abnormal_behaviors(behavs, attck_techs)
    _es.insert_behaviors('abnormal', abnormals)
    _neo4j = graph.Neo4jGraph(conf)
    _neo4j.update_behaviors(abnormals)

def process_winlogbeat(conf, start, end):
    _es = es.ES(conf)
    behavs = sysmon.SysmonData().from_winlogbeat(_es, 'winlogbeat-*', start, end)
    _es.insert_behaviors('raw', behavs)
    attck_techs = attck.load_attcks(conf['attck_yaml'])

    abnormals = rule.filter_abnormal_behaviors(behavs, attck_techs)
    _es.insert_behaviors('abnormal', abnormals)
    _neo4j = graph.Neo4jGraph(conf)
    _neo4j.update_behaviors(abnormals)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', help='conf file')
    parser.add_argument('-t', help='choose csv or winlogbeat')
    parser.add_argument('-i', help='csv file')
    parser.add_argument('-start', help='start date from winlogbeat, like 2019-07-19')
    parser.add_argument('-end', help='end date from winlogbeat, like 2019-07-19')
    args = parser.parse_args()


    if args.t not in ['csv', 'winlogbeat']:
        import sys
        parser.print_usage()
        sys.exit(1)

    conf = parse_conf(args.c)
    if args.t == 'csv':
        process_csv(conf, args.i)
    else:
        process_winlogbeat(conf, args.start, args.end)
    