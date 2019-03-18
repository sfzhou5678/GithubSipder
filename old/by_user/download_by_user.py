# encoding:utf-8

"""
1. 某个用户作为起点
2. 首先获取用户star的项目列表(url+type+star数)
3. 遍历项目列表，download[Python类别并且没重复处理过的项目]
4. 下载完当前的项目之后，找到此项目的stargazers，并把所有不重复的用户加入到user_to_be_handler队列
"""
import urllib.request
from bs4 import BeautifulSoup
import re
import os
import zipfile
import threading
import time


def get_page_source(curUrl):
  req = urllib.request.Request(curUrl)

  req.add_header('User-Agent',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36')
  page_source = urllib.request.urlopen(req).read()
  return page_source


def get_total_page_number(page_source):
  bs_obj = BeautifulSoup(page_source, 'lxml')
  try:
    paginations = bs_obj.find('div', {'class': 'pagination'}).find_all('a')
    page_number = 0
    for label in paginations:
      try:
        page_number = max(page_number, int(label.get_text()))
      except:
        pass
    return page_number
  except:
    return 1


def get_last_apperence_index(string, target):
  last_position = -1
  while True:
    position = string.find(target, last_position + 1)
    if position == -1:
      return last_position
    last_position = position
  return last_position


def get_repo_list(page_source):
  """
  传入页面源码，返回bsobj形式的ul主体(repo_list)
  :param page_source:
  :return:
  """
  bs_obj = BeautifulSoup(page_source)
  repo_list = bs_obj.find('ul', {'class': 'repo-list js-repo-list'})
  return repo_list


def download_project(project_url, download_folder_path, unzip=False):
  baseurl = r'https://codeload.github.com'
  download_url = baseurl + project_url + r'/zip/master'
  try:
    r = urllib.request.urlopen(download_url)
    # download zip
    filepath = os.path.join(download_folder_path, project_url[1:].replace(r'/', '_')) + r'.zip'
    f = open(filepath, 'wb')
    f.write(r.read())
    f.close()
    # print('download completed')

    if (unzip):
      # unzip
      zipf = zipfile.ZipFile(filepath, 'r')
      for file in zipf.namelist():
        zipf.extract(file, filepath.replace(r'.zip', ''))
      zipf.close()
      # print('unzip conpleted')

      # delete zip
      os.remove(filepath)
      # print(filepath+"  completed")
  except:
    print(project_url + ' error')


def get_star_count(string):
  nums = re.findall('[0-9]+', string)
  return nums[-1]


def is_reduntant_project(project_name):
  """
  判断当前项目是否已经处理过
  加锁操作在外部处理
  """
  global handled_project
  if project_name in handled_project:
    print(project_name)
    return True
  return False


def is_reduntant_user(user_url):
  """
  判断当前用户是否已经处理过
  加锁操作在外部处理
  """
  global handled_user
  if user_url in handled_user:
    print(user_url)
    return True
  return False


def handle_stargazer(project_href):
  global threadLock

  url = base_url + project_href + r'/stargazers'
  page_source = get_page_source(url)

  bsobj = BeautifulSoup(page_source, 'lxml')
  # todo while has next page？？
  gazer_list = bsobj.find_all('li', {'class': 'follow-list-item float-left border-bottom'})

  threadLock.acquire()
  for i in range(len(gazer_list)):
    gazer = gazer_list[i]
    user_url = gazer.find('h3', {'class': 'follow-list-name'}).find('a')['href']

    if is_reduntant_user(user_url):
      continue
    user_to_be_handler.append(user_url)
  threadLock.release()


def handle_user():
  global threadLock

  while (len(user_to_be_handler) > 0):
    threadLock.acquire()
    cur_user = user_to_be_handler[0]
    del user_to_be_handler[0]
    handled_user.append(cur_user)
    cur_url = base_url + cur_user + '?tab=stars'
    threadLock.release()

    page_source = get_page_source(cur_url)
    total_page_number = get_total_page_number(page_source)

    for i in range(total_page_number):
      bsobj = BeautifulSoup(page_source, 'lxml')
      project_list = bsobj.find_all('div', {'class': 'col-12 d-block width-full py-4 border-bottom'})
      for j in range(len(project_list)):
        try:
          project = project_list[j]

          project_href = project.find('div', {'class': 'd-inline-block mb-1'}).find('a')['href']
          project_name = project_href[get_last_apperence_index(project_href, r'/') + 1:]
          threadLock.acquire()
          if is_reduntant_project(project_name):
            threadLock.release()
            continue
          handled_project.append(project_name)
          threadLock.release()

          project_type = project.find('div', {'class': 'f6 text-gray mt-2'}).find('span',
                                                                                  {'class': 'mr-3'}).string.strip()
          project_star = get_star_count(project.find('div', {'class': 'f6 text-gray mt-2'}).find('a', {
            'class': 'muted-link tooltipped tooltipped-s mr-3'}).text)
          if project_type != 'Python' or int(project_star) < 5:
            continue

          download_project(project_href, download_folder_path, unzip=False)
          handle_stargazer(project_href)
        except:
          pass


def setup_thread(thread_count):
  def threadStart():
    thread = threading.Thread(target=handle_user)
    thread.start()

  threadStart()
  time.sleep(15)
  for i in range(thread_count):
    threadStart()
    time.sleep(1)


base_url = r'https://github.com'
download_folder_path = r'C:\Users\hasee\Desktop\github-python-download'
threadLock = threading.Lock()

handled_user = []
user_to_be_handler = []

handled_project = []

user_to_be_handler.append(r'/dongzhuoyao')

import socket

socket.setdefaulttimeout(30)

setup_thread(15)
