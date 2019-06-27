# coding:utf-8

from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constans, db
from flask import current_app, jsonify, make_response, request
from ihome.utils.response_code import RET
from ihome.models import User
from ihome.libs.yuntongxun.sms import CCP
import random


# GET 127.0.0.1/api/v1.0/image_codes/<image_code_id>
@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    :param image_code_id: 图片验证码编号
    :return: 正常：验证码图片 异常：返回json
    """
    # 业务逻辑处理
    # 生成验证码
    # 名字， 真实文本， 图片数据
    name, text, image_data = captcha.generate_captcha()

    # 将验证码真实值和编号保存到redis中， 设置有效期
    # 单条维护记录，数据格式：字符串 “image_code_编号”： “真实值”
    try:
        redis_store.setex("image_code_%s" % image_code_id, constans.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        # 记录日志
        current_app.logger.error(e)
        # 返回错误信息
        return jsonify(errno=RET.DBERR, errmag="保存图片验证码失败")

    # 返回图片
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/ipg"
    return resp


# GET /api/v1.0/sms_codes/<mobile>?image_code=xxx&image_code_id=xxx
@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    """获取短信验证码"""
    # 获取参数
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")

    # 校验参数
    if not all([image_code_id, image_code]):
        # 参数不完整
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 业务逻辑处理
    # 从redis中取出真实的图片验证码
    try:
        real_image_code = redis_store.get("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="redis数据库异常")

    # 判断图片验证码是否过期
    if real_image_code is None:
        return jsonify(errno=RET.NODATA, reemsg="图片验证码失败")
    # 删除redis中图片验证码，防止用户使用同一图片验证码验证多次
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        # 添加日子记录
        current_app.logger.error(e)

    # 与用户填写的值进行对比
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")

    # 判断对于这个手机号的操作，在60秒之内有没有记录，如果有，则用户操作过频，不接收处理
    try:
        send_flag = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            return jsonify(errno=RET.REQERR, errmsg="请求过于频繁，请60秒后重试")

    # 如果手机号不存在，则生成短信验证码
    sms_code = "%06d" % random.randint(0, 999999)

    # 保存真实的短信验证码
    try:
        redis_store.setex("sms_code_%s" % mobile, constans.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存发送给这个手机号的记录，防止用户60s内再次发送
        redis_store.setex("send_sms_code_%s" % mobile, constans.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码异常")

    # 发送短信
    try:
        cpp = CCP()
        result = cpp.send_template_sms(mobile, [sms_code, int(constans.SMS_CODE_REDIS_EXPIRES/60)], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="发送异常")

    # 返回值
    if result == 0:
        # 发送成功
        return jsonify(errno=RET.OK, errmsg="发送成功")
    else:
        return jsonify(errno=RET.THIRDERR, errmsg="发送失败")