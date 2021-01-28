from django.contrib.auth.backends import ModelBackend

from users.models import User


class MobileModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 查询用户实例
        try:
            user = User.objects.get(mobile=username)
        except User.DoesNotExist:
            pass
        else:
            # 检查密码
            if user and user.check_password(password):
                return user
