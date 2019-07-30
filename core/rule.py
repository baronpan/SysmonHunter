# -*- coding: utf-8 -*-
import re

from core.behavior import *
from core.entity import *
from core.attck import ATTCKTech
from core.utils import *

CONDITION_MAPPING = {
    'ProcessBehavior': 'process',
    'NetworkBehavior': 'network',
    'FileBehavior': 'file',
    'RegistryBehavior': 'reg',
}

def filter_abnormal_behaviors(behaviors, rules):
    result = []
    for behav in behaviors:
        _attcks = match(behav, rules)
        if len(_attcks) > 0:
            behav.attck_ids = ', '.join(_attcks)
            result.append(behav)
    return result

# return list of matched tech id.
def match(behavior, rules):
    result = []

    behavior_type = type(behavior).__name__
    
    for rule_id, ruleset in rules.iteritems():
        is_matched = False
        rules = [rule for rule in ruleset.conditions if rule['type'] == CONDITION_MAPPING[behavior_type]]
        if behavior_type == 'ProcessBehavior':
            is_matched = match_process_behavior(behavior, rules)
        elif behavior_type == 'NetworkBehavior':
            is_matched = match_network_behavior(behavior, rules)
        elif behavior_type == 'FileBehavior':
            is_matched = match_file_behavior(behavior, rules)
        elif behavior_type == 'RegistryBehavior':
            is_matched = match_registry_behavior(behavior, rules)
        if is_matched:
            result.append(rule_id)
    return result
                
def match_process_behavior(behavior, ruleset):
    for cond in ruleset:
        bresult = []

        if 'process' in cond.keys():
            bresult.append(match_entity(behavior.parent, cond['process']) or match_entity(behavior.current, cond['process']))
        
        if 'file' in cond.keys():
            bresult.append(match_entity(behavior.file, cond['file']))

        is_matched = False
        if 'op' in cond.keys() and cond['op'] == 'and':
            is_matched = op_and(bresult)
        else:
            is_matched = op_or(bresult)
        if is_matched:
            return True
    return False

def match_network_behavior(behavior, ruleset):
    for cond in ruleset:
        bresult = []
        if 'process' in cond.keys():
            bresult.append(match_entity(behavior.process, cond['process']))

        if 'network' in cond.keys():
            bresult.append(match_entity(behavior.network, cond['network']))
        
        if 'file' in cond.keys():
            bresult.append(match_entity(behavior.file, cond['file']))

        is_matched = False
        if 'op' in cond.keys() and cond['op'] == 'and':
            is_matched = op_and(bresult)
        else:
            is_matched = op_or(bresult)
        if is_matched:
            return True
    return False

def match_file_behavior(behavior, ruleset):
    for cond in ruleset:
        bresult = []

        if 'process' in cond.keys():
            bresult.append(match_entity(behavior.process, cond['process']))
        
        if 'file' in cond.keys():
            bresult.append(match_entity(behavior.file, cond['file']))

        is_matched = False
        if 'op' in cond.keys() and cond['op'] == 'and':
            is_matched = op_and(bresult)
        else:
            is_matched = op_or(bresult)
        if is_matched:
            return True
    return False
    
def match_registry_behavior(behavior, ruleset):
    for cond in ruleset:
        bresult = []
        
        if 'process' in cond.keys():
            bresult.append(match_entity(behavior.process, cond['process']))
        
        if 'file' in cond.keys():
            bresult.append(match_entity(behavior.file, cond['file']))

        if 'reg' in cond.keys():
            bresult.append(match_entity(behavior.reg, cond['reg']))

        is_matched = False
        if 'op' in cond.keys() and cond['op'] == 'and':
            is_matched = op_and(bresult)
        else:
            is_matched = op_or(bresult)
        if is_matched:
            return True
    return False

def match_entity(entity, cond):
    bresult = []

    if 'any' in cond.keys():
        for p in entity.props.keys():
            bresult.append(__prop_query(entity.props[p], cond['any']))
        return op_or(bresult)
    
    for p in cond.keys():
        if p in entity.props.keys():
            bresult.append(__prop_query(entity.props[p], cond[p]))
    return op_and(bresult)

# 默认 op 是 or
def __query_nocase(p, conds, op):
    match = [p.lower().find(cond.lower()) != -1 for cond in conds]
    if op == 'or':
        return op_or(match)
    elif op == 'and':
        return op_and(match) 
    elif op == 'not':
        return op_not(match)

def __query_case(p, conds, op):
    match = [p.find(cond) != -1 for cond in conds]
    if op == 'or':
        return op_or(match)
    elif op == 'and':
        return op_and(match) 
    elif op == 'not':
        return op_not(match)

def __query_regex(p, conds, op):
    match = [re.search(re.compile(cond.lower()), p.lower()) != None for cond in conds]
    if op == 'or':
        return op_or(match)
    elif op == 'and':
        return op_and(match) 
    elif op == 'not':
        return op_not(match)
        

def __prop_query(prop, cond):
    op = cond['op'] if 'op' in cond.keys() else 'or'

    if 'flag' not in cond.keys() or cond['flag'] == 'nocase':
        return __query_nocase(prop, cond['pattern'].split('|'), op)
    elif cond['flag'] == 'regex':
        return __query_regex(prop, cond['pattern'].split('|'), op)
    elif cond['flag'] == 'case':
        return __query_case(prop, cond['pattern'].split('|'), op)
    return False