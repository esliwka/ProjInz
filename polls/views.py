from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from project.encrypt_util import sec_hash
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse, FileResponse
from django import forms
from polls.models import PollRespondents, Polls, ClosedQuestions, OpenQuestions, ClosedAnswers, OpenAnswers, \
    UserPollStatus, TokenPolls
from django.contrib.auth.models import User
from users.models import CustomUser
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core import serializers
import json
import io




@login_required
def poll_response(request): 
    # Get the user's polls that they are a respondent of
    user_polls = PollRespondents.objects.filter(user_id=request.user)
    user_polls_pks = list(user_polls.values_list("poll_id", flat=True))
    polls = Polls.objects.filter(pk__in=user_polls_pks)

    if request.method == 'POST':
        # Get the selected poll
        poll_id = request.POST.get('poll_id')
        selected_poll = get_object_or_404(Polls, pk=poll_id)
        closed_questions = ClosedQuestions.objects.filter(poll_id=poll_id)
        open_questions = OpenQuestions.objects.filter(poll_id=poll_id)
        # Save the user's responses to the closed questions
        # ...
        # Save the user's responses to the open questions
        # ...
        # Redirect the user to a success page
        return redirect('poll_response_success')
    else:
        poll_id = request.GET.get('poll_id')
        request.session['poll_id'] = poll_id
        if not poll_id:
            if polls:
                poll_id = polls[0].id
        current_poll = Polls.objects.get(pk=poll_id)
        closed_questions = ClosedQuestions.objects.filter(poll_id=poll_id)
        open_questions = OpenQuestions.objects.filter(poll_id=poll_id)    
        # Render the template with the polls, closed questions, and open questions
        return render(request, 'poll_response.html', {'polls': polls, 'closed_questions': closed_questions, 'open_questions': open_questions,'poll_id':poll_id,'current_poll':current_poll})

@login_required
def poll_response_download(request, poll_id):
    json_data = cache.get(poll_id) # get the json data from the cache
    hash_data = sec_hash(json_data)
    file = io.StringIO(hash_data)
    response = FileResponse(file, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="hash.txt"'
    return response

@login_required
def poll_response_success(request, context):
    poll_id = context.get('poll_id')
    json_data = cache.get(poll_id) # get the json data from the cache
    hash_data = sec_hash(json_data)
    file = io.StringIO(hash_data)
    response = FileResponse(file, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="hash.txt"'
    return render(request, 'poll_response_success.html', {'json_data_hash': hash_data })

class PollForm(forms.Form):
    poll_name = forms.CharField(max_length=200)
    poll_text = forms.CharField(max_length=1000, widget=forms.Textarea, required=False)

class OpenQuestionForm(forms.Form):
    question = forms.CharField(max_length=1000, widget=forms.Textarea, required=True)

class ClosedQuestionForm(forms.Form):
    question = forms.CharField(max_length=200)

class ClosedQuestionAnswerForm(forms.Form):
    answer = forms.CharField(max_length=200)

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
    open_questions_pks = list(OpenQuestions.objects.filter(poll_id=poll).values_list("pk", flat=True))
    open_answers = OpenAnswers.objects.filter(question_id__in=open_questions_pks)
    closed_questions = ClosedQuestions.objects.filter(poll_id=poll)
    closed_questions_pks = list(ClosedQuestions.objects.filter(poll_id=poll).values_list("pk", flat=True))
    closed_answers = ClosedAnswers.objects.filter(question_id__in=closed_questions_pks)
    respondents_users_ids = PollRespondents.objects.filter(poll_id=poll).values_list("user_id", flat=True)
    respondents = CustomUser.objects.filter(pk__in=respondents_users_ids)
    context = {
        'poll': poll,
        'open_questions': open_questions,
        'open_answers': open_answers,
        'closed_questions': closed_questions,
        'closed_answers': closed_answers,
        'respondents': respondents,
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
def add_open_question(request, poll_id):
    if request.method == 'POST':
        form = OpenQuestionForm(request.POST)
        if form.is_valid():
            poll = get_object_or_404(Polls, pk=poll_id)
            question = OpenQuestions(poll_id=poll, question_text=form.cleaned_data['question'])
            question.save()

    return poll_edit(request, poll_id)

@login_required
def add_closed_question(request, poll_id):
    if request.method == 'POST':
        form = ClosedQuestionForm(request.POST)
        if form.is_valid():
            poll = get_object_or_404(Polls, pk=poll_id)
            question = ClosedQuestions(poll_id=poll, question_text=form.cleaned_data['question'])
            question.save()

    return poll_edit(request, poll_id)

@login_required
def add_answer_to_closed(request, poll_id, question_id):
    if request.method == 'POST':
        form = ClosedQuestionAnswerForm(request.POST)
        if form.is_valid():
            question = get_object_or_404(ClosedQuestions, pk=question_id)
            answer = ClosedAnswers(question_id=question, answer=form.cleaned_data['answer'], times_chosen=0)
            answer.save()

    return poll_edit(request, poll_id)

@login_required
def poll_edit(request, poll_id):
    poll = get_object_or_404(Polls, pk=poll_id)
    if poll.poll_is_finished:
        polls = Polls.objects.filter(poll_owner_id=request.user.id)
        return render(request, 'poll_list.html', {'polls': polls, 'error': 'Cannot modify a finished poll'})

    open_questions = OpenQuestions.objects.filter(poll_id=poll)
    closed_questions = ClosedQuestions.objects.filter(poll_id=poll)
    closed_questions_pks = list(ClosedQuestions.objects.filter(poll_id=poll).values_list("pk", flat=True))
    closed_answers = ClosedAnswers.objects.filter(question_id__in=closed_questions_pks)
    context = {
        'poll': poll,
        'open_questions': open_questions,
        'closed_questions': closed_questions,
        'closed_answers': closed_answers,
        'open_question_form': OpenQuestionForm(),
        'closed_question_form': ClosedQuestionForm(),
        'closed_question_answer_form': ClosedQuestionAnswerForm()
    }
    return render(request, 'poll_edit.html', context)

@login_required
def closed_question_delete_answer(request, answer_id):
    answer = get_object_or_404(ClosedAnswers, pk=answer_id)
    answer.delete()
    return redirect('poll_edit', poll_id=answer.question_id.poll_id.id)

def move_answer_up(request, answer_id):
    answer = get_object_or_404(ClosedAnswers, pk=answer_id)
    answer_above = ClosedAnswers.objects.filter(question_id=answer.question_id, pk__lt=answer_id).order_by('-pk').first()
    if answer_above:
        # switch the contents of the answers
        answer.answer, answer_above.answer = answer_above.answer, answer.answer
        answer.save()
        answer_above.save()
    return redirect('poll_edit', poll_id=answer.question_id.poll_id.id)

def move_answer_down(request, answer_id):
    answer = get_object_or_404(ClosedAnswers, pk=answer_id)
    answer_below = ClosedAnswers.objects.filter(question_id=answer.question_id, pk__gt=answer_id).order_by('pk').first()
    if answer_below:
        # switch the contents of the answers
        answer.answer, answer_below.answer = answer_below.answer, answer.answer
        answer.save()
        answer_below.save()
    return redirect('poll_edit', poll_id=answer.question_id.poll_id.id)
    


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
