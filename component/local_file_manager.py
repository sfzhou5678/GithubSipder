import os
import zipfile


class LocalFileManager(object):
  def __init__(self, base_folder, http_manager, unzip=False):
    self.unzip = unzip
    self.http_manager = http_manager

    self.base_folder = base_folder
    if not os.path.exists(self.base_folder):
      os.makedirs(self.base_folder)

  def download(self, url, relative_save_path):
    true_save_path = os.path.join(self.base_folder, relative_save_path)  # 实际运行时base_folder是可变的，所以要分离开来
    self.do_download_repo(url, true_save_path)
    self.clean_repo(true_save_path)  ## local_save_path目录里将会有一个名为{repo_name}_{branch}的文件夹, 需要过滤文件并且删除该文件夹

  def do_download_repo(self, download_url, true_save_path):
    """
    注意: download_url有时候可能会出错(比如html版无法得到branch, 可能就会下错)
    :param download_url:
    :param true_save_path:
    :return:
    """
    if not os.path.exists(true_save_path):
      os.makedirs(true_save_path)
    true_save_path += '/repo.zip'
    try:
      file_data = self.http_manager.read_url(download_url)
      f = open(true_save_path, 'wb')
      f.write(file_data)
      f.close()

      if (self.unzip):
        zipf = zipfile.ZipFile(true_save_path, 'r')
        for file in zipf.namelist():
          zipf.extract(file, true_save_path.replace('repo.zip', ''))
        zipf.close()
        os.remove(true_save_path)
    except:
      print(download_url + ' error')

  def clean_repo(self, true_save_path):
    pass
