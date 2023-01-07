from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from project.encrypt_util import sec_hash
from django.core.cache import cache
from django.http import HttpResponse
from django import forms
from polls.models import PollRespondents, Polls, ClosedQuestions, OpenQuestions, ClosedAnswers, OpenAnswers, \
    UserPollStatus, TokenPolls
from django.contrib.auth.models import User
from users.models import CustomUser


class PollForm(forms.Form):
    poll_name = forms.CharField(max_length=200)
    poll_text = forms.CharField(max_length=1000, widget=forms.Textarea, required=False)


class AddQuestionForm(forms.Form):
    poll_name = forms.CharField(max_length=200)
    poll_text = forms.CharField(max_length=1000, widget=forms.Textarea, required=False)


class QuestionForm(forms.Form):
    question_text = forms.CharField(max_length=200)


class AddRespondentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(AddRespondentForm, self).__init__(*args, **kwargs)
        polls_list = list([(poll.id, poll.poll_name) for poll in Polls.objects.filter(poll_owner_id=user)])
        self.fields['polls'] = forms.ChoiceField(choices=polls_list)
    users_choices = CustomUser.objects.all()
    users_list = [(user.id, user.email) for user in users_choices]
    users = forms.ChoiceField(choices=users_list)


@login_required
def poll_list(request):
    polls = Polls.objects.filter(poll_owner_id=request.user.id)
    return render(request, 'poll_list.html', {'polls': polls})


@login_required
def poll_detail(request, poll_id):
    poll = get_object_or_404(Polls, pk=poll_id)
    open_questions = OpenQuestions.objects.filter(poll_id=poll)
    closed_questions = ClosedQuestions.objects.filter(poll_id=poll)
    closed_questions_pks = ClosedQuestions.objects.filter(poll_id=poll).values("pk")
    closed_answers = ClosedAnswers.objects.filter(question_id__in=closed_questions_pks)
    context = {
        'poll': poll,
        'open_questions': open_questions,
        'closed_questions': closed_questions,
        'closed_questions_pks': closed_questions_pks,
        'closed_answers': closed_answers,
    }
    return render(request, 'poll_detail.html', context)


@login_required
def create_poll(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            poll = Polls(poll_name=form.cleaned_data['poll_name'], poll_text=form.cleaned_data['poll_text'],
                         poll_owner_id=request.user)
            poll.save()
            return redirect('poll_list')
    else:
        form = PollForm()
    return render(request, 'create_poll.html', {'form': form})


@login_required
def edit_poll(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            poll = Polls(poll_name=form.cleaned_data['poll_name'], poll_text=form.cleaned_data['poll_text'],
                         poll_owner_id=request.user)
            poll.save()
            return redirect('poll_list')
    else:
        form = PollForm()
    return render(request, 'edit_poll.html', {'form': form})


@login_required
def add_respondent(request):
    if request.method == 'POST':
        form = AddRespondentForm(request.POST, user=request.user.id)
        if form.is_valid():
            poll = Polls.objects.get(id=form.cleaned_data['polls'])
            user = CustomUser.objects.get(id=form.cleaned_data['users'])
            poll_respondent = PollRespondents(poll_id=poll, user_id=user)
            poll_respondent.save()
            return redirect('poll_list')
    else:
        form = AddRespondentForm(user=request.user)
    return render(request, 'add_respondent.html', {'form': form})


def redis_test(request):
    cache.set("key", "test value")
    redis_response = cache.get('key')
    # cache.close()
    return render(request, 'redis_test.html', {'redis_response': redis_response})


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
