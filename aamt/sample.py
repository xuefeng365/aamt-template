# -*- coding: utf-8 -*-

# @Software: PyCharm
# @File: sample.py
# @Author: xuefeng365
# @E-mail: 120158568@qq.com,
# @Site:
# @Time: 11月 23, 2022

gitignore_content = """.idea/
.pytest_cache/
.aamt_allure_tmp/
__pycache__/
*.pyc
report/
debug/"""


client_content = """
from mimetypes import MimeTypes

import jmespath
import requests
import json
import allure
from urllib.parse import urlencode
import time

from requests import Response

from common.logger import Logger
from common.config import *
from requests_toolbelt.multipart.encoder import MultipartEncoder
from until.fake import TepVars



class Body_type():
    none = '无类型'
    # 默认
    json = 'json数据'
    form_text = '表单数据 ：纯json数据'
    form_file = '表单数据 ：文件二进制流+json数据'
    binary = '文件直传：文件二进制流'
    graphql = '其他类型'


class HttpClient(Body_type):

    def __init__(self):

        self.session = requests.Session()

        # 变量池实例
        self.aamt_vars = TepVars()
        # 日志实例
        self.logging = Logger

        # 获取当前使用的环境
        self.environ_active = Operate_config().read_environ_active()
        # 获取激活yaml的所有数据
        self.env_vars_data = Read_yaml().get_env_vars_yaml()

        self.host = self.env_vars_data['after_host']

        self.default_header = {
            "Content-Type": "application/json",
            "language": "zh_CN"
        }

    def send(self, url:str='', method='post', body={}, body_type:str=Body_type.json,x_token='', file_key='picFile',file_path='',timeout=30, **kwargs):

        start_time = time.time()

        if not url.startswith(("http://", "https://")):
            raise Exception("请输入正确的url, 记得带上http:// 或者 https:// 哦")

        # 用户传了headers,就用用户的,不传就用默认的
        headers = kwargs.get("headers", self.default_header)

        if x_token:
            headers["_token_"] = x_token.strip('"')  # strip() 方法用于移除字符串头尾指定的字符（默认为空格或换行符）或字符序列。

        if method == "get":
            result = self.session.request(url=url, method=method, params=body, headers=headers,timeout=timeout,**kwargs)

        elif method == "post":
            self.logging.info(f'body_type类型：{body_type}')
            if body_type == Body_type.json:
                headers['Content-Type'] = 'application/json; charset=UTF-8'
                result = self.session.request(url=url, method=method, json=body, headers=headers,timeout=timeout,**kwargs)
            elif body_type == Body_type.form_file:
                filename = file_path.split('\\')[-1]  # xiaoxin.png
                # 通过 mimetypes 来自动识别文件类型 ： https://cloud.tencent.com/developer/section/1369143
                fileType = MimeTypes().guess_type(file_path)[0]
                # 没有识别到就不传 content_type
                if fileType is None:
                    # files = {file_key: ('xiaoxin.png',open(file_path, 'rb'))}
                    files = {'file_key': (filename, open(file_path, 'rb'))}

                    # 也可以用已下的方法，不用加 filename
                    # files = {file_key: open(file_path, 'rb'))}
                    # files = {'file_key': open(file_path, 'rb')}
                else:
                    # files = {file_key: ('xiaoxin.png',open(file_path, 'rb'),'image/png')}
                    files = {file_key: (filename, open(file_path, 'rb'), fileType)}
                body.update(files)
                # 把要传入的数据 转变为form_data格式
                form_data = MultipartEncoder(body)
                # 以下命令自动 转变 headers 中的 Content-Type 为：'multipart/form-data; boundary=。。。。。。。。。。。
                headers['Content-Type'] = form_data.content_type
                # :param data:(可选)字典，元组列表，字节，或文件类对象发送到:class: 'Request'的主体中。
                result = self.session.request(url=url, method=method, data=form_data, headers=headers,timeout=timeout,**kwargs)

            elif body_type == Body_type.form_text:
                # 把要传入的数据 转变为form_data格式
                form_data = MultipartEncoder(body)
                # 以下命令自动 转变 headers 中的 Content-Type 为：'multipart/form-data; boundary=。。。。。。。。。。。
                headers['Content-Type'] = form_data.content_type
                result = self.session.request(url=url, method=method, data=form_data, headers=headers,timeout=timeout,**kwargs)

            elif body_type == Body_type.binary:
                files = {file_key: open(file_path, 'rb')}
                # 文件流通过files 传给request的请求参数files
                result = self.session.request(url=url, method=method, json=body, headers=headers, files=files,timeout=timeout,**kwargs)
            else:
                raise ValueError(f"=====body_type没有定义，{body_type} 请确认====")

        elif method == "patch":
            result = self.session.request(url=url, method=method, data=json.dumps(body), headers=headers, timeout=timeout,**kwargs)

        elif method == "delete":
            result = ''
        elif method == "put":
            result = ''
        else:
            raise ValueError(f"=====大兄弟===暂不支持{method} 请求呢====需要就自己补充吧====")

        end_time = time.time()
        # python 内置函数 保留4位小数
        time_ = round((end_time-start_time), 4)

        # 处理
        result = AamtResponse(result)

        try:
            self.logging.info(f'\n请求日志：\nurl: {url}\nmethod: {method}\nbody: \n{body}\nbody_type: {body_type}\nheaders: \n{headers}\n**********************************************************************************')
            self.logging.debug(f'\n响应日志：\n响应码: {result.status_code}\n请求>响应 时间开销: {time_}\n**********************************************************************************\n')
        except AttributeError:
            self.logging.error(
                f'\n无法获取响应码， 响应日志：\n{result}\n请求>响应 时间开销: {time_}\n**********************************************************************************\n')
        except TypeError:
            self.logging.warning(f'警告：{kwargs}')

        self.__create_request_log(url, method, body, body_type, headers)
        try:
            self.__create_response_log(result.status_code, result.json(),time_)
            return result.json()
        except:
            self.__create_response_log(result.status_code, result.text,time_)
            self.logging.warning(f'\n注意 响应内容：不可以序列化，具体响应如下：\n{result.text}')
            return result.text

    def get_full_url(self, url, etc={}, replace={}, h=""):
        if h:
            host = h.rstrip('/')  # rstrip() 删除 string 字符串末尾的指定字符（默认为空格）.
        else:
            host = self.host.rstrip('/')

        url = url.lstrip('/')  # lstrip() 方法用于截掉字符串左边的空格或指定字符。
        full_url = host + "/" + url
        # full_url += "?"
        full_url += "?platform={}".format(self.environ_active)
        if etc:
            s = urlencode(etc)  # urlencode  urllib库里面有个urlencode函数，可以把key-value这样的键值对转换成我们想要的格式，返回的是a=1&b=2这样的字符串
            full_url += "&" + s
        if replace:
            full_url = full_url.format(replace)  # str.format() 方法通过字符串中的花括号 {} 来识别替换字段 replacement field，从而完成字符串的格式化。
            # full_url = str.format(full_url,replace) #str.format() 方法通过字符串中的花括号 {} 来识别替换字段 replacement field，从而完成字符串的格式化。
        return full_url


    # 目的就是 在allure显示,没什么实际意义
    @allure.step("请求日志")
    def __create_request_log(self, url, method, body, body_type, headers):
        pass

    # 目的就是 在allure显示
    @allure.step('响应日志')
    def __create_response_log(self, status_code, text,time_):
        pass


class AamtResponse(Response):
    # 包装requests.Response，简化jmespath写法
    def __init__(self, response):

        super().__init__()
        for k, v in response.__dict__.items():
            self.__dict__[k] = v

    def jmespath(self, expression):
        return jmespath.search(expression, self.json())


if __name__ == '__main__':

    a = HttpClient()
    a.send(url='http://www.baidu.com',method='get', body={}, body_type=Body_type.json)


"""
public_api_content = """
# -*- coding: utf-8 -*-
# @Software: PyCharm
# @File: public_api.py
# @Author: xuefeng365
# @E-mail: 120158568@qq.com,
# @Site:
# @Time: 5月 05, 2022
import sys
from time import sleep

import allure
import jmespath
from jsonpath import jsonpath

from api.client import HttpClient
from common.config import *
from common.logger import Logger
from common.mysqlhelper import MysqlHelper
from until.fake import fake

sys.path.append("..")


class Public(HttpClient):
    # api = TepVars()

    def __init__(self, token):
        '''
        :param token:  ini 文件里的 字段名，（比如 'systerm_admin_token'）
        '''
        super().__init__()
        # 从配置文件里 读取最新的token文件
        xin_token = Operate_config().read_token(section='Token', key=token)
        self.token = xin_token
        print(f'读取到的最新token:{xin_token}')

    @allure.step('新增全新公司：{name}')
    def add_company(self, name='xuefeng', cid=''):
        '''
        pid: 如果是要建子公司，就填写主公司的 cid，如果是要建全新公司，留空（直接填写name: 全新公司名即可）
        '''
        # 查询公司是否已存在
        company_cid = self.get_company_cid(company_name=name)
        if company_cid:
            print(f'公司 {name} 已存在,公司cid:{company_cid}')
        else:
            print(f'公司 {name} 不存在')
            # 新增
            body = {
                'dto': f'{{"name":"{name}","legalPerson":"","abbreviation":"{name}","address":"","city":"","businessLicense":"","companyType":"Franchisee","introduce":"","note":"","pid":"{cid}","companyContactList":[]}}'}

            url = '/system/newCompanyInfo/add'
            method = 'post'

            url = self.get_full_url(url, h=self.host)
            ret = self.send(url=url, method=method, body=body, body_type=self.form_text, x_token=self.token)
            if jmespath.search('code', ret) == 200:
                print('新增成功')
            elif jmespath.search('code', ret) == 500:
                if '已被注册' in ret['message']:
                    print(ret)
                assert '已被注册' in ret['message'], f'异常，新增模板异常，异常信息；{ret}'

    @allure.step('从数据库查询 公司：{company_name} 对应的cid')
    def get_company_cid(self, company_name='xuefeng'):
        # 从数据库查询 对应的公司id
        mysql = MysqlHelper(self.env_vars_data['DB']['host'], self.env_vars_data['DB']['username'],
                            self.env_vars_data['DB']['password'], self.env_vars_data['DB']['db1'],
                            self.env_vars_data['DB']['port'])
        ret = mysql.get_one(f'SELECT * FROM company_info WHERE name = "{company_name}";')
        # assert ret is not None, f"数据表 {self.env_vars_data['DB']['db1']} 无法查询到，公司 {company_name} 对应的cid"
        if ret:
            company_cid = ret['cid']
            return company_cid
        else:
            print(
                f"{self.env_vars_data['DB']['host']} 环境， 数据表 {self.env_vars_data['DB']['db1']} 无法查询到 公司：{company_name} 对应的cid")

    @allure.step('新增公司模板：{name},并给公司模板分配所有权限')
    def company_template_assign_permissions(self, name='auto_template', resourceList=[]):
        body = {"isDefault": "0", "name": name, "note": "自动化", "resourceList": resourceList}
        url = 'system/resourceTemplate/saveTemplate'
        method = 'post'
        url = self.get_full_url(url, h=self.host)
        ret = self.send(url=url, method=method, body=body, body_type=self.json, x_token=self.token)
        if jmespath.search('code', ret) == 200:
            print(f'公司模板 {name} 新增并分配权限成功')
        elif jmespath.search('code', ret) == 500:
            assert '存在' in ret['message'], f'异常, 新增公司模板 {name} 功能异常，请检查'
        else:
            assert False, f'异常，公司模板分配权限异常，接口响应信息；{ret}'
"""
brand_controller_api_content = """
# -*- coding: UTF-8 -*-
import sys

import jmespath

# from common.config import *
from api.brand.route import *
from api.client import *

sys.path.append("..")


class Brand_ControllerApi(HttpClient):
    ''' 初始化-传入配置文件里的token值 然后调用 依赖token的其他方法 ，比如加购物车 查看下订单等等 '''

    def __init__(self, token):
        '''
        :param token:  ini 文件里的 字段名，（比如 'xuefeng_buyer_token'）
        '''
        super().__init__()
        # 从配置文件里 读取最新的token文件
        self.token = Operate_config().read_token(section='Token', key=token)

    # add品牌
    data0 = brand_controller['add_brand']['case_data'][0]['body']

    @allure.step('新增品牌')
    def add_brand(self, name=data0['name'],
                  note=data0['note'],
                  id=data0['id'],
                  iconFile=data0['iconFile'],
                  pictureUrl=data0['pictureUrl']):

        # 本地绝对路径
        path_iconFile = get_file_path(iconFile)

        body = {"name": name,
                "note": note,
                "id": id,
                "iconFile": iconFile,
                "pictureUrl": pictureUrl}

        url = brand_controller['add_brand']['url']
        method = brand_controller['add_brand']['method']
        url = self.get_full_url(url, h=self.host)

        ret = self.send(url=url, method=method, body=body, body_type=Body_type.form_file, file_key='iconFile',
                        file_path=path_iconFile, x_token=self.token)

        # assert jmespath.search('code', ret) == 200, f'异常，新增品牌 接口响应信息：{ret}'
        return ret

    @allure.step('查询品牌列表')
    # 查询品牌列表
    def brand_list(self, brand_name=''):

        body = {"name": brand_name, "pageIndex": 1, "pageSize": 100, "useToSelect": "1"}
        url = '/upc/productBrand/page'
        method = 'post'
        url = self.get_full_url(url, h=self.host)
        ret = self.send(url, method=method, body=body, body_type=Body_type.json, x_token=self.token)

        class Clazz:
            # 品牌id
            a = jmespath.search(f"result.records[?name== '{brand_name}'].id|[0]", ret)
            # a = jmespath.search('result.records[0].id', ret)
            id = a if a else ''
            print(f'品牌:{brand_name} 对应的id是：{id}')

        return Clazz

    data0 = brand_controller['del_brand']['case_data'][0]['body']

    @allure.step('删除品牌')
    def del_brand(self, brand_name='自动化add品牌'):
        id = self.brand_list(brand_name=brand_name).id

        if id:

            # print(f'所有品牌列表：{list} \n取第一个品牌id:{id}')
            url = brand_controller['del_brand']['url']
            method = brand_controller['del_brand']['method']
            body = {}
            url = self.get_full_url(url, replace=id, h=self.host)

            ret = self.send(url=url, method=method, body=body, body_type=Body_type.json, x_token=self.token)
            assert jmespath.search('code', ret) == 200, f'异常，删除品牌 接口响应信息：{ret}'
        else:

            print(f'品牌：{brand_name} 不存在')
"""
brand_route_content = """
from common.config import *

"后台品牌接口路径（前台）"
brand_controller = Read_yaml().get_test_yaml(filepath="/brand/brand_controller.yaml")

"""
conftest_content = """
# -*- coding: UTF-8 -*-
import sys

import pytest

from common.public_api import Public

sys.path.append("..")

from common.logintoken import Login_after

# 导入token Environ env
from common.config import *
from common.public_api import get_authority_id


@pytest.fixture(scope='session')
def env_vars_data():
    result = Read_yaml().get_env_vars_yaml()
    return result


# --------------- 怡和 超级管理员管理后台 登录及其数据初始化 开始 -----------
@pytest.fixture(scope="session")
# def systerm_admin_login(user_info=env_vars_data['systerm']):
def systerm_admin_login(env_vars_data):
    print('超管登录')
    Login_after(env_vars_data['systerm'], 'systerm_admin_token')


# @pytest.fixture(scope="session", autouse=True)
@pytest.fixture(scope="session")
def init_admin(systerm_admin_login):
    # -------- 调用公共方法 新建基础数据（不需要返回值）  ---------
    print('调用公共方法 新建基础数据（不需要返回值）')
    pub_d = Public(token='systerm_admin_token')
    print('-+-+-+', env_vars_data['systerm'])

    # 医生基础数据
    warehouse_names = [f"{env_vars_data['systerm']['account']}仓库1", f"{env_vars_data['systerm']['account']}仓库2"]
    warehouse_types = ['自有仓库', '店铺自有']
    shelve_type1 = '入库区'
    shelve_type2 = '出库区'
    shelve_type3 = '普通区'

    for warehouse_name in warehouse_names:
        for warehouse_type in warehouse_types:
            pub_d.add_warehouse(name=warehouse_name, type=warehouse_type)

            pub_d.add_shelves(warehouse_name=warehouse_name, name=f'{warehouse_name}_{shelve_type1}', type=shelve_type1)
            pub_d.add_shelves(warehouse_name=warehouse_name, name=f'{warehouse_name}_{shelve_type2}', type=shelve_type2)
            pub_d.add_shelves(warehouse_name=warehouse_name, name=f'{warehouse_name}_{shelve_type3}', type=shelve_type3)

    # 新增分类-已默认3个分类
    pub_d.add_classification()

    brand_name = 'auto品牌1'
    commodity_upcs = [('111111229980', '主产品'), ('222222447863', '主产品'), ('888888861827', '非升级配件'),
                      ('999999435729', '升级配件')]

    # 新增品牌
    pub_d.add_brand(name=brand_name)
    # 新增upc
    for commodity_upc in commodity_upcs:
        pub_d.add_commodity(brand_name=brand_name, upcCode=commodity_upc[0], name='auto', types_name=commodity_upc[1])

    template_role = ['auto_template', 'auto_role']
    companys = [
        ('怡和（不删）', ['521']),
        ('xuefeng', ['5200', '5201']),
        ('xuefeng2', ['5300', '5400'])
    ]

    # -------- 怡和 账号，新增公司、新增模板（分配全部权限）、新增角色（分配权限） 、新增用户（分配角色） ----------
    for company in companys:
        pub_d.add_company(name=company[0])

    # 新增模板，给模板分配全部权限
    resourceList = get_authority_id()
    pub_d.company_template_assign_permissions(name=template_role[0], resourceList=resourceList)

    # 公司分配模板
    for company in companys:
        if company != '怡和（不删）':
            pub_d.assign_templates_to_companies(company_name=company[0], template_name=template_role[0])
        else:
            print('怡和主体 请自行分配模板，脚本跳过')

    # 每个公司下 新建角色 并 给角色分配权限
    for company in companys:
        pub_d.add_role(company_name=company[0], role_name=template_role[1], cid=222260, resourses=resourceList)
    # 每个公司下 新建用户 并 给用户分配权限
    for company in companys:
        for account in company[1]:
            pub_d.add_user(company_name=company[0], account=account, password=account, firstName='脚本', lastName='新增',
                           role_name=template_role[1])

    # -------- 新增公司、新增模板（分配全部权限）、新增角色（分配权限） 、新增用户（分配角色） ----------

    # # 给521分配仓库权限
    # pub_d.assign_warehouse_permissions_to_users(account='521', warehouse_name='auto仓库')

    # # ------------ 线下采购基础数据 -----------
    # # 新增下线采购供应商 和 银行卡信息
    # pub_d.add_Offline_purchasing_suppliers(suppliers='xuefeng线下采购')

    yield pub_d


# --------------- 怡和 超级管理员管理后台 登录及其数据初始化 结束 -----------


# --------------- xuefeng 医生1 登录及其数据初始化 开始 -----------
@pytest.fixture(scope="session")
def login_doctor1(env_vars_data):
    print('xuefeng_doctor1 登录')
    Login_after(env_vars_data['xuefeng_doctor1'], 'xuefeng_doctor1_token')


@pytest.fixture(scope="session", autouse=True)
# @pytest.fixture(scope="session")
def init_doctor1(login_doctor1):
    # -------- 调用公共方法 新建基础数据（不需要返回值）  ---------
    print('调用公共方法 新建基础数据（不需要返回值）')
    pub_d = Public(token='xuefeng_doctor1_token')
    # 医生基础数据

    warehouse_names = ['xuefeng_doctor1仓库1', 'xuefeng_doctor1仓库2']
    warehouse_types = ['自有仓库', '店铺自有']
    shelve_type1 = '入库区'
    shelve_type2 = '出库区'
    shelve_type3 = '普通区'

    for warehouse_name in warehouse_names:
        for warehouse_type in warehouse_types:
            pub_d.add_warehouse(name=warehouse_name, type=warehouse_type)

            pub_d.add_shelves(warehouse_name=warehouse_name, name=f'{warehouse_name}_{shelve_type1}', type=shelve_type1)
            pub_d.add_shelves(warehouse_name=warehouse_name, name=f'{warehouse_name}_{shelve_type2}', type=shelve_type2)
            pub_d.add_shelves(warehouse_name=warehouse_name, name=f'{warehouse_name}_{shelve_type3}', type=shelve_type3)

    brand_name = 'auto品牌1'
    commodity_upcs = [('111111229980', '主产品'), ('222222447863', '主产品'), ('888888861827', '非升级配件'),
                      ('999999435729', '升级配件')]

    skus = [('auto1_sku_00001', '全新', '111111229980'), ('auto1_sku_00002', '全新', '111111229980'),
            ('auto1_sku_00003', '全新', '111111229980'),
            ('auto2_sku_00001', '全新', '222222447863'), ('auto2_sku_00002', '全新', '222222447863'),
            ('auto2_sku_00003', '全新', '222222447863'),
            ('auto_sku_peijian_00001', '全新', '888888861827'),
            ('auto_sku_peijian_shengji_00001', '全新', '999999435729')]

    for commodity_upc in commodity_upcs:
        pub_d.add_commodity(brand_name=brand_name, upcCode=commodity_upc[0], name='auto', types_name=commodity_upc[1])

    for sku in skus:
        pub_d.add_sku(skuCode=sku[0], newOld=sku[1], upcCode=sku[2], manager='52005200')

    # # ------------ 线下采购基础数据 -----------
    # # 新增下线采购供应商 和 银行卡信息
    # pub_d.add_Offline_purchasing_suppliers(suppliers='xuefeng线下采购')

    yield pub_d


# --------------- xuefeng 医生1 登录及其数据初始化 结束 -----------


# --------------- xuefeng 医生2 登录及其数据初始化 开始 -----------
@pytest.fixture(scope="session")
def login_doctor2(env_vars_data):
    print('xuefeng_doctor2 登录')
    Login_after(env_vars_data['xuefeng_doctor2'], 'xuefeng_doctor2_token')


# @pytest.fixture(scope="session", autouse=True)
@pytest.fixture(scope="session")
def init_doctor2(login_doctor2):
    # -------- 调用公共方法 新建基础数据（不需要返回值）  ---------
    print('调用公共方法 新建基础数据（不需要返回值）')
    pub_d = Public(token='xuefeng_doctor2_token')

    yield pub_d


# --------------- xuefeng 医生2 登录及其数据初始化 结束 -----------


# --------------- xuefeng2 护士1 登录及其数据初始化 开始 -----------
@pytest.fixture(scope="session")
def login_nurse1(env_vars_data):
    print('xuefeng2_nurse1 登录')
    Login_after(env_vars_data['xuefeng2_nurse1'], 'xuefeng2_nurse1_token')


# 返回值-护士身份- 增加基础数据 返回公共方法实例
# @pytest.fixture(scope="session", autouse=True)
@pytest.fixture(scope="session")
def init_nurse1(login_nurse1):
    # -------- 调用公共方法 新建基础数据（不需要返回值）  ---------
    print('调用公共方法 新建基础数据（不需要返回值）')
    pub_n = Public(token='xuefeng2_nurse1_token')

    # # 护士基础数据
    # pub_n.add_warehouse(name='auto护士仓库', type='护士仓库')
    #
    # pub_n.add_shelves(warehouse_name='auto护士仓库',name='auto护士入库区1', type='入库区')
    # pub_n.add_shelves(warehouse_name='auto护士仓库',name='auto护士出库区1', type='出库区')
    # pub_n.add_shelves(warehouse_name='auto护士仓库',name='auto护士破损区1', type='破损区')
    #
    # # 给5201分配仓库权限
    # pub_n.assign_warehouse_permissions_to_users(account='5201', warehouse_name='auto护士仓库')
    #
    #
    # # 期货护士绑定采购商
    # pub_n.bind_buyers(codeOrName=pub_n.get_company_cid(company_name='怡和（不删）'))
    # # 期货护士添加支付方式--如果有自动化新增的支付方式，就跳过
    # pub_n.nurse_add_payment_method()
    # # 现货--个人中心新增一个地址
    # pub_n.center_self_add_address()

    yield pub_n


# --------------- xuefeng2 护士1 登录及其数据初始化 结束 -----------


# --------------- xuefeng2 护士2 登录及其数据初始化 开始 -----------
@pytest.fixture(scope="session")
def login_nurse2(env_vars_data):
    print('xuefeng2_nurse2 登录')
    Login_after(env_vars_data['xuefeng2_nurse2'], 'xuefeng2_nurse2_token')


# 返回值-护士身份- 增加基础数据 返回公共方法实例
# @pytest.fixture(scope="session", autouse=True)
@pytest.fixture(scope="session")
def init_nurse2(login_nurse2):
    # -------- 调用公共方法 新建基础数据（不需要返回值）  ---------
    print('调用公共方法 新建基础数据（不需要返回值）')
    pub_n = Public(token='xuefeng2_nurse2_token')

    yield pub_n


# --------------- xuefeng2 护士2 登录及其数据初始化 结束 -----------


# --------------- guangzhou 医生1 登录及其数据初始化 开始 -----------

@pytest.fixture(scope="session")
def login_doctor1_gz(env_vars_data):
    Login_after(env_vars_data['gz_doctor1'], 'gz_doctor1_token')


# @pytest.fixture(scope="session", autouse=True)
@pytest.fixture(scope="session")
def init_d(login_doctor1_gz):
    # -------- 调用公共方法 新建基础数据（不需要返回值）  ---------
    print('调用公共方法 新建基础数据（不需要返回值）')
    pub_d = Public(token='gz_doctor1_token')

    yield pub_d

# --------------- guangzhou 医生1 登录及其数据初始化 结束 -----------


"""
test_brand_content = """
# -*- coding: UTF-8 -*-
import sys

import allure
import pytest

from api.brand.brand_controller_api import Brand_ControllerApi
from api.brand.route import *
from common.assert_api import assert_api

sys.path.append("..")


# 后台身份会话
@pytest.fixture(scope="session")
def xuefeng_brand_controller():
    return Brand_ControllerApi("gz_doctor1_token")


# 数据清理 -- 接口
@pytest.fixture()  # 函数级别
def del_brand(xuefeng_brand_controller):
    # xuefeng_brand_controller.del_brand()
    yield
    # 清楚自动化品牌数据
    xuefeng_brand_controller.del_brand()


data = brand_controller['add_brand']['case_data']


@allure.feature('测试品牌模块')
@allure.story('增加品牌功能')
# @pytest.mark.smoke
# @pytest.mark.skip
class Test_add_brand1():

    @pytest.mark.parametrize("case_data", data, ids=[data[i]['case_name'] for i in range(len(data))])  # 参数化测试用例
    def test_add_brand(self, case_data, xuefeng_brand_controller, del_brand):
        allure.dynamic.title(f'title：{case_data["case_name"]}')
        case_body = case_data['body']

        ret = xuefeng_brand_controller.add_brand(name=case_body['name'],
                                                 note=case_body['note'],
                                                 id=case_body['id'],
                                                 iconFile=case_body['iconFile'],
                                                 pictureUrl=case_body['pictureUrl']
                                                 )

        assert_api(ret, expect_data=case_data["expect"])


data = brand_controller['del_brand']['case_data']


@allure.feature('测试品牌模块')
@allure.story('删除品牌功能')
# @pytest.mark.smoke
# @pytest.mark.skip
class Test_del_brand1():

    @pytest.mark.parametrize("case_data", data, ids=[data[i]['case_name'] for i in range(len(data))])  # 参数化测试用例
    def test_add_brand(self, case_data, xuefeng_brand_controller):
        allure.dynamic.title(f'title：{case_data["case_name"]}')
        case_body = case_data['body']

        ret = xuefeng_brand_controller.del_brand(brand_name=case_body['name'])
        assert ret and ret['message'] == 'success', f'删除品牌失败，请检查删除功能是否异常 或者 要删除的品牌：{case_body["name"]} 是否存在'


def test1():
    pass


if __name__ == "__main__":
    pytest.main(['-m', __file__])
    # pytest.main(['-m smoke',__file__])

"""
assert_api_content = """

from common.logger import *

# @decorate_log
def assert_api(actual_data,expect_data):
    '''

    :param actual_data: 实际响应
    :param expect_data: 预期
    :return:
    '''

    try:
        a = expect_data
        b = actual_data
        for i, j in a.items():
            if i in b.keys():
                assert j == b[i],f'断言失败 >  预期的值：{j} （{type(j)}） ！= 实际的值：{b[i]} （{type(b[i])}）'
    except AssertionError as e:
        # 将异常抛出
        raise e

"""
config_content = """
# -*- coding: UTF-8 -*-
import configparser
import os

import yaml


class Config():
    # 全局项目根目录
    project_root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


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


# 获取配置文件中的key值 (token值)
systerm_admin_token = Operate_config().read_token(key='systerm_admin_token')
xuefeng2_doctor1_token = Operate_config().read_token(key='xuefeng_doctor1_token')
xuefeng2_doctor2_token = Operate_config().read_token(key='xuefeng_doctor2_token')
xuefeng_nurse1_token = Operate_config().read_token(key='xuefeng2_nurse1_token')
xuefeng_nurse2_token = Operate_config().read_token(key='xuefeng2_nurse2_token')

gz_doctor1_token = Operate_config().read_token(key='gz_doctor1_token')
gz_nurse1_token = Operate_config().read_token(key='gz_nurse1_token')


"""
logger_content = """
import logging
import os
import time
from functools import wraps

import colorlog

from common.config import Config

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

"""
logintoken_content = """
# -*- coding: utf-8 -*-

import hashlib

import jmespath

from api.client import HttpClient
from common.config import *


# ***********  前端登录  ***********

class Login(HttpClient):
    ''' 初始化登录-- 定义token（coolie 或者 session）字段：目的为了鉴权，并将其写入配置文件'''

    def __init__(self, user_info, token):
        super().__init__()  # 继承上个类的ini
        self.username = user_info['userEmail']
        self.password = user_info['userPassword']
        result = self.login_front(username=self.username, password=self.password)
        assert result['code'] == 200, "前台登录失败"
        self.token = result['result']['token']
        print(f'======自动运行：先获取 前台{token}========: {self.token}')

        # 把token值写入配置文件中
        Operate_config().write(section="Token", key=token, value=self.token)

    def login_front(self, username, password):
        body = {
            "userEmail": username,
            "userPassword": password
        }
        url = '/internet/user/login'
        method = 'post'
        url = super().get_full_url(url, h=self.env_vars_data['front_host'])
        return super().send(url=url, method=method, body=body, body_type=self.json)


# **********************************


# ***********  后台登录  ***********

class Login_after(HttpClient):

    def __init__(self, user_info, token):
        # 传入token（coolie 或者 session）字段：目的为了写入配置文件
        super().__init__()  # 继承上个类的ini
        self.username = user_info['account']

        # ----------- 密码进行MD5加密 ------------ #
        mima = str(user_info['password'])
        # md5加密对象
        md5 = hashlib.md5()
        # 填入要加密的字符串
        md5.update(mima.encode('utf-8'))
        # 转化为16进制字符串
        new_mima = md5.hexdigest()

        # ----------- MD5加密结束 ------------ #

        self.password = new_mima

        result = self.login_after(username=self.username, password=self.password)
        assert jmespath.search('code', result) == 200, f"系统管理登录失败,接口响应 \n {result}\n"
        self.token = result['result']['token']
        print(f'======自动运行：先获取 后台token========: {self.token}')
        # 把token值写入配置文件中
        Operate_config().write(section="Token", key=token, value=self.token)

    def login_after(self, username, password):
        etc = {
            "account": username
            , "password": password
        }
        url = '/system/userInfo/login'
        method = 'get'
        url = super().get_full_url(url, etc=etc, h=self.env_vars_data['after_host'])
        return super().send(url=url, method=method)

# ***********************************

"""
mysqlhelper_content = """
import json
from datetime import datetime
from typing import Union

import pymysql


class MysqlHelper(object):

    def __init__(self, host, username, password, database, port=3306, charset="utf8mb4"):
        # 初始化数据库连接，并指定查询的结果集以字典形式返回
        # self.connection = pymysql.connect()
        self.connection = pymysql.connect(host=host,
                                          user=username,
                                          password=password,
                                          db=database,
                                          port=port,
                                          charset=charset,
                                          cursorclass=pymysql.cursors.DictCursor
                                          )
        # 创建游标
        self.cursor = self.connection.cursor()

    # 关闭数据库连接
    def close(self):
        self.cursor.close()
        self.connection.close()

    # 查询一条记录
    def get_one(self, sql, params=()):
        ret = None
        try:
            # 执行 游标下的 sql语句
            self.cursor.execute(sql, params)
            # 返回游标下 查询结果 fetchone() 一条结果 ；fetchall(),返回一个list，里面有多条，数据 ，每一条是一个元组
            ret = self.cursor.fetchone()

            # 使用commit解决查询数据出现概率查错问题
            self.connection.commit()

            # print(ret)
            return self.verify(ret)

        except Exception as e:
            print(e)
        return ret

    # 查询所有记录
    def get_all(self, sql, params=()):
        list_data = None
        try:
            self.cursor.execute(sql, params)
            # 返回游标下 查询结果 fetchone() 一条结果 ；fetchall(),返回一个list，里面有多条，数据 ，每一条是一个元组
            list_data = self.cursor.fetchall()

            # 使用commit解决查询数据出现概率查错问题
            self.connection.commit()
            return self.verify(list_data)

        except Exception as e:
            pass
            # print(e)
        return list_data

    def verify(self, result: dict) -> Union[dict, None]:
        # 验证结果能否被json.dumps序列化
        # 尝试变成字符串，解决datetime 无法被json 序列化问题
        try:
            json.dumps(result)
        except TypeError:  # TypeError: Object of type datetime is not JSON serializable
            for k, v in result.items():
                if isinstance(v, datetime):
                    result[k] = str(v)
        return result

    # 魔法函数
    def __edit(self, sql, params):
        count = 0
        try:
            count = self.cursor.execute(sql, params)
            # 提交
            self.connection.commit()
            # self.close()
        except Exception as e:
            print(e)
        return count

    # 插入
    def insert(self, sql, params=()):
        return self.__edit(sql, params)

    # 修改
    def update(self, sql, params=()):
        return self.__edit(sql, params)

    # 删除
    def delete(self, sql, params=()):
        return self.__edit(sql, params)


if __name__ == '__main__':
    mysql = MysqlHelper('192.168.X.X', 'root', 'XXXX', 'test2', port=3306)
    # # 删除一条数据

    # 查询一条数据
    sql2 = "select * from `user_info` where `account` = '640'"
    print('查询一条数据是：', mysql.get_one(sql2))
    print('查询多条数据是：', mysql.get_all(sql2))
    mysql.close()

"""
brand_controller_content = """
add_brand:
  title: 新增品牌
  url: /upc/productBrand/save
  method: post
  case_data:
  - case_name: case1_后台新增品牌，必填参数全部正确入参，新增成功
    body: {"name":"自动化add品牌",
           "note":"自动化新建",
           "id":"",
           "iconFile":"apple.png",
           "pictureUrl":""}

    expect: {"code":200,"message":"success"}

  - case_name: case1_后台新增品牌，必填参数全部正确入参，新增成功
    body: {"name":"",
           "note":"自动化新建",
           "id":"",
           "iconFile":"apple.png",
           "pictureUrl":""}

    expect: {"code":500}


del_brand:
  title: 删除品牌
  url: /upc/productBrand/delete/{}
  method: post
  case_data:
  - case_name: case1_传入正确品牌id,删除品牌，成功
    body: {"name":"自动化add品牌"}
    expect: {'code': 200, 'message': 'success'}
"""
aamt_content = """
[Token]
systerm_admin_token = eH-nczOHaPLWo4m9Lnk
xuefeng_doctor1_token = eyJ0eXAiOiJKV1QiLCJhbGciOiJ
xuefeng_doctor2_token = i1E_qtuYK7XAcTE
xuefeng2_nurse1_token = eCjn45Ac_6NVKFbVkE
xuefeng2_nurse2_token = 4Jft40hbVkE
gz_doctor1_token = HmFAzQdwgl9gA
gz_nurse1_token = 451515151515

[Environ]
active = test
"""
env_vars_test_yaml_content = """
#数据库
DB:
  host: 192.168.XX.XX
  port: 3300

  username: XXXXX
  password: XXXXX
  db: wholesale

# 后台域名
after_host: http://192.168.XX.XX


#怡和 超级管理员（新建用户、授权用）
systerm:
  account: 520
  password: 520

# ------------  xuefeng 账号数据 开始 ----------
# xuefeng主体, 医生1
xuefeng_doctor1:
  account: 5200
  password: 5200


# xuefeng主体, 医生2
xuefeng_doctor2:
  account: 5201
  password: 5201


# xuefeng2 主体，护士1
xuefeng2_nurse1:
  account: 5300
  password: 5300

# xuefeng 主体，护士2
xuefeng2_nurse2:
  account: 5400
  password: 5400
# ------------  xuefeng 账号数据 结束 ----------



# ------------  guangzhou 账号数据 开始 ----------
# guangzhou主体, 医生1
gz_doctor1:
  account: gz01
  password: gz01


# guangzhou1 主体, 护士1
gz_nurse1:
  account: gz10
  password: gz10

# ------------  guangzhou 账号数据 结束 ----------

"""
env_vars_uat_yaml_content = """
#数据库
DB:
  host: 192.168.XX.XX
  port: 3300

  username: XXXXX
  password: XXXXX
  db: wholesale

# 后台域名
after_host: http://192.168.XX.XX


#怡和 超级管理员（新建用户、授权用）
systerm:
  account: 520
  password: 520

# ------------  xuefeng 账号数据 开始 ----------
# xuefeng主体, 医生1
xuefeng_doctor1:
  account: 5200
  password: 5200


# xuefeng主体, 医生2
xuefeng_doctor2:
  account: 5201
  password: 5201


# xuefeng2 主体，护士1
xuefeng2_nurse1:
  account: 5300
  password: 5300

# xuefeng 主体，护士2
xuefeng2_nurse2:
  account: 5400
  password: 5400
# ------------  xuefeng 账号数据 结束 ----------



# ------------  guangzhou 账号数据 开始 ----------
# guangzhou主体, 医生1
gz_doctor1:
  account: gz01
  password: gz01


# guangzhou1 主体, 护士1
gz_nurse1:
  account: gz10
  password: gz10

# ------------  guangzhou 账号数据 结束 ----------

"""
clear_results_content = """
import os
import shutil

# shutil.rmtree( src )   #递归删除一个目录以及目录内的所有内容
# os.makedirs() 方法用于递归创建目录。
    # 解决allure报告缓存和Jenkins无文件报错


def clear_allure():
    filepath = (os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + "/report/allure-results/")
    if os.path.exists(filepath):
        shutil.rmtree("{}".format(filepath))
        os.makedirs("{}".format(filepath))
    else:
        os.makedirs("{}".format(filepath))
    path_report = (os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + "/report/allure-report")
    if os.path.exists(path_report):
        shutil.rmtree("{}".format(path_report))


if __name__ == '__main__':
    print(os.path.abspath(os.path.dirname(__file__)) + "/report/allure-results/")
"""
fake_content = """
from faker import Faker

from common.logger import Logger

fake = Faker("zh_CN")


class Faker_:
    def __init__(self):
        self.fake = Faker("zh_CN")
        # 选择中文

    def get_phone_number(self):
        return self.fake.phone_number()

    def get_name(self):
        return self.fake.name()

    def get_email(self):
        return self.fake.email()

    def md5(self):
        return self.fake.md5()


class TepVars:
    # 全局变量池

    def __init__(self):
        self.vars_ = {'a': '初始值'}

    def put(self, key, value):
        self.vars_[key] = value
        Logger.info(f'变量池 成功新增：{{{key}：{value}}}')

    def get(self, key):
        value = ""
        try:
            value = self.vars_[key]
        except KeyError:
            Logger.error(f'异常：获取 {key} 失败, 当前变量池：{self.vars_}')
        return value


if __name__ == "__main__":
    test = Faker_()
    print(test.get_name())
    print(test.get_phone_number())
    print(test.get_email())

    print('年月日：', fake.date(pattern=' %Y-%m-%d'))

    print('随机年份：', fake.year)

    print('随机年份：', fake.year)

    print('随机月份：', fake.month)

    print('随机几号：', fake.day_of_month)

    print('随机星期数：', fake.day_of_week)

    print('时间：', fake.time(pattern='%H:%M:%S'))

    # -30y是过去30年前为开始日期，end_date表示结束到今天

    print('过去某一天：', fake.date_between(start_date="-30y", end_date="today"))

    print('今天：', fake.date_between_dates)  # 今天

    print('日期和时间：', fake.date_time)  # 2021-05-14 19:36:00

    print('当前日期时间：', fake.date_time_between_dates)

    # print('某个区间内随机日期时 间：', fake.date_time_between_dates(datetime_start=datetime(1999, 2, 2, 10, 30, 20), dat
    # etime_end = datetime(2000, 2, 2, 10, 30, 20)))

    print('未来的日期：', fake.future_date(end_date="+30d"), str(fake.future_date(end_date="+30d")))

    print('未来的日期时间：', fake.future_datetime(end_date="+30d"),
          f'类型是：{type(fake.future_datetime(end_date="+30d"))}')  # 未来日期和时间)

    print('过去的日期：', fake.past_date(start_date="-30m"))  # 过去日期

    print('过去的日期时间：', fake.past_datetime(start_date="-30d"))  # 过去日期和时间

    print('时间戳：', fake.unix_time(), f'类型是：{type(fake.unix_time())}')
    print('时间戳：', fake.time(), f'类型是：{type(fake.time())}')
    print('随机md5：', fake.md5(), f'类型是：{type(fake.md5())}')

"""

main_content = """
# -*- coding: UTF-8 -*-
import os

import pytest

from common.logger import Logger
from until.clear_results import clear_allure

if __name__ == '__main__':
    Logger.info("Starting.........  走起 ......")

    # 解决allure报告缓存和Jenkins无文件报错

    clear_allure()
    # pytest.main(['-m','smoke'])
    # pytest.main(["-s",'--workers=1', '--tests-per-worker=4'])
    # # --workers=n：多进程运行需要加此参数， n是进程数。默认为1
    # 　　--tests-per-worker=n：多线程需要添加此参数，n是线程数
    # 　　如果两个参数都配置了，就是进程并行，每个进程最多n个线程，总线程数：进程数*线程数
    # 注意：pytest-parallel支持python3.6及以上版本，如果是想做多进程并发的需要在linux平台或mac上做，windows上不起作用即(workers永远=1)，如果是做多线程的Linux/Mac/Windows平台都支持，进程数为workers设置的值。

    pytest.main()
    # 测试报告本地静态数据生成--allure generate ./allure-xml -o ./allure-result
    os.system(r"allure generate ./report/allure-results -o ./report/allure-report --clean")
    # port = randint(1000, 9999)
    # os.system('allure open ./report/allure-report --port {}'.format(port))  # 打开报告

# 失败重试
# • 测试失败后要重新运行n次，要在重新运行之间添加延迟时 间，间隔n秒再运行。
# • 执行:
# • 安装:pip install pytest-rerunfailures
# • pytest -v - -reruns 5 --reruns-delay 1 —每次等1秒 重试5次


# 在windows下想用多进程的选pytest-xdist； 想用多线程的选pytest-parallel

"""
pytest_content = """
[pytest]
;addopts = -sq --strict -m smoke --alluredir ./report/allure-results

;addopts = -sq --reruns 0 --reruns-delay 1 --alluredir ./report/allure-results

;addopts = -sq --workers 1 --tests-per-worker 1 --alluredir ./report/allure-results

;addopts = -sq --workers 1 --tests-per-worker 1 --reruns 3 --reruns-delay 1 --alluredir ./report/allure-results

addopts = -sq --alluredir ./report/allure-results
testpaths = ./case

;python_files = test_order.py
;python_files = test_brand.py
;python_files = test_*.py
;python_classes = Test*
;python_functions = test_*

markers =
    smoke:0
    test:1

"""
requirements_content = """
allure-pytest==2.11.1
allure-python-commons==2.11.1
attrs==22.1.0
certifi==2022.9.24
charset-normalizer==2.1.1
colorama==0.4.6
colorlog==6.7.0
et-xmlfile==1.1.0
exceptiongroup==1.0.0
execnet==1.9.0
Faker==15.1.1
idna==3.4
iniconfig==1.1.1
jmespath==1.0.1
jsonpath==0.82
openpyxl==3.0.10
packaging==21.3
pluggy==1.0.0
pycodestyle==2.9.1
PyMySQL==1.0.2
pyparsing==3.0.9
pytest==7.2.0
pytest-rerunfailures==10.2
pytest-xdist==3.0.2
python-dateutil==2.8.2
PyYAML==6.0
requests==2.28.1
requests-toolbelt==0.10.1
six==1.16.0
tomli==2.0.1
urllib3==1.26.12
win32-setctime==1.1.0

"""
Markdown_content = """
# 待补充
"""

fastapi_mock_content = """#!/usr/bin/python
# encoding=utf-8

import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/login")
async def login(req: Request):
    body = await req.json()
    if body["username"] == "dongfanger" and body["password"] == "123456":
        return {"token": "de2e3ffu29"}
    return ""


@app.get("/searchSku")
def search_sku(req: Request):
    if req.headers.get("token") == "de2e3ffu29" and req.query_params.get("skuName") == "电子书":
        return {"skuId": "222", "price": "2.3"}
    return ""


@app.post("/addCart")
async def add_cart(req: Request):
    body = await req.json()
    if req.headers.get("token") == "de2e3ffu29" and body["skuId"] == "222":
        return {"skuId": "222", "price": "2.3", "skuNum": "3", "totalPrice": "6.9"}
    return ""


@app.post("/order")
async def order(req: Request):
    body = await req.json()
    if req.headers.get("token") == "de2e3ffu29" and body["skuId"] == "222":
        return {"orderId": "333"}
    return ""


@app.post("/pay")
async def pay(req: Request):
    body = await req.json()
    if req.headers.get("token") == "de2e3ffu29" and body["orderId"] == "333":
        return {"success": "true"}
    return ""


if __name__ == '__main__':
    uvicorn.run("fastapi_mock:app", host="127.0.0.1", port=5000)
"""

mitm_content = """#!/usr/bin/python
# encoding=utf-8

# mitmproxy录制流量自动生成用例

import os
import time

from mitmproxy import ctx

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tests_dir = os.path.join(project_dir, "tests")
# tests/mitm
mitm_dir = os.path.join(tests_dir, "mitm")
if not os.path.exists(mitm_dir):
    os.mkdir(mitm_dir)
# 当前时间作为文件名
filename = f'test_{time.strftime("%Y%m%d_%H%M%S", time.localtime())}.py'
case_file = os.path.join(mitm_dir, filename)
# 生成用例文件
template = \"\"\"import allure
from tep.client import request


@allure.title("")
def test(env_vars):
\"\"\"
if not os.path.exists(case_file):
    with open(case_file, "w", encoding="utf8") as fw:
        fw.write(template)


class Record:
    def __init__(self, domains):
        self.domains = domains

    def response(self, flow):
        if self.match(flow.request.url):
            # method
            method = flow.request.method.lower()
            ctx.log.error(method)
            # url
            url = flow.request.url
            ctx.log.error(url)
            # headers
            headers = dict(flow.request.headers)
            ctx.log.error(headers)
            # body
            body = flow.request.text or {}
            ctx.log.error(body)
            with open(case_file, "a", encoding="utf8") as fa:
                fa.write(self.step(method, url, headers, body))

    def match(self, url):
        if not self.domains:
            ctx.log.error("必须配置过滤域名")
            exit(-1)
        for domain in self.domains:
            if domain in url:
                return True
        return False

    def step(self, method, url, headers, body):
        if method == "get":
            body_grammar = f"params={body}"
        else:
            body_grammar = f"json={body}"
        return f\"\"\"
    # 描述
    # 数据
    # 请求
    response = request(
        "{method}",
        url="{url}",
        headers={headers},
        {body_grammar}
    )
    # 提取
    # 断言
    assert response.status_code < 400
\"\"\"


# ==================================配置开始==================================
addons = [
    Record(
        # 过滤域名
        [
            "http://www.httpbin.org",
            "http://127.0.0.1:5000"
        ],
    )
]
# ==================================配置结束==================================

\"\"\"
==================================命令说明开始==================================
# 正向代理（需要手动打开代理）
mitmdump -s mitm.py
# 反向代理
mitmdump -s mitm.py --mode reverse:http://127.0.0.1:5000 --listen-host 127.0.0.1 --listen-port 8000
==================================命令说明结束==================================
\"\"\"
"""

structure_content = """项目结构说明：
files：文件
fixtures：pytest fixture
reports：allure测试报告
samples：示例代码
  db：数据库
    test_mysql.py：连接MySQL
  http：requests请求
    test_request.py：requests常见用法
    test_request_monkey_patch.py：tep request猴子补丁测试
  login_pay：登陆到下单流程
    mvc：mvc接口用例分离示例（不推荐）
    tep：极速写法（强烈推荐）
tests：测试用例
utils：工具
  fastapi_mock.py：自带fastapi项目
  http_client.py：tep request猴子补丁
  mitm.py：mitmproxy抓包自动生成用例
.gitignore：Git忽略文件规则
conf.yaml：项目配置
conftest.py：pytest conftest
pytest.ini：pytest配置
"""
