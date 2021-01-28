"""elephantmall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path('register/$', views.RegisterView.as_view(), name="register"),
    re_path("usernames/(?P<username>[a-zA-Z0-9-_]{5,20})/count/$",
        views.UsernameCountView.as_view(),
        name="username_count"),
    re_path("mobiles/(?P<mobile>1[3-9]\d{9})/count/$", views.MobileCountView.as_view(), name="mobile_count"),
    re_path("login/$", views.LoginView.as_view(), name="login"),
    re_path("logout/$", views.LogoutView.as_view(), name="logout"),
    re_path("info/$", views.UserCenterView.as_view(), name="info"),
    # re_path("info/$", login_required(views.UserCenterView.as_view()), name="info"), # 方式1
    re_path(r"^emails/$", views.EmailView.as_view(), name="emails"),

    re_path(r"^addresses/$", views.AddressesView.as_view(), name="addresses"),
    re_path(r"^addresses/create/$", views.AddressesView.as_view(), name="addresses_create"),
    re_path(r"^addresses/(?P<address_id>\d+)/$", views.AddressesView.as_view(), name="addresses_update_delete"),
    re_path(r"^addresses/(?P<address_id>\d+)/default/$", views.DefaultAddressView.as_view(), name="addresses_default"),
    re_path(r"^addresses/(?P<address_id>\d+)/title/$", views.AddressTitleView.as_view(), name="addresses_title"),
    re_path(r"^password/$", views.PasswordView.as_view(), name="password"),
]
