# encoding:utf-8
import urllib.request
import re
import os
from bs4 import BeautifulSoup
import zipfile


def get_proj_urls(bs_obj):
  """
  传入bsobj形式的ul主体，返回ul中所有li下的a标签的href
  :param bs_obj:
  :return:
  """
  project_urls = []
  project_divs = bs_obj.find_all('div', {'class': 'd-inline-block col-9 mb-1'})
  for project in project_divs:
    url = project.find('a', {'class': 'v-align-middle'})['href']
    project_urls.append(url)
  return project_urls


def get_repo_list(page_source):
  """
  传入页面源码，返回bsobj形式的ul主体(repo_list)
  :param page_source:
  :return:
  """
  bs_obj = BeautifulSoup(page_source)
  repo_list = bs_obj.find('ul', {'class': 'repo-list js-repo-list'})
  return repo_list


def download_projects(project_urls, download_folder_path, unzip=False):
  baseurl = r'https://codeload.github.com'
  # https://codeload.github.com/kingname/python/zip/master
  # /kingname/python
  for url in project_urls:
    download_url = baseurl + url + r'/zip/master'
    try:
      r = urllib.request.urlopen(download_url)

      # download zip
      filepath = os.path.join(download_folder_path, url[1:].replace(r'/', '-')) + r'.zip'
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
      print(url + ' error')
