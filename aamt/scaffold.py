# -*- coding: utf-8 -*-

# @Software: PyCharm
# @File: scaffold.py
# @Author: xuefeng365
# @E-mail: 120158568@qq.com,
# @Site:
# @Time: 11月 23, 2022

import os
import platform
import sys

from aamt.sample import *
from loguru import logger


class ExtraArgument:
    """命令行附加参数映射"""
    # 是否创建Python虚拟环境
    create_venv = False


def init_parser_scaffold(subparsers):
    """定义参数"""
    sub_parser_scaffold = subparsers.add_parser("startproject", help="Create a new project with template structure.")
    sub_parser_scaffold.add_argument("project_name", type=str, nargs="?", help="Specify new project name.")
    sub_parser_scaffold.add_argument(
        "-venv",
        dest="create_venv",
        action="store_true",
        help="Create virtual environment in the project, and install aamt.",
    )
    return sub_parser_scaffold


def create_scaffold(project_name):
    """ 创建项目脚手架"""
    if os.path.isdir(project_name):
        logger.warning(
            f"Project folder {project_name} exists, please specify a new project name."
        )
        return 1
    elif os.path.isfile(project_name):
        logger.warning(
            f"Project name {project_name} conflicts with existed file, please specify a new one."
        )
        return 1

    logger.info(f"Create new project: {project_name}")
    # os.getcwd() 获取当前目录
    print(f"Project root dir: {os.path.join(os.getcwd(), project_name)}\n")

    # 创建文件夹
    def create_folder(path):
        os.makedirs(path)
        msg = f"Created folder: {path}"
        print(msg)

    # 创建文件
    def create_file(path, file_content=""):
        with open(path, "w", encoding="utf-8") as f:
            f.write(file_content)
        msg = f"Created file:   {path}"
        print(msg)

    create_folder(project_name)

    create_folder(os.path.join(project_name, "api"))
    create_file(os.path.join(project_name, "api", "__init__.py"))
    create_file(os.path.join(project_name, "api", "logintoken.py"), file_content=logintoken_content)
    create_file(os.path.join(project_name, "api", "public_api.py"), file_content=public_api_content)
    create_folder(os.path.join(project_name , "api", "brand"))
    create_file(os.path.join(project_name, "api", "brand", "__init__.py"))
    create_file(os.path.join(project_name, "api", "brand", "brand_controller_api.py"), file_content=brand_controller_api_content)
    create_file(os.path.join(project_name, "api", "brand", "route.py"), file_content=brand_route_content)

    create_folder(os.path.join(project_name, "fixtures"))
    create_file(os.path.join(project_name, "fixtures", "__init__.py"))
    create_file(os.path.join(project_name, "fixtures", "fixture_admin.py"), file_content=fixture_admin_content)
    create_folder(os.path.join(project_name , "fixtures", "xf"))
    create_file(os.path.join(project_name, "fixtures", "xf", "__init__.py"))
    create_file(os.path.join(project_name, "fixtures", "xf", "fixture_xf.py"), file_content=fixture_xf_content)
    create_folder(os.path.join(project_name , "fixtures", "zhangsan"))
    create_file(os.path.join(project_name, "fixtures", "zhangsan", "__init__.py"))
    create_file(os.path.join(project_name, "fixtures", "zhangsan", "fixture_zhangsan.py"), file_content=fixture_zhangsan_content)

    create_folder(os.path.join(project_name, "case"))
    create_file(os.path.join(project_name, "case", "__init__.py"))
    create_file(os.path.join(project_name, "case", "conftest.py"),file_content=conftest_content1)
    create_folder(os.path.join(project_name, "case", "test_brand"))
    create_file(os.path.join(project_name, "case", "test_brand", "test_brand.py"),file_content=test_brand_content)


    create_folder(os.path.join(project_name, "common"))
    create_file(os.path.join(project_name, "common", "__init__.py"))
    create_file(os.path.join(project_name, "common", "assert_api.py"),file_content=assert_api_content)
    create_file(os.path.join(project_name, "common", "mysqlhelper.py"),file_content=mysqlhelper_content)
    create_file(os.path.join(project_name, "common", "emailhelper.py"),file_content=emailhelper_content)
    create_file(os.path.join(project_name, "common", "project.py"),file_content=project_content)

    create_folder(os.path.join(project_name, "data"))
    create_file(os.path.join(project_name, "data", "brand_controller.yaml"),file_content=brand_controller_content)

    create_folder(os.path.join(project_name, "file"))
    create_folder(os.path.join(project_name, "log"))
    create_folder(os.path.join(project_name, "report"))

    create_folder(os.path.join(project_name, "resources"))
    create_file(os.path.join(project_name, "resources", "aamt.ini"),file_content=aamt_ini_content)
    create_folder(os.path.join(project_name, "resources", "env_vars"))
    create_file(os.path.join(project_name, "resources", "env_vars", "env_vars_test.yaml"),file_content=env_vars_test_yaml_content)
    create_file(os.path.join(project_name, "resources", "env_vars", "env_vars_uat.yaml"),file_content=env_vars_uat_yaml_content)

    create_folder(os.path.join(project_name, "until"))
    create_file(os.path.join(project_name, "until", "__init__.py"))
    create_file(os.path.join(project_name, "until", "client.py"), file_content=client_content)
    create_file(os.path.join(project_name, "until", "fake.py"), file_content=fake_content)
    create_file(os.path.join(project_name, "until", "fastapi_mock.py"), file_content=fastapi_mock_content)
    create_file(os.path.join(project_name, "until", "mitm.py"), file_content=mitm_content)
    create_file(os.path.join(project_name, "until", "dao.py"), file_content=dao_conftent)

    create_file(os.path.join(project_name, "main.py"), file_content=main_content)
    create_file(os.path.join(project_name, "pytest.ini"), file_content=pytest_content)
    create_file(os.path.join(project_name, "requirements.txt"), file_content=requirements_content)
    create_file(os.path.join(project_name, "README.md"), file_content=README_content)
    create_file(os.path.join(project_name, "conftest.py"), file_content=conftest_content)
    create_file(os.path.join(project_name, "项目结构说明.txt"), structure_content)
    create_file(os.path.join(project_name, "run.sh"), run_shell_content)




    if ExtraArgument.create_venv:
        # 创建Python虚拟环境
        os.chdir(project_name)
        print("\nCreating virtual environment")
        os.system("python -m venv .venv")
        print("Created virtual environment: .venv")

        # 在Python虚拟环境中安装aat
        print("Installing aamt")
        if platform.system().lower() == 'windows':
            os.chdir(".venv")
            os.chdir("Scripts")
            os.system("pip install aamt")
        elif platform.system().lower() == 'linux':
            os.chdir(".venv")
            os.chdir("bin")
            os.system("pip install aamt")


def main_scaffold(args):
    # 项目脚手架处理程序入口
    ExtraArgument.create_venv = args.create_venv
    sys.exit(create_scaffold(args.project_name))



