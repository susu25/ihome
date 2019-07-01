# coding:utf-8


from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
from ihome.utils.response_code import RET
import functools


# 自定义正则转换器
class ReConverter(BaseConverter):
    """万能转换器"""
    def __init__(self, url_map, *args):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        # 保存正则表达式
        self.regex = args[0]


# 自定义登录验证装饰器
def login_required(view_func):
    # wraps函数的作用是将warpper内层函数的属性设置为被装饰函数view_func的属性
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断用户的登录状态
        user_id = session.get("user_id")

        # 如果用户登录执行视图函数
        if user_id is not None:
            # 将user_id保存到g对象中,在视图函数中可以通过g对象获取保存数据
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # 如果未登录，返回未登录信息
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    return wrapper