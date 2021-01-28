import logging

from celery_tasks.app import app
from elephantmall.libs.ronglian_sms_sdk.SendMessage import CCP
from elephantmall.utils import constants

# 3*2^(n-1)
# 3
# 6
# 12
# 24
@app.task(name="send_sms_code", bind=True, retry_backoff=3) #bind 绑定自己，允许失败后重新发起请求；retry_backoff 重试时间
def send_sms_code(self, mobile, sms_code):
    """

    :param mobile: 手机号
    :param sms_code: 验证码
    :return: 0 表示成功 -1 表示失败
    """
    try:
        ret = CCP().send_message(constants.SMS_TEMPLATE_ID, mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60])
        logging.getLogger("django").info("sms_code:" + sms_code)
    except Exception as e:
        raise self.retry(exc=e, max_retries=4)

    return ret