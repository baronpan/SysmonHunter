# -*- coding: utf-8 -*-

import yaml

AttckLevel = [
    'ignore', 
    'low', 
    'medium', 
    'high', 
    'critical'
]

AttckPhase = [
    'Initial Access', 
    'Execution', 
    'Persistence', 
    'Privilege Escalation', 
    'Defense Evasion',
    'Credential Access',
    'Discovery',
    'Lateral Movement',
    'Collection',
    'Command and Control',
    'Exfiltration',
    'Impact',
]

class ATTCKTech(object):
    def __init__(self, _id, _raw):
        self.id = _id
        self.name = _raw['name']
        self.description = _raw['description']
        self.level = _raw['level']
        self.phase = _raw['phase']
        self.conditions = _raw['query']

    def __str__(self):
        return '{}: {} ({})'.format(self.id, self.name, self.description)


def load_attcks(yaml_path):
    techs = {}

    with open(yaml_path) as _yaml:
        rules = yaml.load(_yaml)
        for _id, e in rules.iteritems():
            techs[_id] = ATTCKTech(_id, e)
    return techs

def get_attcks_name(ids, techs):
    id_list = ids.split(', ')
    id_names = [techs[_id].name for _id in id_list if _id in techs.keys()]
    return ','.join(id_names)
