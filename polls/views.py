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
    TokenPolls
from django.contrib.auth.models import User
from users.models import CustomUser
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db import transaction
from django.db.models import Q
import io
from polls.forms import PolishPasswordChangeForm

class PollForm(forms.Form):
    poll_name = forms.CharField(max_length=200, label='Nazwa ankiety')
    poll_text = forms.CharField(max_length=1000, widget=forms.Textarea, required=False, label='Opis ankiety')

class OpenQuestionForm(forms.Form):
    question = forms.CharField(max_length=1000, widget=forms.Textarea, required=True, label='Pytanie otwarte')

class ClosedQuestionForm(forms.Form):
    question = forms.CharField(max_length=200, required=True, label='Pytanie zamknięte')

class ClosedQuestionAnswerForm(forms.Form):
    answer = forms.CharField(max_length=200 , required=True, label='Odpowiedź')

class AddRespondentForm(forms.Form):
    users = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label='Użytkownik', empty_label=None)
    polls = forms.ModelChoiceField(queryset=Polls.objects.all(), label='Ankieta', empty_label=None, to_field_name='poll_name' )

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
            order = ClosedAnswers.objects.filter(question_id=question).count() + 1
            answer = ClosedAnswers(question_id=question, answer=form.cleaned_data['answer'], times_chosen=0, order=order)
            answer.save()

    return poll_edit(request, poll_id)

@login_required
def delete_poll(request, poll_id):
    poll = get_object_or_404(Polls, pk=poll_id)
    poll.delete()
    return redirect('poll_list')

@login_required
def delete_closed_question(request, question_id):
    question = get_object_or_404(ClosedQuestions, pk=question_id)
    question.delete()
    return redirect('poll_edit', poll_id=question.poll_id.id)

@login_required
def delete_open_question(request, question_id):
    question = get_object_or_404(OpenQuestions, pk=question_id)
    question.delete()
    return redirect('poll_edit', poll_id=question.poll_id.id)

# @login_required
# def delete_answer(request, answer_id):
#     answer = get_object_or_404(ClosedAnswers, pk=answer_id)
#     answer.delete()
#     return redirect('poll_edit', poll_id=answer.question_id.poll_id.id)

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

@transaction.atomic
@login_required
def closed_question_delete_answer(request, answer_id):
    answer = get_object_or_404(ClosedAnswers, pk=answer_id)
    closed_question = ClosedQuestions.objects.filter(poll_id=answer.question_id.poll_id.id)
    answer.delete()
    remaining_answers = ClosedAnswers.objects.filter(question_id=answer.question_id).order_by('order')
    if len(remaining_answers)>0:
        for i in range(0,len(remaining_answers)):
            if remaining_answers[i].order != i+1:
                remaining_answers[i].order=i+1
                remaining_answers[i].save()
    return redirect('poll_edit', poll_id=answer.question_id.poll_id.id)



@transaction.atomic
@login_required
def move_answer_up(request, answer_id):
    answer = get_object_or_404(ClosedAnswers, pk=answer_id)
    answers = ClosedAnswers.objects.filter(question_id=answer.question_id)
    current_index = answers.filter(pk=answer_id).first().order
    if current_index == 1:
        return redirect('poll_edit', poll_id=answer.question_id.poll_id.id)
    else:
        prev_answer = answers.filter(order=current_index - 1).first()
        answer.order, prev_answer.order = prev_answer.order, answer.order
        answer.save()
        prev_answer.save()
    return redirect('poll_edit', poll_id=answer.question_id.poll_id.id)

@transaction.atomic
@login_required
def move_answer_down(request, answer_id):
    answer = get_object_or_404(ClosedAnswers, pk=answer_id)
    answers = ClosedAnswers.objects.filter(question_id=answer.question_id)
    current_index = answers.filter(pk=answer_id).first().order
    if current_index == answers.count():
        return redirect('poll_edit', poll_id=answer.question_id.poll_id.id)
    else:
        next_answer = answers.filter(order=current_index + 1).first()
        answer.order, next_answer.order = next_answer.order, answer.order
        answer.save()
        next_answer.save()
    return redirect('poll_edit', poll_id=answer.question_id.poll_id.id)

@login_required
def add_respondent(request):
    if request.method == 'POST':
        first_user = CustomUser.objects.first()
        first_poll = Polls.objects.first()
        form = AddRespondentForm(request.POST, initial={'users': first_user, 'polls': first_poll} if first_user and first_poll else None)

        if form.is_valid():
            poll = Polls.objects.get(id=form.cleaned_data['polls'].pk)
            user = CustomUser.objects.get(id=form.cleaned_data['users'].pk)
            poll_respondent = PollRespondents(poll_id=poll, user_id=user)
            poll_respondent.save()
            return redirect('poll_list')
    else:
        form = AddRespondentForm()
        form.fields['polls'].queryset = Polls.objects.filter(poll_owner_id=request.user.id)

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
    is_users = Q(user_id=request.user)
    is_answered = Q(answered=True)
    is_not_answered = Q(answered=False)
    answered_polls_ids = PollRespondents.objects.filter(is_users & is_answered).values_list("poll_id")
    not_answered_polls_ids = PollRespondents.objects.filter(is_users & is_not_answered).values_list("poll_id")
    user_poll_ids = Polls.objects.filter(poll_owner_id_id=request.user).values_list("id")
    user_polls = Polls.objects.filter(id__in=user_poll_ids)
    answered_polls = Polls.objects.filter(id__in=answered_polls_ids)
    not_answered_polls = Polls.objects.filter(id__in=not_answered_polls_ids)
    context = {
        'user': request.user,
        'hashed_email': hashed_email,
        'form': form,
        'answered_polls': answered_polls,
        'not_answered_polls': not_answered_polls,
        'user_polls': user_polls,
    }
    return render(request, 'user_home.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PolishPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Hasło zostało zmienione!')
            return redirect('user_home')
        else:
            messages.error(request, 'Proszę poprawić błędy poniżej.')
            return redirect('change_password')
    else:
        form = PolishPasswordChangeForm(request.user)
        args = {'form': form}
        return render(request, 'change_password.html', args)


def index(request):
    if request.user.is_authenticated:
        return redirect('user_home')
    return render(request, 'index.html')

@login_required
def update_poll_name(request, poll_id, new_name):
    poll = get_object_or_404(Polls, pk=poll_id)
    if request.method == 'POST':
        # new_name = request.POST.get('new_name')
        poll.poll_name = new_name
        poll.save()
        return redirect('poll_edit', poll_id=poll.id)
    else:
        return render(request, 'poll_edit.html', {'poll': poll})

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
            return render(request, 'login.html', {'error': 'Złe dane logowania'})
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('index')

