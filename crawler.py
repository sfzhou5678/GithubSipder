from component import CrawlerScheduler, HttpManager, DBManager, LocalFileManager, HtmlInfoProcessor, APIInfoProcessor
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
import requests

if __name__ == '__main__':
  base_folder = r'D:\DeeplearningData\GithubCode\Java'
  seed_users = ['gaopu', 'sfzhou5678']
  target_languages = ['Java']
  threads = 0

  unzip = False
  clean_repo = False

  use_proxy = False
  default_timeout = 10

  db_config = 'data/db_info.json'
  db_info = json.load(open(db_config))
  print(db_info)

  agents = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36']

  db = DBManager(db_info)
  http_manager = HttpManager(agents, use_proxy=use_proxy, default_timeout=default_timeout)
  file_manager = LocalFileManager(base_folder, http_manager, unzip=unzip, clean_repo=clean_repo)
  info_processor = HtmlInfoProcessor(http_manager)
  # info_processor=APIInfoProcessor(http_manager)

  scheduler = CrawlerScheduler(target_languages, seed_users,
                               db, http_manager, file_manager, info_processor,
                               threads=threads)
  scheduler.seed_warmup()
  scheduler.start_processor()
