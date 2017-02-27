# encodint:utf-8

import urllib.request
from bs4 import BeautifulSoup
import download
import re

def get_page_source(curUrl):
    req = urllib.request.Request(curUrl)


    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36')
    page_source = urllib.request.urlopen(req).read()
    return page_source


def get_total_page_number(page_source):
    bs_obj=BeautifulSoup(page_source)
    paginations=bs_obj.find('div',{'class':'pagination'}).find_all('a')
    page_number=0
    for label in paginations:
        try:
            page_number=max(page_number,int(label.get_text()))
        except:
            pass
    return page_number


def get_start(downloaded_urls,url,save_path,deepth):
    if(deepth>8):
        return
    page_source=get_page_source(url)
    total_page_number=get_total_page_number(page_source)
    reg=re.compile('p=[0-9]+')

    for i in range(total_page_number):
        cur_url=reg.sub('p='+str(i+1),url)
        page_source=get_page_source(cur_url)
        repo_list=download.get_repo_list(page_source)
        project_urls=download.get_proj_urls(repo_list)
        for new_url in project_urls:
            if new_url not in downloaded_urls:
                downloaded_urls[new_url]='0'
            else:
                project_urls.remove(new_url)
        download.download_projects(project_urls,save_path,unzip=False)

    for (k,v) in downloaded_urls.items():
        if downloaded_urls[k] =='0':
            key_word=k.split(r'/')[-1]
            newurl=r'https://github.com/search?p=1&q='+key_word+r'+language%3APython+stars%3A%3E5&ref=searchresults&type=Repositories&utf8=%E2%9C%93'
            downloaded_urls[k]='1'
            get_start(downloaded_urls,newurl,save_path,deepth+1)
    print(downloaded_urls)

# https://github.com/search?utf8=%E2%9C%93&q=python123+language%3APython+stars%3A%3E5&type=Repositories&ref=searchresults
url=r'https://github.com/search?p=1&q=language%3APython+stars%3A%3E5&ref=searchresults&type=Repositories&utf8=%E2%9C%93'
save_path=r'D:\DeeplearningData\github-python-download'

# 格式为:'/username/project_name':'0|1' 1/0分别表示已/未访问
downloaded_urls={}
get_start(downloaded_urls,url,save_path,1)

