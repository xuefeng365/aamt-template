import json
import time
from mimetypes import MimeTypes
from urllib.parse import urlencode

import allure
import jmespath
import requests
from requests import Response
from requests_toolbelt.multipart.encoder import MultipartEncoder

from aamt.config import *
from aamt.fixture import AamtVars
from aamt.logger import Logger


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
        self.aamt_vars = AamtVars()
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

    def send(self, url: str = '', method='post', body={}, body_type: str = Body_type.json, x_token='',
             file_key='picFile', file_path='', timeout=30, **kwargs):

        start_time = time.time()

        if not url.startswith(("http://", "https://")):
            raise Exception("请输入正确的url, 记得带上http:// 或者 https:// 哦")

        # 用户传了headers,就用用户的,不传就用默认的
        headers = kwargs.get("headers", self.default_header)

        if x_token:
            headers["_token_"] = x_token.strip('"')  # strip() 方法用于移除字符串头尾指定的字符（默认为空格或换行符）或字符序列。

        if method == "get":
            result = self.session.request(url=url, method=method, params=body, headers=headers, timeout=timeout,
                                          **kwargs)

        elif method == "post":
            self.logging.info(f'body_type类型：{body_type}')
            if body_type == Body_type.json:
                headers['Content-Type'] = 'application/json; charset=UTF-8'
                result = self.session.request(url=url, method=method, json=body, headers=headers, timeout=timeout,
                                              **kwargs)
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
                result = self.session.request(url=url, method=method, data=form_data, headers=headers, timeout=timeout,
                                              **kwargs)

            elif body_type == Body_type.form_text:
                # 把要传入的数据 转变为form_data格式
                form_data = MultipartEncoder(body)
                # 以下命令自动 转变 headers 中的 Content-Type 为：'multipart/form-data; boundary=。。。。。。。。。。。
                headers['Content-Type'] = form_data.content_type
                result = self.session.request(url=url, method=method, data=form_data, headers=headers, timeout=timeout,
                                              **kwargs)

            elif body_type == Body_type.binary:
                files = {file_key: open(file_path, 'rb')}
                # 文件流通过files 传给request的请求参数files
                result = self.session.request(url=url, method=method, json=body, headers=headers, files=files,
                                              timeout=timeout, **kwargs)
            else:
                raise ValueError(f"=====body_type没有定义，{body_type} 请确认====")

        elif method == "patch":
            result = self.session.request(url=url, method=method, data=json.dumps(body), headers=headers,
                                          timeout=timeout, **kwargs)

        elif method == "delete":
            result = ''
        elif method == "put":
            result = ''
        else:
            raise ValueError(f"=====大兄弟===暂不支持{method} 请求呢====需要就自己补充吧====")

        end_time = time.time()
        # python 内置函数 保留4位小数
        time_ = round((end_time - start_time), 4)

        # 处理
        result = AamtResponse(result)

        try:
            self.logging.info(
                f'\n请求日志：\nurl: {url}\nmethod: {method}\nbody: \n{body}\nbody_type: {body_type}\nheaders: \n{headers}\n**********************************************************************************')
            self.logging.debug(
                f'\n响应日志：\n响应码: {result.status_code}\n请求>响应 时间开销: {time_}\n**********************************************************************************\n')
        except AttributeError:
            self.logging.error(
                f'\n无法获取响应码， 响应日志：\n{result}\n请求>响应 时间开销: {time_}\n**********************************************************************************\n')
        except TypeError:
            self.logging.warning(f'警告：{kwargs}')

        self.__create_request_log(url, method, body, body_type, headers)
        try:
            self.__create_response_log(result.status_code, result.json(), time_)
            return result.json()
        except:
            self.__create_response_log(result.status_code, result.text, time_)
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
    def __create_response_log(self, status_code, text, time_):
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
    a.send(url='http://www.baidu.com', method='get', body={}, body_type=Body_type.json)
