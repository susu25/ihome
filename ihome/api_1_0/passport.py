# coding:utf-8

from . import api
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
from ihome import redis_store, db, constans
from ihome.models import User
from sqlalchemy.exc import IntegrityError # sqlalchemy的IntegrityError异常，表示数据库已存在该唯一值
import re


@api.route("/users", methods=["POST"])
def register():
    """注册
    请求的参数： 手机号，短信验证码，密码，确认密码
    参数格式： json"""

    # 获取请求参数
    req_dict = request.get_json()

    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    password2 = req_dict.get("password2")

    # 校验参数
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断手机号格式
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    # 判断密码一致性
    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg="两次密码不一致")

    # 从redis中取出短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="读取真实短信验证码异常")

    # 判断验证码是否过期
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")

    # 删除短信验证码
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 判断用户短信验证码的正确性
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

    # # 判断用户的手机号是否注册过
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    # else:
    #     if user is not None:
    #         return jsonify(errno=RET.DATAEXIST, errmsg="手机已注册")
    #
    # 直接在数据库中设置函数对密码进行sha1加密，给原始值加上盐值(salt)在进行hash加密，即password+"xxx"在hash

    # 保存用户的注册数据到数据库中
    user = User(name=mobile, mobile=mobile)
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据库操作错误，回滚
        db.session.rollback()
        # 表示手机号出现了重复值，即手机号已注册
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据异常")

    # 保存登录状态到session
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="注册成功")


@api.route("/sessions", methods=["POST"])
def login():
    """
    用户登录
    参数： 手机号、密码， 格式：json
    """
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")
    # 校验参数
    # 校验参数完整性
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 手机号格式
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.DBERR, errmsg="手机号格式错误")

    # 判断错误次数是否超限，如果超限，则返回
    # redis 记录请求次数： “access_nums_请求的ip”
    user_ip = request.remote_addr # 用户的ip地址
    try:
        access_nums = redis_store.get("sccess_nums_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) >= constans.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg="错误次数过多，请稍后重试")

    # 从数据库查询用户的数据对象
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    # 进行密码对比验证
    if user is None or not user.check_password(password):
        # 如果验证失败，记录错误次数，返回信息
        try:
            # redis的incr可以对字符串类型的数字数据进行加以操作，如果数据不存在则初始化为1
            redis_store.incr("access_num_%s" % user_ip)
            redis_store.expire("access_num_%s" % user_ip, constans.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)

        return  jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")

    # 如果验证成功，保存登录状态到session
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="登录成功")


@api.route("/session", methods=["GET"])
def check_login():
    """检查登录状态"""
    # 尝试从session中获取用户信息
    name = session.get("name")
    # 如果session中存在数据name则表示用户已登陆，否则未登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


@api.route("/session", methods=["DELETE"])
def logout():
    """登出"""
    session.clear()
    return jsonify(errno=RET.OK, errmsg="OK")