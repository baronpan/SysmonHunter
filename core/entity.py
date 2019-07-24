# -*- coding: utf-8 -*-
import pandas
from core.utils import *

class BaseEntity(object):
    TYPE = 'base'
    PROPS = []
    def __init__(self, _raw):
        self.props = {}

        if _raw:
            for key, value in _raw.iteritems():
                self.__setitem__(key, value)

    def __getitem__(self, key):
        if key not in self.__class__.PROPS:
            raise KeyError()

        return self.props[key] if key in self.props.keys() else ''

    def __setitem__(self, key, value):
        if key not in self.__class__.PROPS:
            raise KeyError()

        if value is None or value is pandas.np.nan:
            self.props[key] = ''
        else:
            self.props[key] = value.encode('utf-8')


class FileEntity(BaseEntity):
    TYPE = 'file'
    PROPS = ['hash', 'path', 'name', 'sig', 'type']

    def __init__(self, _raw):
        super(FileEntity, self).__init__(_raw)

class ProcessEntity(BaseEntity):
    TYPE = 'process'
    PROPS = ['pid', 'image', 'cmdline', 'user', 'calltrace', 'guid']
    
    def __init__(self, _raw):
        super(ProcessEntity, self).__init__(_raw)
        
class NetworkEntity(BaseEntity):
    TYPE = 'network'
    PROPS = ['clientip', 'clientport', 'rip', 'rport', 'protocol', 'rhost', 'ua', 'url']
    
    def __init__(self, _raw):
        super(NetworkEntity, self).__init__(_raw)

class RegistryEntity(BaseEntity):
    TYPE = 'reg'
    PROPS = ['path', 'key', 'value']
    
    def __init__(self, _raw):
        super(RegistryEntity, self).__init__(_raw)


class EndPointEntity(BaseEntity):
    TYPE = 'endpoint'
    PROPS = ['uuid', 'ip']

    def __init__(self, _raw):
        super(EndPointEntity, self).__init__(_raw)

class UserEntity(BaseEntity):
    TYPE = 'user'
    PROPS = ['name', 'domain', 'privilege']

    def __init__(self, _raw):
        super(UserEntity, self).__init__(_raw)

class ServiceEntity(BaseEntity):
    pass