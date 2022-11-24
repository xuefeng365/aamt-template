# -*- coding: UTF-8 -*-
# @Software: PyCharm
# @File: dao.py
# @Author: xuefeng365
# @E-mail: 120158568@qq.com,
# @Site:
# @Time: 11月 23, 2022

from aamt.logger import Logger

try:
    from sqlalchemy import create_engine
    from texttable import Texttable
except ModuleNotFoundError:
    pass


def mysql_engine(host, port, user, password, db):
    # sqlalchemy create_engine
    try:
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}")
    except NameError:
        return ""
    return engine


def print_db_table(data_frame):
    """以表格形式打印数据表"""
    tb = Texttable()
    tb.header(data_frame.columns.array)
    tb.set_max_width(0)
    # text * cols
    tb.set_cols_dtype(['t'] * data_frame.shape[1])
    tb.add_rows(data_frame.to_numpy(), header=False)
    Logger.info(tb.draw())
