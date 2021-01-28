import os, sys

from celery import Celery

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elephantmall.settings.dev")

app = Celery("elephant")
app.config_from_object("celery_tasks.celery_config")
app.autodiscover_tasks(["celery_tasks.sms.tasks"])
app.autodiscover_tasks(["celery_tasks.email.tasks"])