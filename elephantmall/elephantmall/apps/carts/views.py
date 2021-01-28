from django.http import HttpRequest
from django.shortcuts import render

# Create your views here.
from django.views import View


class CartsView(View):
    def get(self, request: HttpRequest):
        return render(request, "index_test.html")