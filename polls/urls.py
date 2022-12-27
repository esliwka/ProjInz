from django.urls import path
#from polls.views import HomePageView
from . import views

urlpatterns = [
    path('hash', views.mock_hash, name='mock_hash')
]