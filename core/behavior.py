# -*- coding: utf-8 -*-

from core.entity import *


class BaseBehavior(object):
    CONTEXT = []
    def __init__(self, _raw):
        self.attck_ids = ''
        self.date = None
        self.relation = ''

    def getname(self):
        return self.__class__.__name__

    def get_value(self):
        pass

    def get_attribute_names(self):
        attrs = ['timestamp', 'relation', 'attckids', 'behaviortype', 'value']
        for _attr in self.__class__.CONTEXT:
            attrs.extend([_attr + '.' + prop for prop in self.__dict__[_attr].__class__.PROPS])
        return attrs

    def serialize(self):
        serobj = {'timestamp': self.date, 'relation': self.relation, 'attckids': self.attck_ids, 'behaviortype': self.getname(), 'value': self.get_value()}
        for _attr in self.__class__.CONTEXT:
            _obj = self.__dict__[_attr]
            serobj.update({_attr + '.' + prop: _obj[prop] for prop in _obj.__class__.PROPS})

        return serobj

    @staticmethod
    def deserialize(_raw):
        mappings = {
            'ProcessBehavior': ProcessBehavior,
            'NetworkBehavior': NetworkBehavior,
            'FileBehavior': FileBehavior,
            'RegistryBehavior': RegistryBehavior,
        }
        
        behav_data = {}
        behav_data['datetime'] = _raw['timestamp']
        behav_data['relation'] = _raw['relation']
        cols = list(_raw.keys())
        for col in cols:
            if '.' in col:
                if col.split('.')[0] not in behav_data.keys():
                    behav_data[col.split('.')[0]] = {}
                behav_data[col.split('.')[0]][col.split('.')[1]] = _raw[col]

        _instance = mappings[_raw['behaviortype']](behav_data)
        _instance.attck_ids = _raw['attckids']
        return _instance


class ProcessBehavior(BaseBehavior):
    CONTEXT = ['parent', 'current', 'file', 'endpoint']
    def __init__(self, _raw):
        super(ProcessBehavior, self).__init__(_raw)

        self.parent = ProcessEntity(_raw['parent'])
        self.current = ProcessEntity(_raw['current'])
        self.file = FileEntity(_raw['file'])
        self.date = _raw['datetime']
        self.endpoint = EndPointEntity(_raw['endpoint'])
        self.relation = _raw['relation']

    def __str__(self):
        return '{} Endpoint({}) on {}: ({} {}) -{}-> ({} {})'.format(self.__class__.__name__, self.endpoint['uuid'], self.date, self.parent['image'], self.parent['cmdline'], self.relation, self.current['image'], self.current['cmdline'])

    def get_value(self):
        return '({} {}) -{}-> ({} {})'.format(self.parent['image'], self.parent['cmdline'], self.relation, self.current['image'], self.current['cmdline'])


class NetworkBehavior(BaseBehavior):
    CONTEXT = ['process', 'network', 'file', 'endpoint']
    def __init__(self, _raw):
        super(NetworkBehavior, self).__init__(_raw)

        self.process = ProcessEntity(_raw['process'])
        self.network = NetworkEntity(_raw['network'])
        self.file = FileEntity(_raw['file'])
        self.date = _raw['datetime']
        self.endpoint = EndPointEntity(_raw['endpoint'])
        self.relation = _raw['relation']

    def __str__(self):
        return '{} Endpoint({}) on {}: {} -{}-> {}({})'.format(self.__class__.__name__, self.endpoint['uuid'], self.date, self.process['image'], self.relation, self.network['rhost'], self.network['rip'])

    def get_value(self):
        return '{} -{}-> {}({})'.format(self.process['image'], self.relation, self.network['rhost'], self.network['rip'])

class FileBehavior(BaseBehavior):
    CONTEXT = ['process', 'file', 'endpoint']
    def __init__(self, _raw):
        super(FileBehavior, self).__init__(_raw)

        self.process = ProcessEntity(_raw['process'])
        self.file = FileEntity(_raw['file'])
        self.date = _raw['datetime']
        self.endpoint = EndPointEntity(_raw['endpoint'])
        self.relation = _raw['relation']

    def __str__(self):
        return '{} Endpoint({}) on {}: {} -{}-> {}'.format(self.__class__.__name__, self.endpoint['uuid'], self.date, self.process['image'], self.relation, self.file['path'])

    def get_value(self):
        return '{} -{}-> {}'.format(self.process['image'], self.relation, self.file['path'])

class RegistryBehavior(BaseBehavior):
    CONTEXT = ['process', 'reg', 'file', 'endpoint']
    def __init__(self, _raw):
        super(RegistryBehavior, self).__init__(_raw)

        self.process = ProcessEntity(_raw['process'])
        self.reg = RegistryEntity(_raw['reg'])
        self.file = FileEntity(_raw['file'])
        self.date = _raw['datetime']
        self.endpoint = EndPointEntity(_raw['endpoint'])
        self.relation = _raw['relation']

    def __str__(self):
        return '{} Endpoint({}) on {}: {} -{}-> {} {} {}'.format(self.__class__.__name__, self.endpoint['uuid'], self.date, self.process['image'], self.relation, self.reg['path'], self.reg['key'], self.reg['value'])

    def get_value(self):
        return '{} -{}-> {} {} {}'.format(self.process['image'], self.relation, self.reg['path'], self.reg['key'], self.reg['value'])


BEHAVIOR_SETS = [
    ProcessBehavior,
    NetworkBehavior,
    FileBehavior,
    RegistryBehavior,
]