from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user_home/', views.user_home, name='user_home'),
    path('change_password/', views.change_password, name='change_password'),
    path('redis-test/', views.redis_test, name='redis_test'),
]
