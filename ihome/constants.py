# coding:utf-8

# 图片验证码的reids有效期,单位：秒
IMAGE_CODE_REDIS_EXPIRES = 180

# 短信验证码的redis有效期，单位：秒
SMS_CODE_REDIS_EXPIRES = 300

# 发送短信验证码的时间间隔，单位：秒
SEND_SMS_CODE_INTERVAL = 60

# 登录错误尝试次数
LOGIN_ERROR_MAX_TIMES = 5

# 登录错误限制时间，单位：秒
LOGIN_ERROR_FORBID_TIME = 600

# 七牛云空间域名
QINIU_URL_DOMAIN = "http://ptwabztd5.bkt.clouddn.com/"

# 城区信息的缓存时间，单位：秒
AREA_INFO_REDIS_CACHE_EXPIRES = 7200

# 首页展示最多的房屋数量
HOME_PAGE_MAX_HOUSES = 5

# 首页房屋数据的缓存时间，单位：秒
HOME_PAGE_DATA_REDIS_EXPIRES = 7200

# 房屋详情页面展示的评论最大数
HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 30

# 房屋详情页面数据的缓存时间，单位：秒
HOUSE_DETAIL_REDIS_EXPIRE_SECOND = 7200

# 房屋列表页面每页数据容量
HOUSE_LIST_PAGE_CAPACITY = 2

# 房屋列表页面页数的缓存时间，单位：秒
HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES = 7200

# 支付宝的网关地址（支付地址域名）
ALIPAY_URL_PREFIX = "https://openapi.alipaydev.com/gateway.do?"