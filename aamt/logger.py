# -*- coding: UTF-8 -*-
# @Software: PyCharm
# @File: logger.py
# @Author: xuefeng365
# @E-mail: 120158568@qq.com,
# @Site:
# @Time: 11月 23, 2022


import logging
import os
import time
from functools import wraps

import colorlog

from aamt.config import Config

# logging模块中包含的类
# 用来自定义日志对象的规则（比如：设置日志输出格式、等级等）
# 常用子类：StreamHandler、FileHandler
# StreamHandler 控制台输出日志
# FileHandler 日志输出到文件

# BASE_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# print(BASE_PATH)

# 日志文件路径
LOG_PATH = os.path.join(Config.project_root_dir, "log")
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)


class Logger():

    def __init__(self):
        log_colors_config = {
            'DEBUG': 'white',  # cyan white
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red'}

        # 创建一个logger日志对象
        self.logger = logging.getLogger("log")

        # 创建日志格式(不带颜色)对象
        self.file_formater = logging.Formatter(
            fmt='[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S')

        # 创建颜色格式（(带颜色)）对象
        self.console_formatter = colorlog.ColoredFormatter(
            fmt='%(log_color)s[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S',
            log_colors=log_colors_config)

        # 输出到控制台
        self.console = logging.StreamHandler()
        self.logname = os.path.join(LOG_PATH, "{}.log".format(time.strftime("%Y%m%d")))  # 创建日志路径和时间
        # 输出到文件：获取日志路径，并创建FileHandler对象（）-- 设定写入方式：追加
        self.filelogger = logging.FileHandler(self.logname, mode='a', encoding="UTF-8")

        # 设置默认的日志级别  控制台logger 和 handler以最高级别为准，不同handler之间可以不一样，不相互影响
        self.logger.setLevel(logging.INFO)

        self.console.setLevel(logging.INFO)
        self.filelogger.setLevel(logging.INFO)
        # self.logger.setLevel(logging.INFO)
        # self.logger.setLevel(logging.WARNING)

        # 设置控制台日志的颜色
        self.console.setFormatter(self.console_formatter)
        # 设置文件日志的颜色
        self.filelogger.setFormatter(self.file_formater)

        # 重复日志问题：
        # 1、防止多次addHandler；
        # 2、loggername 保证每次添加的时候不一样；
        # 3、显示完log之后调用removeHandler
        if not self.logger.handlers:
            self.logger.addHandler(self.console)
            self.logger.addHandler(self.filelogger)

        self.console.close()
        self.filelogger.close()


Logger = Logger().logger


def decorate_log(func):
    @wraps(func)
    # Python装饰器中@wraps作用 https://blog.csdn.net/weixin_40576010/article/details/88639686
    def log(*args, **kwargs):
        Logger.info(f'-- 开始执行 {func.__name__} --')
        try:
            func(*args, **kwargs)
        except Exception as e:
            Logger.error(f'-- {func.__name__}执行失败，原因：{e} --')
            raise e
        else:
            Logger.info(f'-- {func.__name__} 执行成功 --')

    return log


# 调试用
@decorate_log
def xuefeng():
    assert 2 == 2


if __name__ == '__main__':
    xuefeng()

    Logger.info("---测试开始---")
    Logger.warning("---测试开始---")
    Logger.error("---测试结束---")
    Logger.debug("---测试结束---")
