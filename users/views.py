from django.shortcuts import render
from django.contrib.auth import get_user_model
import random
from project.encrypt_util import *

User = get_user_model()
users = User.objects.all()
my_random_user = random.choice(users)
encrypted = encrypt_data(my_random_user)
decrypted = decrypt_data(encrypted)

def users_view(request):
    return render(request, 'users.html', {'user': (encrypted , my_random_user, decrypted )})