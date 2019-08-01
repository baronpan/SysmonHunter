from data import sysmon
from db import es
from utils.common import *

import sys

conf = parse_conf(sys.argv[1])
_es = es.ES(conf)

behavs = sysmon.SysmonData().from_winlogbeat(_es, 'winlogbeat-*', '2019-07-16', '2019-07-16')