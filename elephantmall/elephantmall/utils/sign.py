from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature


class Signer(object):

    def __init__(self, expires_in):
        self.serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in)

    def sign(self, obj):
        """
        对python字典先进行json序列化，再对序列化结果进行签名
        :param obj:
        :return: 签名后的字符串
        """
        token = self.serializer.dumps(obj)
        return token.decode()

    def unsign(self, s):
        """
        对传入的字符串验证签名, 验证成功返回字符串中的被签名的数据对应的python字典
        :param s: 要验证的签名字符串
        :return: python字典
        """
        try:
            obj = self.serializer.loads(s)
        except BadSignature:
            obj = None
        return obj
