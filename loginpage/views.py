from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic.base import TemplateView

class LoginPageView(LoginView):
    template_name = 'loginpage.html'

class UserHomePageView(TemplateView):
    template_name = 'user_home.html'