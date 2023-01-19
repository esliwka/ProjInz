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
    path('polls/<int:poll_id>/edit', views.poll_edit, name='poll_edit'),
    path('polls/<int:poll_id>/', views.poll_detail, name='poll_detail'),
    path('polls/<int:poll_id>/add_open_question', views.add_open_question, name='add_open_question'),
    path('polls/<int:poll_id>/add_closed_question', views.add_closed_question, name='add_closed_question'),
    path('polls/<int:poll_id>/<int:question_id>/add_answer_to_closed', views.add_answer_to_closed, name='add_answer_to_closed'),
    path('poll_response/', views.poll_response, name='poll_response'),
    path('poll_response_success/', views.poll_response_success, name='poll_response_success'),
    path('poll_response_download/<int:poll_id>/', views.poll_response_download, name='poll_response_download'),
    path('delete_answer/<int:answer_id>/', views.closed_question_delete_answer, name='closed_question_delete_answer'),
    path('move_answer_up/<int:answer_id>/', views.move_answer_up, name='move_answer_up'),
    path('move_answer_down/<int:answer_id>/', views.move_answer_down, name='move_answer_down'),
    path('polls/<int:poll_id>/delete/', views.delete_poll, name='delete_poll'),
    path('open_questions/<int:question_id>/delete/', views.delete_open_question, name='delete_open_question'),
    path('closed_questions/<int:question_id>/delete/', views.delete_closed_question, name='delete_closed_question'),
    path('update_poll_name/<int:poll_id>/', views.update_poll_name, name='update_poll_name'),





]
