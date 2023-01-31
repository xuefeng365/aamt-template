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
from loguru import logger

class Config():
    # 全局项目根目录
    project_root_dir = ''


def fixture_paths(root_path=Config.project_root_dir):
    '''
    fixture路径，1、项目下的fixtures；2、aamt下的fixture；
    :return:
    '''
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
    logger.info(f'1、项目下的fixtures：{paths}')
    # aamt下的fixture
    paths.append("aamt.fixture")
    logger.info(f'2、aamt下的fixtures：{[paths[-1]]}')
    return paths

