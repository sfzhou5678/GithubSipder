# encoding:utf-8
import re
import pickle
import collections

import datetime
import time

date = "2018-02-12T09:22:02Z"
print(time.strptime(date, "%Y-%m-%dT%H:%M:%SZ"))

now = time.strptime(time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
print(now)
