import os
import json
import time
import zipfile
import urllib.request
import socket
import random
import threading
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
from datetime import datetime
import requests

# agents = [
#   'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0',
#   'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
#   'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
#   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER'
#   'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
#   'Opera/9.25 (Windows NT 5.1; U; en)',
#   'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
#   'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
#   'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
#   'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
#   "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
#   "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
#   "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0"
# ]
with open('data/user_agents.txt') as f:
  agents = [line.strip() for line in f.readlines()]
proxies = []
overdue_ips = set()


def update_proxies():
  print('Update proxies...')
  global proxies
  global overdue_ips

  for page in range(3):
    url = 'http://www.xicidaili.com/nn/%s' % ('' if page == 0 else str(page + 1))

    headers = {'User-Agent': agents[random.randint(0, len(agents) - 1)]}
    web_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    for i in range(1, len(ips)):
      ip_info = ips[i]
      tds = ip_info.find_all('td')
      ip = 'http://' + tds[1].text + ':' + tds[2].text
      if ip not in overdue_ips and ip not in proxies:
        proxies.append(ip)
  print('Available proxies num:', len(proxies))


def get_random_proxy():
  global proxies
  proxy_ip = random.choice(proxies)
  proxy = {'http': proxy_ip}
  return proxy


def read_url(url, use_proxy=False):
  time.sleep(1)  # 每次都延缓一下
  if not use_proxy:
    req = urllib.request.Request(url)
    req.add_header('User-Agent', agents[random.randint(0, len(agents) - 1)])
    page_source = urllib.request.urlopen(req).read()
    page_source = page_source.decode("UTF-8")
  else:
    if len(proxies) <= 10:
      update_proxies()
    page_source = '[]'
    while len(proxies) > 0:
      header = {'User-Agent': agents[random.randint(0, len(agents) - 1)]}
      proxy = get_random_proxy()
      proxy_handler = urllib.request.ProxyHandler(proxy)
      opener = urllib.request.build_opener(proxy_handler)
      request = urllib.request.Request(url, headers=header)
      try:
        page_source = opener.open(request).read().decode('utf-8')
        break
      except HTTPError as e:
        print('HTTP Error, error code: ', e.code)
        proxies.remove(proxy['http'])
        overdue_ips.add(proxy['http'])
      except URLError as e:
        print('Url error, Reason: ', e.reason)
        return '[]'

  return page_source


def get_repos(user_name, type):
  """
  type=['repos','starred']
  1. 获取某个user的repos信息: https://api.github.com/users/{user_name}/repos
  2. 获取某用户所有star了的repo的信息(和2相反):https://api.github.com/users/{user_name}/starred
  :param user_name: 
  :param type: 
  :return: 
  """
  url = 'https://api.github.com/users/%s/%s' % (user_name, type)
  repos = json.loads(read_url(url))
  # try:
  #   repos = json.loads(read_url(url))
  # except:
  #   # TODO: 记录错误记录
  #   repos = []
  #   print('Get repos error_%s_%s' % (user_name, type))
  #   time.sleep(3)
  return repos


def process_user(user_name):
  """
  将user信息存入DB
  :param user_name: 
  :return: 
  """
  pass


def process_stargazers(stargazers_url, user_name_set):
  try:
    users = json.loads(read_url(stargazers_url))
  except:
    users = []
  if len(users) > 0:
    global thread_lock
    thread_lock.acquire()
    for user in users:
      user_id = user['id']
      user_name = user['login']
      if user_name not in user_name_set:
        process_user(user_name)
        user_name_set.add(user_name)
        user_stack.append(user_name)
    thread_lock.release()


def transform_datetime(ts):
  """
  输入的ts形如"2018-02-12T09:22:02Z"
  :param datetime:
  :return:
  """
  ts = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
  return ts


def download_repo(download_url, local_save_path, unzip=True):
  local_save_path += '/repo.zip'
  try:
    r = urllib.request.urlopen(download_url)
    f = open(local_save_path, 'wb')
    f.write(r.read())
    f.close()

    if (unzip):
      zipf = zipfile.ZipFile(local_save_path, 'r')
      for file in zipf.namelist():
        zipf.extract(file, local_save_path.replace('repo.zip', ''))
      zipf.close()
      os.remove(local_save_path)
  except:
    print(download_url + ' error')


def clean_repo_files(local_save_path):
  pass


def process_repo(base_folder, repo, user_name_set, processed_repo_set,
                 target_language=None):
  """
  repo表(要过滤掉fork==True的项目):
  user_id, repo_id, repo_name, repo_url,description,default_branch,
  language, local_save_path,
  create_time, update_time,
  star_cnt, fork_cnt,
  file_cnt, token_cnt, snippet_cnt

  :param repo:
  :return:
  """
  global thread_lock
  thread_lock.acquire()
  repo_id = str(repo['id'])
  if repo_id in processed_repo_set:
    thread_lock.release()
    return
  if repo['fork']:
    processed_repo_set.add(repo_id)
    thread_lock.release()
    return
  language = repo['language']
  if target_language and language != target_language:
    processed_repo_set.add(repo_id)
    thread_lock.release()
    return
  processed_repo_set.add(repo_id)  # TODO: 改成in_processing_repo_set?
  thread_lock.release()

  user_id = str(repo['owner']['id'])
  user_name = repo['owner']['login']

  repo_name = repo['name']
  repo_url = repo['html_url']
  default_branch = repo['default_branch']
  description = repo['description']
  if description is None:
    description = ''

  create_time = transform_datetime(repo['created_at'])
  update_time = transform_datetime(repo['updated_at'])

  ## 因为要做personal, 所以就不舍star的阈值了, 不过之后可以在db里根据star数进行筛选
  star_cnt = repo['stargazers_count']
  fork_cnt = repo['forks_count']

  file_cnt, token_cnt, snippet_cnt = -1, -1, -1  ## 这些等待第二步处理
  ## 获取star了当前repo的所有用户的信息
  stargazers_url = repo['stargazers_url']
  process_stargazers(stargazers_url, user_name_set)

  download_url = "https://codeload.github.com/%s/%s/zip/%s" % (user_name, repo_name, default_branch)
  local_save_path = os.path.join('user_' + user_id, repo_name + '_' + repo_id)  # 这个是存储到db的在base_folder之下的路径
  true_save_path = os.path.join(base_folder, local_save_path)  # 实际运行时base_folder是可变的，所以要分离开来
  if not os.path.exists(true_save_path):
    os.makedirs(true_save_path)
  download_repo(download_url, true_save_path, unzip=True)
  clean_repo_files(true_save_path)  ## local_save_path目录里将会有一个名为{repo_name}_{branch}的文件夹, 需要过滤文件并且删除该文件夹
  ## TODO: 2. save repo infos

  processed_repo_set.add(repo_id)


def user_processor():
  global thread_lock

  while len(user_stack):
    """
    每次拿出一个user, 做的事情有:
    1. 获取这个user所有star了的项目star_repos
    2. 获取当前用户自己的仓库repos
    3. repos+=star_repos, 然后process repo(在这里下载当前repo(到owner的id目录), 同时将该项目的stargazers都加入user_stack)
    """

    thread_lock.acquire()
    print(len(user_stack))
    user_name = user_stack.pop()
    thread_lock.release()
    star_repos = get_repos(user_name, 'starred')
    repos = get_repos(user_name, 'repos')
    repos += star_repos
    for repo in repos:
      process_repo(base_folder, repo, user_name_set, processed_repo_set, target_language='Java')


def setup_thread(thread_count):
  thread = threading.Thread(target=user_processor)
  thread.start()
  time.sleep(60)  # 这是为了更新待处理的user池, 避免threads提前退出

  for i in range(thread_count - 1):
    thread = threading.Thread(target=user_processor)
    thread.start()
    time.sleep(1)


if __name__ == '__main__':
  socket.setdefaulttimeout(10)

  # TODO: 加入db
  # TODO: 加入resotre from cache
  base_folder = r'D:\DeeplearningData\GithubCode\Java'
  if not os.path.exists(base_folder):
    os.makedirs(base_folder)
  seed_users = ['gaopu', 'sfzhou5678']

  ## TODO: 各种set, stack封装成类
  user_name_set = set()
  processed_repo_set = set()
  user_stack = []  # TODO: 处理一下star和repo的交互逻辑

  for user_name in seed_users:
    if user_name not in user_name_set:
      ## TODO: save user infos
      process_user(user_name)
      user_name_set.add(user_name)
      user_stack.append(user_name)

  thread_lock = threading.Lock()
  setup_thread(15)
