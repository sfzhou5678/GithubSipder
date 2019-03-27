import os
import json
import threading


class CrawlerScheduler(object):
  def __init__(self, target_languages, seed_users,
               db, http_manager, file_manager, info_processor,
               threads=0):
    """
    控制user_queue, processed_user_set,
     repo_queue,processed_repo_set

    :param target_languages:
    :param seed_users:
    :param db:
    :param http_manager:
    :param file_manager:
    :param info_processor: 给定user或repo name, info_processor可获取更具体的相关信息(走API或走html)
    :param threads: 线程数，0表示使用单线程
    """
    self.target_languages = set(target_languages)
    self.seed_users = seed_users
    self.threads = threads
    self.thread_lock = threading.Lock()

    self.db = db
    self.http_manager = http_manager
    self.file_manager = file_manager
    self.info_processor = info_processor

    self.user_name_set = set()
    self.processed_repo_set = set()
    self.user_stack = []

  def restore(self, log_path):
    pass

  def seed_warmup(self):
    """
    第一次运行时调用，和restore冲突
    :return:
    """
    for user_name in self.seed_users:
      if user_name not in self.user_name_set:
        user_info = self.info_processor.get_user_info(user_name)
        self.db.record_user(user_info)
        self.user_name_set.add(user_name)
        self.user_stack.append(user_name)

  def start_processor(self):
    """
    实际运行程序的入口，多线程也调用这个函数

    :return:
    """
    while len(self.user_stack):
      """
      每次拿出一个user, 做的事情有:
      1. 获取这个user所有star了的项目star_repos
      2. 获取当前用户自己的仓库repos
      3. repo_infos+=starred_repo_infos, 然后process repo_info(在这里下载当前repo(到owner的id目录), 同时将该项目的stargazers都加入user_stack)
      """

      self.thread_lock.acquire()
      print(len(self.user_stack))
      user_name = self.user_stack.pop()
      self.thread_lock.release()

      starred_repo_infos = self.info_processor.get_repo_infos(user_name, 'starred')
      repo_infos = self.info_processor.get_repo_infos(user_name, 'repos')
      repo_infos += starred_repo_infos
      for repo_info in repo_infos:
        self.process_repo(repo_info)

  def process_repo(self, repo_info):
    """
    repo表(要过滤掉fork==True的项目):
    user_id, repo_name, repo_name, repo_url,description,default_branch,
    language, local_save_path,
    create_time, update_time,
    star_cnt, fork_cnt,
    file_cnt, token_cnt, snippet_cnt

    :param repo:
    :return:
    """
    self.thread_lock.acquire()
    repo_name = str(repo_info['repo_name'])
    if repo_name in self.processed_repo_set:
      self.thread_lock.release()
      return
    language = repo_info['language']
    if self.target_languages and language not in self.target_languages:
      self.processed_repo_set.add(repo_name)
      self.thread_lock.release()
      return
    self.processed_repo_set.add(repo_name)  # TODO: 改成in_processing_repo_set?
    self.thread_lock.release()

    user_name = repo_info['user_name']
    default_branch = repo_info['default_branch']

    file_cnt, token_cnt, snippet_cnt = -1, -1, -1  ## 这些等待第二步处理
    ## 获取star了当前repo的所有用户的信息
    stargazers_url = repo_info['stargazers_url']
    stargazers = self.info_processor.get_stargazers(stargazers_url)
    if len(stargazers) > 0:
      self.process_stargazers(stargazers)

    download_url = "https://codeload.github.com/%s/%s/zip/%s" % (user_name, repo_name, default_branch)
    relative_save_path = os.path.join('[%s]' % user_name, repo_name)  # 这个是存储到db的在base_folder之下的路径
    self.file_manager.download(download_url, relative_save_path)

    ## TODO: 2. save repo infos
    self.db.record_repo(repo_info)

  def process_stargazers(self, stargazers):
    self.thread_lock.acquire()

    for user_info in stargazers:
      user_name = user_info['user_name']
      if user_name not in self.user_name_set:
        user_info = self.info_processor.get_user_info(user_name)
        self.db.record_user(user_info)
        self.user_name_set.add(user_name)
        self.user_stack.append(user_name)
    self.thread_lock.release()
