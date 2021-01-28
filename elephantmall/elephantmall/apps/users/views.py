import json

from users.models import Address
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponseForbidden, JsonResponse
from django.db import DatabaseError
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from celery_tasks.email.tasks import send_virify_email
from django.conf import settings
from elephantmall.utils import constants
from elephantmall.utils.mixin import LoginRequiredMixin
from elephantmall.utils.response_code import RETCODE
from users.models import User
from django.core.mail import send_mail

from elephantmall.utils.sign import Signer

from django.contrib.auth import login, authenticate, logout

import re,sys

# Create your views here.

class RegisterView(View):
    """用户注册"""

    def get(self, request: HttpRequest):
        """展示用户注册界面"""
        print(sys.path)
        return render(request, 'register.html')

    def post(self, request: HttpRequest):
        """提交用户注册数据"""

        # 1.提取数据
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        mobile = request.POST.get("mobile")
        sms_code = request.POST.get("sms_code")
        allow = request.POST.get("allow")

        # 2.校验数据
        # 判断参数是否齐全
        if not all([username, password, password2, mobile, sms_code, allow]):
            return HttpResponseForbidden("缺少必须的参数")
        # 判断用户名是否是5-20个字符
        if not re.match(r"^[a-zA-Z0-9-_]{5,20}$", username):
            return HttpResponseForbidden("请输入5-20个字符的用户名")
        # 判断密码是否是8-20个字符
        if not re.match(r"^[a-zA-Z0-9]{8,20}$", password):
            return HttpResponseForbidden("请输入8-20个字符的密码")
        # 判断手机号是否合法
        if not re.match(r"^1[3-9]\d{9}$", mobile):
            return HttpResponseForbidden("请输入正确的手机号")
        # 判断两次密码是否一致
        if password != password2:
            return HttpResponseForbidden("两次密码输入不一致")
        # 判断是否勾选用户协议
        if allow != "on":
            return HttpResponseForbidden("请勾选用户协议")
        # 判断短信验证码是否正确
        connection = get_redis_connection("sms_code")
        sms_code_redis = connection.get(mobile)
        if sms_code_redis is None:
            return render(request, "register.html", {"register_errmsg": "短信验证码无效"})
        if sms_code != sms_code_redis.decode():
            return render(request, "register.html", {"register_errmsg": "短信验证码错误"})

        # 3.处理逻辑
        # 创建用户
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError as e:
            return render(request, "register.html", {"register_errmsg": "服务器注册错误"})
        # 保持用户登录状态
        login(request, user)

        # 4.返回响应

        response = redirect("/")
        response.set_cookie('username', user.username)
        return response

class UsernameCountView(View):
    """验证用户名是否重复"""

    def get(self, request, username):
        # 提取数据
        # 校验数据
        # 处理逻辑
        try:
            count = User.objects.filter(username=username).count()
        except DatabaseError:
            ret = {
                "code": RETCODE.DBERR,
                "errmsg": '查询失败',
                "count": 0
            }
        # 返回响应
        ret = {
            "code": RETCODE.OK,
            "errmsg": 'OK',
            "count": count
        }
        return JsonResponse(ret)

class MobileCountView(View):
    """验证手机号是否重复"""

    def get(self, request, mobile):
        # 提取数据
        # 校验数据
        # 处理逻辑
        try:
            count = User.objects.filter(mobile=mobile).count()
        except DatabaseError:
            data = {
                "code": RETCODE.DBERR,
                "errmsg": '查询用户失败',
                "count": 0
            }
        # 返回结果
        data = {
            "code": RETCODE.OK,
            "errmsg": 'OK',
            "count": count
        }
        return JsonResponse(data)


class LoginView(View):
    def get(self, request):
        """打开登录页面"""
        return render(request, "login.html")

    def post(self, request):
        """提交登录数据"""
        # 1.提取参数
        username = request.POST.get("username")
        password = request.POST.get("password")
        remembered = request.POST.get("remembered")

        # 2.校验参数
        if not all([username, password, remembered]):
            return HttpResponseForbidden("缺少必须的参数")

        # 判断用户名是否是5-20个字符
        if not re.match(r"^[a-zA-Z0-9-_]{5,20}$", username):
            return HttpResponseForbidden("请输入5-20个字符的用户名")
        # 判断密码是否是8-20个字符
        if not re.match(r"^[a-zA-Z0-9]{8,20}$", password):
            return HttpResponseForbidden("请输入8-20个字符的密码")

        # 3.处理逻辑
        # 3.1 认证登录数据
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, "login.html", {"loginerror": "用户名或者密码错误"})
        # 3.2 保持登录状态
        login(request, user)
        if remembered != "on":
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)
        # 返回响应
        # 1、直接登陆跳转到首页；2、用户中心-》登陆界面，跳转到用户中心
        next_path = request.GET.get("next", reverse("contents:index"))
        response = redirect(next_path)
        response.set_cookie("username", user.username, max_age=constants.USERNAME_COOKIE_EXPIRES)
        return response


class LogoutView(View):
    """退出登录"""

    def get(self, request):
        # 清理session
        logout(request)
        # 删除cookie中的username
        response = redirect(reverse("contents:index"))
        response.delete_cookie("username")
        # 重定向到首页
        return response


# class UserCenterView(View):
#     def get(self, request: HttpRequest):
#         """打开用户中心页面"""
#         if request.user.is_authenticated:
#             return render(request, "user_center_info.html")
#         else:
#             return redirect(reverse("users:login"))

# # 方式1
# class UserCenterView(View):
#     def get(self, request: HttpRequest):
#         """打开用户中心页面"""
#         # if request.user.is_authenticated:
#         #     return render(request, "user_center_info.html")
#         # else:
#         #     return redirect(reverse("users:login"))
#         return render(request, "user_center_info.html")


# # 方式2
# class UserCenterView(View):
#
#     @classmethod
#     def as_view(cls, **initkwargs):
#         view = super().as_view()
#         return login_required(view)   # 类视图的装饰方法
#
#     def get(self, request: HttpRequest):
#         """打开用户中心页面"""
#         return render(request, "user_center_info.html")


# 方式3
class UserCenterView(LoginRequiredMixin, View):         #  mixin设计模式

    def get(self, request: HttpRequest):
        """打开用户中心页面"""
        context = {
            "username": request.user.username,
            "mobile": request.user.mobile,
            "email": request.user.email,
            "email_active": request.user.email_active,
        }
        return render(request, "user_center_info.html", context)


class EmailView(View):
    def put(self, request: HttpRequest):
        """
        添加邮箱
        :param request:
        :return:
        """
        # 1.判断用户是否登录
        # 没有登录，返回错误信息
        if not request.user.is_authenticated:
            return JsonResponse({'code': RETCODE.USERERR, 'errmsg': "用户未登录"})
        # 2.提取数据
        data = json.loads(request.body.decode())
        email = data.get('email')

        # 3.验证邮箱数据
        # 3.1.验证邮箱格式不通过，返回错误信息
        if not email:
            return HttpResponseForbidden("缺少必须的参数")
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return HttpResponseForbidden("参数格式不正确")
        # 4.处理数据
        # 4.1.修改User表中邮箱数据
        request.user.email = email
        request.user.save()
        # 4.2.发送邮箱验证邮件
        userid = {"user_id": request.user.id}
        token = Signer(constants.EMAIL_VERIFY_SIGN_EXPIRES).sign(userid)
        verify_url = settings.EMAIL_VERIFY_URL + "?token=" + token
        # subject = "大象商城邮箱验证"
        # message = ""
        # from_email = settings.EMAIL_FROM
        # recipient_list = [email]
        # html_message = '<p>尊敬的用户您好！</p>' \
        #                '<p>感谢您使用蜗牛商城。</p>' \
        #                '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
        #                '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
        # send_mail(subject, message, from_email, recipient_list, html_message=html_message)

        # user_id = {"user_id": request.user.id}
        # token = Signer(constants.EMAIL_VERIFY_SIGN_EXPIRES).sign(user_id)
        # verify_url = settings.EMAIL_VERIFY_URL + "?token=" + token
        send_virify_email.delay(email, verify_url)
        # 5.返回成功响应结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class EmailVerifyView(View):
    pass


class AddressesView(View):
    def get(self, request: HttpRequest):
        addresses = Address.objects.filter(user=request.user, is_deleted=False)
        print("test:", request.user.username)

        address_list = []
        for address in addresses:
            address_list.append({
                'id': address.id,
                'title': address.title,
                'receiver': address.receiver,
                'province': address.province.name,
                'province_id': address.province_id,
                'city': address.city.name,
                'city_id': address.city_id,
                'district': address.district.name,
                'district_id': address.district_id,
                'place': address.place,
                'mobile': address.mobile,
                'tel': address.telephone,
                'email': address.email,
            })
        context = {
            'addresses': address_list,
            'user': request.user
        }
        return render(request, "user_center_address.html", context)

    def post(self, request: HttpRequest):
        """新增收货地址"""
        # 1.提取数据
        data_dict = json.loads(request.body.decode())
        title = data_dict.get("title")
        receiver = data_dict.get("receiver")
        province_id = data_dict.get("province_id")
        city_id = data_dict.get("city_id")
        district_id = data_dict.get("district_id")
        place = data_dict.get("place")
        mobile = data_dict.get("mobile")
        tel = data_dict.get("tel")
        email = data_dict.get("email")

        # 2.校验数据
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseForbidden("缺少必须的参数")
        if not re.match(r"^1[345789]\d{9}$", mobile):
            return HttpResponseForbidden("mobile格式错误")
        if tel and not re.match(r"^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$", tel):
            return HttpResponseForbidden("tel格式错误")
        if email and not re.match(r"^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            return HttpResponseForbidden("email格式错误")
        if not title:
            title = receiver

        # 3.处理逻辑
        try:
            address = Address.objects.create(
                title=title,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                telephone=tel,
                email=email,
                user=request.user
            )
        except Exception:
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': "新增地址失败"})
        # 4.返回响应
        address_dict = {
            'id': address.id,
            'title': address.title,
            'receiver': address.receiver,
            'province': address.province.name,
            'province_id': address.province_id,
            'city': address.city.name,
            'city_id': address.city_id,
            'district': address.district.name,
            'district_id': address.district_id,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.telephone,
            'email': address.email,
        }
        return JsonResponse({'code': RETCODE.OK, 'errmsg': "ok", 'address': address_dict})

    def put(self, request: HttpRequest, address_id):
        # 1.提取数据
        data_dict = json.loads(request.body.decode())
        receiver = data_dict.get("receiver")
        province_id = data_dict.get("province_id")
        city_id = data_dict.get("city_id")
        district_id = data_dict.get("district_id")
        place = data_dict.get("place")
        mobile = data_dict.get("mobile")
        tel = data_dict.get("tel")
        email = data_dict.get("email")

        # 2.校验数据
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseForbidden("缺少必须的参数")
        if not re.match(r"^1[345789]\d{9}$", mobile):
            return HttpResponseForbidden("mobile格式错误")
        if tel and not re.match(r"^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$", tel):
            return HttpResponseForbidden("tel格式错误")
        if email and not re.match(r"^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            return HttpResponseForbidden("email格式错误")

        # 3.处理逻辑
        try:
            Address.objects.filter(id=address_id).update(
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                telephone=tel,
                email=email
            )
        except Exception:
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': "修改地址失败"})
        # 4.返回响应
        address = Address.objects.get(id=address_id)
        address_dict = {
            'id': address_id,
            'title': address.title,
            'receiver': address.receiver,
            'province': address.province.name,
            'province_id': address.province_id,
            'city': address.city.name,
            'city_id': address.city_id,
            'district': address.district.name,
            'district_id': address.district_id,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.telephone,
            'email': address.email,
        }
        return JsonResponse({'code': RETCODE.OK, 'errmsg': "ok", 'address': address_dict})

    def delete(self, request: HttpRequest, address_id):
        """删除收货地址"""
        # Address.objects.filter(id=address_id).update(is_deleted=True)
        try:
            address = Address.objects.get(id=address_id)
            address.is_deleted = True
            address.save()
        except:
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': "删除地址失败"})
        return JsonResponse({'code': RETCODE.OK, 'errmsg': "ok"})


class DefaultAddressView(View):
    def put(self, request: HttpRequest, address_id):
        try:
            request.user.default_address_id = address_id
            request.user.save()
        except Exception:
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': "设置默认收货地址失败"})
        return JsonResponse({'code': RETCODE.OK, 'errmsg': "ok"})


class AddressTitleView(View):
    def put(self, request: HttpRequest, address_id):
        """修改地址标题"""
        data = json.loads(request.body.decode())
        title = data.get("title")

        try:
            address = Address.objects.get(id=address_id)
            address.title = title
            address.save()
        except:
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': "修改地址标题失败"})
        return JsonResponse({'code': RETCODE.OK, 'errmsg': "ok"})


class PasswordView(View):
    def get(self, request):
        """打开修改密码页面"""
        return render(request, "user_center_pass.html")

    def post(self, request):
        # 1.提取参数
        old_pwd = request.POST.get("old_pwd")
        new_pwd = request.POST.get("new_pwd")
        new_cpwd = request.POST.get("new_cpwd")

        # 2.校验参数
        if not all([old_pwd, new_pwd, new_cpwd]):
            return HttpResponseForbidden("缺少必须数据")

        if not request.user.check_password(old_pwd):
            return HttpResponseForbidden("原密码不正确")

        if not re.match(r"^[a-zA-Z0-9]{8,20}$", new_pwd):
            return HttpResponseForbidden("密码格式错误")

        if new_pwd != new_cpwd:
            return HttpResponseForbidden("两次输入的密码不一致")

        # 3.处理逻辑
        try:
            request.user.set_password(new_pwd)
            request.user.save()
        except:
            return HttpResponseForbidden("修改密码失败")

        # 退出登录
        logout(request)
        response = redirect(reverse("users:login"))
        response.delete_cookie("username")
        # 4.返回响应
        return response