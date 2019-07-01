# coding:utf-8

from ihome.tasks.main import celery_app
from ihome.libs.yuntongxun.sms import CCP


@celery_app.task
def send_sms(to, datas, temp_id):
    """发送异步短信"""
    ccp = CCP()
    try:
        result = ccp.send_template_sms(to, datas, temp_id)
    except Exception as e:
        result = -2
    return result