from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user_home/', views.user_home, name='user_home'),
    path('change_password/', views.change_password, name='change_password'),
    path('redis-test/', views.redis_test, name='redis_test'),
    path('create_poll/', views.create_poll, name='create_poll'),
    path('poll-list/', views.poll_list, name='poll_list'),
    path('add-respondent/', views.add_respondent, name='add_respondent'),
    path('polls/<int:poll_id>/', views.poll_detail, name='poll_detail'),
]
