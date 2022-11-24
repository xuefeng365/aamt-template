# -*- coding: UTF-8 -*-
# @Software: PyCharm
# @File: fixture.py
# @Author: xuefeng365
# @E-mail: 120158568@qq.com,
# @Site:
# @Time: 11月 23, 2022

import pytest
from faker import Faker

from aamt.config import *


class Project:
    dir = ""


def _project_dir(session):
    # 从缓存中获取项目根目录
    project_dir = session.config.cache.get("project_dir", None)
    if not project_dir:
        # 第一次运行没有.pytest_cache
        cwd = os.getcwd()
        tests = cwd.find("tests")
        samples = cwd.find("samples")
        if tests > 0:
            project_dir = cwd[:cwd.find("tests")]
        elif samples > 0:
            project_dir = cwd[:cwd.find("samples")]
        else:
            project_dir = cwd
    return project_dir


def pytest_sessionstart(session):
    Project.dir = _project_dir(session)


@pytest.fixture(scope="session")
def faker_ch():
    """中文造数据"""
    return Faker(locale="zh_CN")


@pytest.fixture(scope="session")
def faker_en():
    """英文造数据"""
    return Faker()


@pytest.fixture(scope="session")
def pd():
    """pandas库"""
    try:
        import pandas
        return pandas
    except ModuleNotFoundError:
        pass


@pytest.fixture(scope="session")
def file_dir():
    """file目录的路径"""
    return os.path.join(Project.dir, "file")



@pytest.fixture(scope="session")
def env_vars():
    """读取激活环境下的yaml文件里的配置信息（账号、密码、数据库等）"""
    return Read_yaml().get_env_vars_yaml()




