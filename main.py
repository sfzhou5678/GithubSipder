import os
import json
import time
import zipfile
import urllib.request
import socket


def read_url(url):
  req = urllib.request.Request(url)
  req.add_header('User-Agent',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36')

  page_source = urllib.request.urlopen(req).read()
  page_source = page_source.decode("UTF-8")
  return page_source


def get_repos(user_name):
  url = 'https://api.github.com/users/%s/repos' % user_name
  try:
    repos = json.loads(read_url(url))
  except:
    # TODO: 记录错误记录
    repos = []
  return repos


def process_user(user_name):
  pass


def process_stargazers(stargazers_url, user_name_set):
  pass


def transform_datetime(datetime):
  """
  输入的datetime形如"2018-02-12T09:22:02Z"
  :param datetime:
  :return:
  """
  datetime = time.strptime(datetime, "%Y-%m-%dT%H:%M:%SZ")
  return datetime


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
  repo_id = str(repo['id'])
  if repo_id in processed_repo_set:
    return
  if repo['fork']:
    processed_repo_set.add(repo_id)
    return
  language = repo['language']
  if target_language and language != target_language:
    processed_repo_set.add(repo_id)
    return

  user_id = str(repo['owner']['id'])
  user_name = repo['owner']['login']

  repo_name = repo['name']
  # FIXME:
  if repo_name.find('CCL') >= 0:
    return
  repo_url = repo['html_url']
  default_branch = repo['default_branch']
  description = repo['description']
  if description is None:
    description = ''

  create_time = transform_datetime(repo['created_at'])
  update_time = transform_datetime(repo['updated_at'])

  star_cnt = repo['stargazers_count']
  fork_cnt = repo['forks_count']

  file_cnt, token_cnt, snippet_cnt = -1, -1, -1  ## 这些等待第二步处理

  download_url = "https://codeload.github.com/%s/%s/zip/%s" % (user_name, repo_name, default_branch)
  local_save_path = os.path.join(base_folder, 'user_' + user_id, repo_name + '_' + repo_id)
  if not os.path.exists(local_save_path):
    os.makedirs(local_save_path)
  download_repo(download_url, local_save_path, unzip=True)
  clean_repo_files(local_save_path)  ## local_save_path目录里将会有一个名为{repo_name}_{branch}的文件夹, 需要过滤文件并且删除该文件夹
  ## TODO: 2. save repo infos

  ## TODO: 3. 获取star了当前repo的所有用户的信息
  stargazers_url = repo['stargazers_url']
  process_stargazers(stargazers_url, user_name_set)

  processed_repo_set.add(repo_id)


if __name__ == '__main__':
  socket.setdefaulttimeout(10)

  # TODO: 加入db
  # TODO: 加入resotre from cache
  base_folder = r'D:\DeeplearningData\GithubCode\Java'
  seed_users = ['sfzhou5678']
  user_name_set = set()
  processed_repo_set = set()
  user_stack = []

  for user_name in seed_users:
    if user_name not in user_name_set:
      ## TODO: save user infos
      process_user(user_name)
      user_name_set.add(user_name)
      user_stack.append(user_name)

  while len(user_stack):
    user_name = user_stack.pop()
    repos = get_repos(user_name)
    for repo in repos:
      process_repo(base_folder, repo, user_name_set, processed_repo_set, target_language='Java')
