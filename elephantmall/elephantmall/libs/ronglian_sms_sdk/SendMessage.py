from ronglian_sms_sdk import SmsSDK

accId = '8aaf0708762cb1cf01773322818e5b4e'
accToken = '7c9dc89721354d118fd50c8cdff0b0f5'
appId = '8aaf0708762cb1cf0177332282555b55'


class CCP(object):
    """发送短信的辅助类"""

    def __new__(cls, *args, **kwargs):
        # 判断是否存在类属性_instance，_instance是类CCP的唯一对象，即单例
        if not hasattr(CCP, "_instance"):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls._instance.sdk = SmsSDK(accId, accToken, appId)
        return cls._instance

    def send_message(self, tid, mobile, datas):
        """发送模板短信"""
        # @param mobile 手机号码
        # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
        # @param tid 模板Id
        resp = eval(self.sdk.sendMessage(tid, mobile, datas))
        print(resp,type(resp))
        # 如果云通讯发送短信成功，返回的字典数据result中statuCode字段的值为"000000"
        if resp.get("statusCode") == "000000":
            # 返回0 表示发送短信成功
            return 0
        else:
            # 返回-1 表示发送失败
            return -1

if __name__ == '__main__':
    ccp = CCP()
    # 注意： 测试的短信模板编号为1
    res = ccp.send_message(1, '17855827681', ['987654', 5])
    print(res)



# def send_message():
#     sdk = SmsSDK(accId, accToken, appId)
#     tid = '1'
#     mobile = '17855827681'
#     datas = ('123456', '5')
#     resp = sdk.sendMessage(tid, mobile, datas)
#     print(resp)

# send_message()
