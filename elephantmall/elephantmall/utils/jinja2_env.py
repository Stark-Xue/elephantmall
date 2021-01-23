from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from jinja2 import Environment


def jinja2_environment(**option):
    environment = Environment(**option)
    environment.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
    })
    return environment


"""
确保可以在模板引擎中使用{{ url('') }} {{ static('') }}这类语句 
"""