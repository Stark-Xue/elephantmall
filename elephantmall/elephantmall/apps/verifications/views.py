import random

from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from redis import Redis

from celery_tasks.sms.tasks import send_sms_code
from elephantmall.libs.captcha.captcha import captcha
from elephantmall.libs.ronglian_sms_sdk.SendMessage import CCP
from elephantmall.utils import constants
from elephantmall.utils.response_code import RETCODE


class ImageCodeView(View):
    """图片验证码"""
    def get(self, request, uuid):
        # 1.提取数据
        # 2.校验数据
        # 3.处理逻辑
        # 3.1生成图片验证码
        code, code_text, code_image = captcha.generate_captcha()
        # 3.2保存图片验证码字符串到 redis
        connection: Redis = get_redis_connection("image_code")
        connection.setex(uuid, constants.IMAGE_CODE_REDIS_EXPIRES, code_text) # 设置过期时间
        # 4.返回响应,返回图片验证码byte类型数据
        return HttpResponse(code_image, content_type="image/jpg")


class SmsCodeView(View):
    """短信验证码"""

    def get(self, request: HttpRequest, mobile):
        """
        发送短信验证码
        :param request:
        :param mobile:
        :return:
        """
        sms_conn: Redis = get_redis_connection("sms_code")
        send_flag = sms_conn.get("send_flag_%s" % mobile)
        if send_flag:
            return JsonResponse({"code": RETCODE.THROTTLINGERR, "errmsg": "请求短信验证码太频繁"})
        # 1.接收参数
        image_code: str = request.GET.get("image_code")
        uuid = request.GET.get("uuid")
        # 2.校验参数
        if not all([image_code, uuid]):
            return JsonResponse({"code": RETCODE.NECESSARYPARAMERR, "errmsg": "缺少必须参数"})
        # 3.校验图形验证码
        # 3.1 从redis提取图形验证码
        img_conn: Redis = get_redis_connection("image_code")
        image_code_redis = img_conn.get(uuid)
        if image_code_redis is None:
            return JsonResponse({"code": RETCODE.PARAMERR, "errmsg": "图形验证码失效"})
        image_code_redis = image_code_redis.decode()
        # 3.2 删除图形验证码
        img_conn.delete(uuid)
        # 3.3 比较图形验证码
        if image_code.lower() != image_code_redis.lower():
            return JsonResponse({"code": RETCODE.PARAMERR, "errmsg": "图形验证码错误"})
        # 4.发送短信验证码
        # 4.1 产生短信验证码
        sms_code = "%06d" % random.randint(0, 999999)
        print(sms_code)
        # 4.2 保存短信验证码到redis
        # sms_conn: Redis = get_redis_connection("sms_code")
        pipeline = sms_conn.pipeline()
        pipeline.setex(mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pipeline.setex("send_flag_%s" % mobile, constants.SEND_FLAG_INTERVAL, 1)
        pipeline.execute()
        # 4.3 发送短信验证码
        # ret = CCP().send_message(constants.SMS_TEMPLATE_ID, mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60])
        send_sms_code.delay(mobile, sms_code)
        # 返回响应
        # if ret == 0:
        return JsonResponse({"code": RETCODE.OK, "errmsg": "OK"})
        # else:
        #     return JsonResponse({"code": RETCODE.SMSCODERR, "errmsg": "短信发送失败"})