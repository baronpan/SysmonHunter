from data import sysmon
from db import es
from utils.common import *

import sys


behavs = sysmon.SysmonData().from_csv(sys.argv[1])