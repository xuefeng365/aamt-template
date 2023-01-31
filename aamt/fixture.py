# -*- coding: UTF-8 -*-
# @Software: PyCharm
# @File: fixture.py
# @Author: xuefeng365
# @E-mail: 120158568@qq.com,
# @Site:
# @Time: 11月 23, 2022

import pytest
import json
import os

from filelock import FileLock
from loguru import logger




@pytest.fixture(scope="session")
def aamt_context_manager(tmp_path_factory, worker_id):
    """
    aamt上下文管理器，在xdist分布式执行时，多个session也只执行一次
    参考：https://pytest-xdist.readthedocs.io/en/latest/how-to.html#making-session-scoped-fixtures-execute-only-once
    命令不带-n auto也能正常执行，不受影响
    """

    def inner(produce_expensive_data, *args, **kwargs):
        if worker_id == "master":
            # not executing in with multiple workers, just produce the data and let
            # pytest's fixture caching do its job
            return produce_expensive_data(*args, **kwargs)

        # get the temp directory shared by all workers
        root_tmp_dir = tmp_path_factory.getbasetemp().parent

        fn = root_tmp_dir / "data.json"
        with FileLock(str(fn) + ".lock"):
            if fn.is_file():
                data = json.loads(fn.read_text())
            else:
                data = produce_expensive_data(*args, **kwargs)
                fn.write_text(json.dumps(data))
        return data

    return inner
