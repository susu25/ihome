# coding:utf-8


from flask import Blueprint, current_app, make_response
from flask_wtf import csrf

# 设置字符编码格式，解决字符串与python默认编码格式不同问题
import sys
reload(sys)
sys.setdefaultencoding('utf8')


# 创建静态文件蓝图
html = Blueprint("web_html", __name__)


# 127.0.0.1:5000/xxx.html
# 127.0.0.1:5000/favicon.ico # 浏览器默认网站标识，浏览器会自己请求这个资源
@html.route("/<re(r'.*'):html_file_name>")
def get_html(html_file_name):
    """提供html文加"""
    # 如果html_file_name为空，表示访问路径时/，请求的是主页
    if not html_file_name:
        html_file_name = "index.html"

    if html_file_name != "favicon.ico":
        html_file_name = "html/" + html_file_name

    # 创建一个csrf_token值
    csrf_token = csrf.generate_csrf()

    # flask提供的返回静态资源的方法
    resp = make_response(current_app.send_static_file(html_file_name))

    # 设置cookie值
    resp.set_cookie("csrf_token", csrf_token)

    return resp
