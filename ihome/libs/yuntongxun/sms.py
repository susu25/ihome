# coding:utf-8

from CCPRestSDK import REST

#主帐号
accountSid= '8a216da86b652116016b73f7b0950c87'

#主帐号Token
accountToken= '5df801b340944cd0b17713a19ed37528'

#应用Id
appId='8a216da86b652116016b73f7b0f10c8e'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id

class CCP(object):
    """自定义封装发送短信辅助类"""
    # 保存对象的类属性
    instance = None

    def __new__(cls):
        # 单例模式创建对象
        if cls.instance is None:
            obj = super(CCP, cls).__new__(cls)

            # 初始化REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)

            cls.instance = obj

        return cls.instance

    def send_template_sms(self, to, datas, temp_id):
        # sendTemplateSMS(手机号码,内容数据,模板Id)
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        # for k, v in result.iteritems():
        #
        #     if k == 'templateSMS':
        #         for k, s in v.iteritems():
        #             print '%s:%s' % (k, s)
        #     else:
        #         print '%s:%s' % (k, v)

        # smsMessageSid:ff75e0f84f05445ba08efdd0787ad7d0
        # dateCreated:20171125124726
        # statusCode:000000
        status_code = result.get("statusCode")
        if status_code == "000000":
            # 表示发送短信成功
            return 0
        else:
            # 发送失败
            return -1

if __name__ == '__main__':
    ccp = CCP()
    # ret = ccp.send_template_sms("15638781235", ["1234", "5"], 1)
    # print (ret)
    
   
