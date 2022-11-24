# -*- coding: utf-8 -*-

# @Software: PyCharm
# @File: cli.py
# @Author: xuefeng365
# @E-mail: 120158568@qq.com,
# @Site:
# @Time: 11月 23, 2022


import argparse
import sys

from aamt import __description__, __version__
from aamt.scaffold import init_parser_scaffold, main_scaffold


def main():
    # 命令行处理程序入口
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("-V", "--version", dest="version", action="store_true", help="show version")
    subparsers = parser.add_subparsers(help="sub-command help")
    sub_parser_scaffold = init_parser_scaffold(subparsers)

    if len(sys.argv) == 1:
        # aamt
        parser.print_help()
        sys.exit(0)
    elif len(sys.argv) == 2:
        if sys.argv[1] in ["-V", "--version"]:
            # aamt -V
            # aamt --version
            print(f"{__version__}")
        elif sys.argv[1] in ["-h", "--help"]:
            # aamt -h
            # aamt --help
            parser.print_help()
        elif sys.argv[1] == "startproject":
            # aamt startproject
            sub_parser_scaffold.print_help()
        sys.exit(0)

    args = parser.parse_args()


    if args.version:
        print(f"{__version__}")
        sys.exit(0)

    if sys.argv[1] == "startproject":
        # aamt startproject project_name
        main_scaffold(args)
