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

# allure源文件临时目录，那一堆json文件，生成HTML报告会删除
allure_source_path = ".allure.source.temp"

def _aamt_reports(config):
    """
    --aamt-reports命令行参数不能和allure命令行参数同时使用，否则可能出错。判断参数是否生效，防止跟allure自带参数冲突
    """
    if config.getoption("--aamt-reports") and not config.getoption("allure_report_dir"):
        return True
    return False

def _is_master(config):
    """
    pytest-xdist分布式执行时，判断是主节点master还是子节点
    主节点没有workerinput属性
    """
    return not hasattr(config, 'workerinput')



class Plugin:
    reports_path = os.path.join(Config.project_root_dir, "reports")

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
    def pytest_configure(config):
        """
        这段代码源自：https://github.com/allure-framework/allure-python/blob/master/allure-pytest/src/plugin.py
        目的是生成allure源文件，用于生成HTML报告
        """
        if _aamt_reports(config):
            if os.path.exists(allure_source_path):
                shutil.rmtree(allure_source_path)
            test_listener = AllureListener(config)
            config.pluginmanager.register(test_listener)
            allure_commons.plugin_manager.register(test_listener)
            config.add_cleanup(cleanup_factory(test_listener))

            clean = config.option.clean_alluredir
            file_logger = AllureFileLogger(allure_source_path, clean)  # allure_source
            allure_commons.plugin_manager.register(file_logger)
            config.add_cleanup(cleanup_factory(file_logger))

    @staticmethod
    def pytest_sessionfinish(session):
        """
        测试运行结束后生成allure报告
        """
        reports_path = os.path.join(Config.project_root_dir, "report")
        if _aamt_reports(session.config):
            if _is_master(session.config):  # 只在master节点才生成报告
                # 最近一份报告的历史数据，填充allure趋势图
                if os.path.exists(reports_path):
                    his_reports = os.listdir(reports_path)
                    # 判断 report文件夹下是否有历史报告
                    if his_reports:
                        # 如果有历史报告，就复制报告的历史数据（json文件）
                        latest_report_history = os.path.join(reports_path, "history")
                        # 将历史报告数据复制到新报告的临时文件里
                        shutil.copytree(latest_report_history, os.path.join(allure_source_path, "history"))
                        # 删除历史报告
                        shutil.rmtree(reports_path)

                # html文件 存放路径
                html_report_name = reports_path

                # allure_source_path ： allure源文件临时目录，那一堆json文件，生成HTML报告会删除
                os.system(f"allure generate {allure_source_path} -o {html_report_name}  --clean")
                shutil.rmtree(allure_source_path)

    # @staticmethod
    # def pytest_sessionfinish(session):
    #     """
    #     测试运行结束后生成allure报告
    #     """
    #     reports_path = os.path.join(Config.project_root_dir, "reports")
    #     if _aamt_reports(session.config):
    #         if _is_master(session.config):  # 只在master节点才生成报告
    #             # 最近一份报告的历史数据，填充allure趋势图
    #             if os.path.exists(reports_path):
    #                 his_reports = os.listdir(reports_path)
    #                 if his_reports:
    #                     # print(f'报告目录文件有：{his_reports}')
    #                     # 清除多余的报告，只保留最近的一份报告
    #                     for i in his_reports[:-1]:
    #                         shutil.rmtree(os.path.join(Config.project_root_dir, 'reports', i))
    #                     # print(f'操作只保留最近一份报告目录：{his_reports}')
    #                     latest_report_history = os.path.join(reports_path, his_reports[-1], "history")
    #                     # 复制最近一份报告的记录
    #                     shutil.copytree(latest_report_history, os.path.join(allure_source_path, "history"))
    #                     # 删除最近一份报告的记录，下面会生成新的
    #                     shutil.rmtree(os.path.join(Config.project_root_dir, 'reports', his_reports[-1]))
    #
    #             current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
    #             # html_report_name = os.path.join(reports_path, "report")
    #             html_report_name = os.path.join(reports_path, "report-" + current_time)
    #             os.system(f"allure generate {allure_source_path} -o {html_report_name}  --clean")
    #             shutil.rmtree(allure_source_path)
    #

def aamt_plugins():
    # conftest 加载插件时，从调用堆栈列表里获取信息，再组装成所需路径
    caller = inspect.stack()[1]
    # 保存项目根路径
    Config.project_root_dir = os.path.dirname(caller.filename)
    # 获取所有fixture路径，1、项目下的fixtures；2、aamt下的fixture；
    plugins_path = fixture_paths(root_path=Config.project_root_dir)  # +[其他插件]
    return plugins_path



