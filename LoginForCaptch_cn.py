# -*- coding=utf-8 -*-
__author__ = 'ghostclock'

"""
https://github.com/muchrooms/zheye
识别知乎倒立验证码，登录
"""

import requests
import shutil
import time
import re
try:
    import cookielib
except:
    import http.cookiejar as cookielib

from zheye import zheye
z = zheye()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br"
}


session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("Cookie 未能加载")

def get_xsrf():
    """
    获取xsrf
    """
    response = session.get("https://www.zhihu.com/", headers=headers)
    match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text, re.DOTALL)
    if match_obj:
        _xsrf = match_obj.group(1)
        print("_xsrf = ", _xsrf)
        return _xsrf
    else:
        return ""


def get_captcha():
    """
    获取中文倒立验证码
    """
    time_date = str(int(time.time() * 1000))
    captcha_url = "https://www.zhihu.com/captcha.gif?r={}&type=login&lang=cn".format(time_date)
    response = session.get(url=captcha_url, headers=headers, stream=True)
    if 200 == response.status_code:
        with open("cn_captcha.gif", "wb") as file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, file)

        positions = z.Recognize("cn_captcha.gif") # 返回的tuple的第二个值是x坐标，第一个值是y坐标，笛卡尔坐标系 [(y, x), (y, x)]
        print(positions)

        pos = positions

        poss = []
        for tup in pos:
            temp = []
            x = float(format(tup[1] / 2, "0.2f"))
            y = float(format(tup[0] / 2, "0.2f"))
            temp.append(x)
            temp.append(y)

            poss.append(temp)
        print("处理后的坐标 ", poss)
        return poss


def get_captcha_str():
    """
    获取验证码字符串
    """
    pos = get_captcha()
    captcha_str = '{"img_size": [200, 44], "input_points": %s}' % pos
    print("captcha_str ", captcha_str)
    return captcha_str


def zhihu_login(account, password):
    """
    发起登录请求
    """
    def login_request(login_url, login_key):
        post_data = {
            "_xsrf": get_xsrf(),
            login_key: account,
            "password": password,
        }
        # 不需要验证码，直接登录
        login_page = session.post(login_url, data=post_data, headers=headers)
        code = login_page.status_code
        if 200 == code:
            login_status = login_page.json()
            if 1 == login_status.get("r"):
                captcha_str = get_captcha_str()
                post_data["captcha"] = captcha_str
                post_data["captcha_type"] = "cn"

                login_page = session.post(login_url, data=post_data, headers=headers)
                login_status = login_page.json()
                if "登录成功" == login_status.get("msg"):
                    print("登录成功")
                    # 保存cookies到本地
                    # 下次可以使用cookie直接登录，不需要输入账号和密码
                    session.cookies.save()
                else:
                    print(login_status.get("msg"))
            else:
                print(login_page.content)

    #  知乎登录方式
    if re.match("^1\d{10}", account):
        """
        手机号登录
        """
        print("要登录的手机号为: ", account)
        login_url = "https://www.zhihu.com/login/phone_num"
        login_request(login_url, "phone_num")
    else:
        if "@" in account:
            """
            邮箱登录
            """
            print("要登录的邮箱为: ", account)
            login_url = "https://www.zhihu.com/login/email"
            login_request(login_url, "email")

def is_login():
    """
    通过个人中心页面返回状态码来判断是否为登录状态
    """
    inbox_url = "https://www.zhihu.com/inbox"
    response = session.get(inbox_url, headers=headers)
    if 200 != response.status_code:
        return False
    else:
        return True

if __name__ == "__main__":
    zhihu_login("youaccount", "youpassword")
    # if is_login():
    #     print("你已登录")
    # else:
    #     print("请登录")

