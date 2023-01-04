from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from project.encrypt_util import sec_hash

@login_required
def user_home(request):
    form = PasswordChangeForm(request.user)
    hashed_email = sec_hash(request.user.email)
    context = {
        'user': request.user,
        'hashed_email': hashed_email,
        'form': form
    }
    return render(request, 'user_home.html', context)

def index(request):
    if request.user.is_authenticated:
        return redirect('user_home')
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        print('Received POST request')  # Debugging line
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print('Authenticate returned a user')  # Debugging line
            login(request, user)
            return redirect('user_home')
        else:
            return render(request, 'login.html', {'error': 'Invalid login credentials'})
    return render(request, 'login.html')



def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'polls/change_password.html', {
        'form': form
    })
