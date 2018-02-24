import requests
from pyquery import PyQuery
import os
import urllib.request
import zipfile


def download_project(project_url, download_folder_path, unzip=False):
  baseurl = r'https://codeload.github.com'
  download_url = baseurl + project_url + r'/zip/master'
  print(download_url)
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


def download(repo_list):
  for repo in repo_list:
    cmd_clone = "git clone " + repo
    os.system(cmd_clone)


def get_github(page_start, page_end):
  repo_list = []
  for i in range(page_start, page_end + 1):
    url = "https://github.com/search?p=" + str(i) + "&q=language%3AJava+stars%3A%3E5&type=Repositories&utf8=%E2%9C%93"
    r = requests.get(url=url)
    for i in PyQuery(r.content)("div.repo-list-item"):
      # print(PyQuery(i).find("a.v-align-middle").attr("href"))
      repo_url = "https://github.com" + PyQuery(i).find("a.v-align-middle").attr("href") + ".git"
      name = PyQuery(i)("a.v-align-middle").text()
      desc = PyQuery(i)("p.col-9").text()
      print("项目：" + name, "描述：" + desc, "项目地址：" + repo_url)

      download_project(PyQuery(i).find("a.v-align-middle").attr("href"),
                       r'E:\GithubJavaRepo', True)
      repo_list.append(repo_url)
      # print(repo_url)
  return repo_list


if __name__ == '__main__':
  repo_list = get_github(1, 3)
  # download(repo_list)
