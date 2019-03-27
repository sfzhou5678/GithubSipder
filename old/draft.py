# encoding:utf-8
import re
import pickle
import collections

from datetime import datetime
import time

# date = "2018-02-12T09:22:02Z"
# print(time.strptime(date, "%Y-%m-%dT%H:%M:%SZ"))
# print(time_stamp)
# time_stamp = time.strptime(date, "%Y-%m-%dT%H:%M:%SZ")


#
# now = time.strptime(time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
# print(now)

import psycopg2

conn = psycopg2.connect(database="github_code", user="postgres", password="postgres", host="localhost", port="5432")
cur = conn.cursor()  # 创建指针对象

# 创建表

# try:
#   cur.execute('INSERT INTO "user"(user_id, user_name, user_url) VALUES(%s,%s,%s)', ('', 'zsf1', 'http'))
#   cur.execute('INSERT INTO "user"(user_id, user_name, user_url) VALUES(%s,%s,%s)', ('', 'zsf2', 'http'))
#   conn.commit()
# except Exception as e:
#   print(e)

try:
  time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  print(time_stamp)
  cur.execute(
    'INSERT INTO repo(user_name, repo_id, repo_name, repo_url, description, default_branch, language, local_save_path,record_time) '
    'VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s)',
    ('zsf5678', '', 'test_repo1', 'repo_url', '', 'master', 'Java', 'test_repo-master', time_stamp))
  conn.commit()
except Exception as e:
  print(e)
