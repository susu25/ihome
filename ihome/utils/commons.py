# coding:utf-8


from werkzeug.routing import BaseConverter


# 自定义正则转换器
class ReConverter(BaseConverter):
    """万能转换器"""
    def __init__(self, url_map, *args):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        # 保存正则表达式
        self.regex = args[0]