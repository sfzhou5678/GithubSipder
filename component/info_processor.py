class InfoProcessor(object):
  def __init__(self):
    pass

  def get_user_info(self, user_name):
    pass

  def get_repo_infos(self, user_name, type):
    """
    获取跟指定的user相关的repo
    :param user_name:
    :param type: ['starred', 'repos']
    :return:
    """
    pass

  def get_stargazers(self, stargazers_url):
    pass


class HtmlInfoProcessor(InfoProcessor):
  def __init__(self):
    super().__init__()

  def get_user_info(self, user_name):
    super().get_user_info(user_name)

  def get_repo_infos(self, user_name, type):
    super().get_repo_infos(user_name, type)

  def get_stargazers(self, stargazers_url):
    super().get_stargazers(stargazers_url)


class APIInfoProcessor(InfoProcessor):
  def __init__(self):
    super().__init__()

  def get_user_info(self, user_name):
    """
    调用http读取user info, 如果读取失败就只保存user_name
    :param user_name:
    :return:
    """
    user_info = {'user_name': user_name}

    # TODO:
    # url = ''
    # try:
    #   data = self.http_manager.read_url(url)
    #   data = json.loads(data)
    # except:
    #   pass

    return user_info

  def get_repo_infos(self, user_name, type):
    """
    type=['repos','starred']
    1. 获取某个user的repos信息: https://api.github.com/users/{user_name}/repos
    2. 获取某用户所有star了的repo的信息(和2相反):https://api.github.com/users/{user_name}/starred
    :param user_name:
    :param type:
    :return:
    """
    url = 'https://api.github.com/users/%s/%s' % (user_name, type)
    repos = json.loads(self.http_manager.read_url(url))
    # try:
    #   repos = json.loads(read_url(url))
    # except:
    #   # TODO: 记录错误记录
    #   repos = []
    #   print('Get repos error_%s_%s' % (user_name, type))
    #   time.sleep(3)
    return repos

  def get_stargazers(self, stargazers_url):
    # FIXME:
    try:
      users = json.loads(self.http_manager.read_url(stargazers_url))
    except:
      users = []
    return users
