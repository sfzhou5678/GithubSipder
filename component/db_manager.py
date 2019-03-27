import psycopg2


class DBManager(object):
  def __init__(self, db_info):
    self.conn = psycopg2.connect(database=db_info['database'], user=db_info['user'], password=db_info['password'],
                                 host=db_info['host'], port=db_info['port'])
    self.cur = self.conn.cursor()  # 创建指针对象

  def record_user(self, user_info):
    pass

  def record_repo(self, repo_info):
    pass
