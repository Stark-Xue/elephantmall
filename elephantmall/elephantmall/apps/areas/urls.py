from django.urls import re_path

from areas import views

urlpatterns = [
    re_path(r'^areas/$', views.AreaView.as_view(), name="areas"),
]
