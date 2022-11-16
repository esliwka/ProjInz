from django.views.generic.base import TemplateView
from django.shortcuts import render
import random
from project.encrypt_util import *


users = [n for n in range(1, 10)]


def mock_poll(request):
    return render(request, 'index.html', {'user': random.choice(users)})
