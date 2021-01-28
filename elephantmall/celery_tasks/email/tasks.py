from django.conf import settings
from django.core.mail import send_mail

from celery_tasks.app import app


@app.task(name='send_verify_email', bind=True, retry_backoff=3)
def send_virify_email(self, to_email, verify_url):

    try:
        subject = "大象商城邮箱验证"
        message = ""
        from_email = settings.EMAIL_FROM
        recipient_list = [to_email]
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用蜗牛商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
        send_mail(subject, message, from_email, recipient_list, html_message=html_message)
    except Exception as e:
        raise self.retry(exc=e, max_retries=3)