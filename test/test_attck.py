from data import sysmon
from db import es
from utils.common import *
from core import attck
from core import rule

import sys


behavs = sysmon.SysmonData().from_csv(sys.argv[1])
attck_techs = attck.load_attcks(sys.argv[2])

for behav in behavs:
    if len(rule.match(behav, attck_techs)) > 0:
        print behav