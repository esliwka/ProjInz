from django.urls import path
from .views import LoginPageView, UserHomePageView

urlpatterns = [
    path('login', LoginPageView.as_view(), name='loginpage'),
    path('home', UserHomePageView.as_view(), name='userhomepage')
]