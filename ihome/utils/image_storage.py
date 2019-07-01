# coding:utf-8

from qiniu import Auth, put_data, etag, urlsafe_base64_encode
import qiniu.config

# 配置Access Key 和 Secret Key
access_key = 'mKAHGIsBFk1HeFAiEOJ17OB8IXjeflAAHpaETt-E'
secret_key = '1ExpghSzEKhaFd0BJUTf1Mo5TJiy0AI3A8C78Zsw'


def storage(file_data):
    """
    上传文件到七牛云
    :param file_data: 要上传的文件
    :return:
    """

    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'ihome'

    # 生成上传Token，可以指定过期时间
    token = q.upload_token(bucket_name, None, 3600)

    ret, info = put_data(token, None, file_data)

    if info.status_code == 200:
        # 表示上传成功，返回文件名
        return ret.get("key")
    else:
        # 上传失败
        raise Exception("上传到七牛失败")


if __name__ == '__main__':
    with open("./666.jpg", "rb") as f:
        file_data = f.read()
        storage(file_data)