from django.urls import path
#from polls.views import HomePageView
from . import views

urlpatterns = [
    path('', views.mock_poll, name='mock_poll'),
    path('hash', views.mock_hash, name='mock_hash')
]