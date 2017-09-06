# -*- coding=utf-8 -*-
__author__ = 'ghostclock'

import requests
import re
import time
import os.path

try:
    import cookielib
except:
    import http.cookiejar as cookielib
try:
    from PIL import Image   # 需要安装用pillow模块
except:
    pass


"""
用session登录知乎，验证码为数字字母验证码
"""

user_agent_FireFox = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
headers = {
    "Host": "www.zhihu.com",
    "Referer": "https://www.zhihu.com/",
    "User-Agent": user_agent_FireFox
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
        print("_xsrf = %s", _xsrf)
        return _xsrf
    else:
        return ""


def get_captcha():
    """
    获取验证码数字字母验证码
    """
    time_date = str(int(time.time() * 1000))
    captcha_url = "https://www.zhihu.com/captcha.gif?r=" + time_date + "&type=login"
    response = session.get(captcha_url, headers=headers)
    with open("captcha.gif", "wb") as file:
        file.write(response.content)
        file.close()
    # 用pillow 的 Image 显示验证码
    try:
        image = Image.open("captcha.gif")
        image.show()
        image.close()
    except IOError as error:
        print('请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input("请输入验证码\n>")    # 手动输入验证码
    return captcha


def zhihu_login(account, password):
    """
    发起登录请求
    """
    def login_request(login_url, login_key):
        post_data = {
            "_xsrf": get_xsrf(),
            login_key: account,
            "password": password
        }
        # 不需要验证码，直接登录
        login_page = session.post(login_url, data=post_data, headers=headers)
        code = login_page.status_code
        if 200 == code:
            login_status = login_page.json()
            if  1 == login_status.get("r"):
                # 不输入验证码登录失败
                # 使用需要输入验证码的方式登录
                post_data["captcha"] = get_captcha()
                login_page = session.post(login_url, data=post_data, headers=headers)
                login_status = login_page.json()
                print(login_status.get("msg"))
            else:
                print(login_page.content)
        # 保存cookies到本地
        # 下次可以使用cookie直接登录，不需要输入账号和密码
        session.cookies.save()

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
    if is_login():
        print("你已登录")
    else:
        print("请登录")