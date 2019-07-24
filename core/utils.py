# -*- coding: utf-8 -*-
from datetime import datetime

# datetime format
def format_daterange(tr):
    start = datetime.strptime(tr[0] + ' 00:00:00', '%Y-%m-%d %H:%M:%S').isoformat()
    end = datetime.strptime(tr[1] + ' 23:59:59', '%Y-%m-%d %H:%M:%S').isoformat()
    return (start, end)

# logical operates
def op_or(l):
    if len(l) == 0:
        return False

    bresult = False
    for e in l:
        bresult |= e
    return bresult

def op_and(l):
    if len(l) == 0:
        return False
        
    bresult = True
    for e in l:
        bresult &= e
    return bresult

def op_not(l):
    if len(l) != 1:
        return False
    return not l[0]