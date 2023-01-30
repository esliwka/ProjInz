from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user_home/', views.user_home, name='user_home'),
    path('change_password/', views.change_password, name='change_password'),
    
    path('create_poll/', views.create_poll, name='create_poll'),
    path('poll-list/', views.poll_list, name='poll_list'),
    path('add-respondent/', views.add_respondent, name='add_respondent'),
    path('polls/<int:poll_id>/edit', views.poll_edit, name='poll_edit'),
    path('polls/<int:poll_id>/', views.poll_detail, name='poll_detail'),
    path('polls/poll_results/', views.poll_results, name='poll_results'),
    path('verify/', views.user_verify_integrity, name='user_verify_integrity'),
    path('polls/<int:poll_id>/add_respondent/', views.button_add_respondent, name='button_add_respondent'),
    path('polls/<int:poll_id>/respondent_add/', views.button_add_respondent_edit, name='button_add_respondent_edit'),
    path('polls/<int:poll_id>/add_open_question', views.add_open_question, name='add_open_question'),
    path('polls/<int:poll_id>/add_closed_question', views.add_closed_question, name='add_closed_question'),
    path('polls/<int:poll_id>/<int:question_id>/add_answer_to_closed', views.add_answer_to_closed, name='add_answer_to_closed'),
    path('poll_response/', views.poll_response, name='poll_response'),
    path('poll_response_success/<int:poll_id>/', views.poll_response_success, name='poll_response_success'),
    path('register/', views.register_user, name='register_user'),
    path('open_question_responses_download/<int:question_id>/', views.open_question_responses_download, name='open_question_responses_download'),
    path('poll_response_download/<int:poll_id>/', views.poll_response_download, name='poll_response_download'),
    path('polls/unpublish/<int:poll_id>/', views.unpublish_poll, name='unpublish_poll'),
    path('polls/<int:poll_id>/publish/', views.publish_poll, name='publish_poll'),
    path('delete_answer/<int:answer_id>/', views.closed_question_delete_answer, name='closed_question_delete_answer'),
    path('move_answer_up/<int:answer_id>/', views.move_answer_up, name='move_answer_up'),
    path('move_answer_down/<int:answer_id>/', views.move_answer_down, name='move_answer_down'),
    path('polls/<int:poll_id>/delete/', views.delete_poll, name='delete_poll'),
    path('open_questions/<int:question_id>/delete/', views.delete_open_question, name='delete_open_question'),
    path('closed_questions/<int:question_id>/delete/', views.delete_closed_question, name='delete_closed_question'),
    path('update_poll_name/<int:poll_id>/', views.update_poll_name, name='update_poll_name'),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
