# -*- coding: utf-8 -*-

# @Software: PyCharm
# @File: plugin.py
# @Author: xuefeng365
# @E-mail: 120158568@qq.com,
# @Site: 
# @Time: 11月 23, 2022

import inspect
import os
import shutil
import tempfile
import time

import allure_commons
from allure_commons.logger import AllureFileLogger
from allure_pytest.listener import AllureListener
from allure_pytest.plugin import cleanup_factory

from aamt.config import Config, fixture_paths

# allure临时目录
allure_temp = tempfile.mkdtemp()


def aamt_plugins():
    # conftest 加载插件时，从调用堆栈列表里获取信息，再组装成所需路径
    caller = inspect.stack()[1]
    # 保存项目根路径
    Config.project_root_dir = os.path.dirname(caller.filename)
    # 获取所有fixture路径，1、项目下的fixtures；2、aamt下的fixture；
    plugins_path = fixture_paths(root_path=Config.project_root_dir)  # +[其他插件]
    return plugins_path


class Plugin:
    @staticmethod
    def pytest_addoption(parser):
        # allure测试报告 命令行参数
        parser.addoption(
            "--aamt-reports",
            action="store_const",
            const=True,
            help="Create aamt allure HTML reports."
        )

    @staticmethod
    def _aamt_reports(config):
        # 判断参数是否生效，防止跟allure自带参数冲突
        if config.getoption("--aamt-reports") and not config.getoption("allure_report_dir"):
            return True
        else:
            return False

    @staticmethod
    def pytest_configure(config):
        if Plugin._aamt_reports(config):
            test_listener = AllureListener(config)
            config.pluginmanager.register(test_listener)
            allure_commons.plugin_manager.register(test_listener)
            config.add_cleanup(cleanup_factory(test_listener))

            clean = config.option.clean_alluredir
            file_logger = AllureFileLogger(allure_temp, clean)
            allure_commons.plugin_manager.register(file_logger)
            config.add_cleanup(cleanup_factory(file_logger))

    @staticmethod
    def pytest_sessionfinish(session):
        # 测试运行结束后生成allure报告
        if Plugin._aamt_reports(session.config):
            reports_dir = os.path.join(Config.project_root_dir, "reports")
            current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
            new_report = os.path.join(reports_dir, "report-" + current_time)
            if os.path.exists(reports_dir):
                # 复制历史报告，填充allure趋势图数据
                his_reports = os.listdir(reports_dir)
                if his_reports:
                    latest_report_history = os.path.join(reports_dir, his_reports[-1], "history")
                    shutil.copytree(latest_report_history, os.path.join(allure_temp, "history"))
            os.system(f"allure generate {allure_temp} -o {new_report}  --clean")
            shutil.rmtree(allure_temp)


