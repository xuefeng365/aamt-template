# -*- coding: UTF-8 -*-
# @Software: PyCharm
# @File: config.py
# @Author: xuefeng365
# @E-mail: 120158568@qq.com,
# @Site:
# @Time: 11月 23, 2022


import configparser
import os

import yaml


class Config():
    # 全局项目根目录
    project_root_dir = ''
    # project_root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Operate_config(Config):

    def __init__(self):
        super().__init__()

        self.env_configpath = os.path.join(self.project_root_dir, "resources", "aamt.ini")

        # 实例化configParser对象
        self.conf = configparser.ConfigParser()
        self.conf.read(self.env_configpath, encoding="utf-8")

    # 读取配置文件中的key值  (读取)
    def read_token(self, section='Token', key=''):
        return self.conf.get(section, key)

    # 读取配置文件中的key值  (读取)
    def read_environ_active(self, section='Environ', key='active'):
        return self.conf.get(section, key)

    # 将value的值写入配置文件中
    def write(self, section='Token', key='', value=''):
        self.conf.set(section, key, value)  # 给iphone分组设置 key:value  (iphone_url:www.xxx.com)

        # 写入文件
        with open(self.env_configpath, 'w', encoding="utf-8") as configfile:
            self.conf.write(configfile)


class Read_yaml(Operate_config):

    def __init__(self):
        super().__init__()

    def get_env_vars_yaml(self):
        env_active = self.read_environ_active()
        env_filename = f'env_vars_{env_active}.yaml'
        with open(
                os.path.join(self.project_root_dir, "resources", "env_vars", env_filename), encoding="utf-8") as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)

    def get_test_yaml(self, filepath):
        '''
        filepath="/brand/brand_controller.yaml"
        '''
        # 测试用例数据
        test_data_path = f"{Config.project_root_dir}/data/{filepath}".replace("\\", "/").replace("//", "/")

        with open(test_data_path, encoding="utf-8") as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)


def get_file_path(file_name, middle='file'):
    '''
    file_name: 文件名，比如 xiaoxin.png
    '''

    filePath = f"{Config.project_root_dir}/{middle}/{file_name}".replace("\\", "/").replace("//", "/")
    return filePath


def fixture_paths(root_path=Config.project_root_dir):
    """
    fixture路径，1、项目下的fixtures；2、aamt下的fixture；
    :return:
    """
    _fixtures_dir = os.path.join(root_path, "fixtures")
    paths = []
    # 项目下的fixtures
    for root, _, files in os.walk(_fixtures_dir):
        for file in files:
            if file.startswith("fixture_") and file.endswith(".py"):
                full_path = os.path.join(root, file)
                import_path = full_path.replace(_fixtures_dir, "").replace("\\", ".")
                import_path = import_path.replace("/", ".").replace(".py", "")
                paths.append("fixtures" + import_path)
    # aamt下的fixture
    paths.append("aamt.fixture")
    return paths

# 获取配置文件中的key值 (token值)
# systerm_admin_token = Operate_config().read_token(key='systerm_admin_token')
# print(Config.project_root_dir)
