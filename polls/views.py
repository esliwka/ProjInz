from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from project.encrypt_util import sec_hash, generate_user_id_token
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse, FileResponse
from django import forms
from polls.models import PollRespondents, Polls, ClosedQuestions, OpenQuestions, ClosedAnswers, OpenAnswers, \
    TokenPolls, UserPollStatus
from django.contrib.auth.models import User
from users.models import CustomUser
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db import transaction
from django.db.models import Q, F, Count
import io
from polls.forms import PolishPasswordChangeForm, UserCreationForm
import json
from django.utils import timezone
import datetime
import pandas as pd
from django.contrib.admin.views.decorators import staff_member_required

class OpenQuestionForm(forms.Form):
    question = forms.CharField(max_length=1000, widget=forms.Textarea, required=True, label='Dodaj pytanie otwarte')

class ClosedQuestionForm(forms.Form):
    question = forms.CharField(max_length=200, required=True, label='Dodaj pytanie zamknięte')

class ClosedQuestionAnswerForm(forms.Form):
    answer = forms.CharField(max_length=200 , required=True, label='Dodaj odpowiedź')

class AddRespondentForm(forms.Form):
    users = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label='Użytkownik', empty_label=None)
    polls = forms.ModelChoiceField(queryset=Polls.objects.all(), label='Ankieta', empty_label=None, to_field_name='poll_name' )

class VerifyTokenForm(forms.Form):
    user_token = forms.CharField(label='Wprowadź token', max_length=66, min_length=66, required=True)

def user_verify_integrity(request):
    form = VerifyTokenForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user_token = form.cleaned_data['user_token']
            request.session['user_token2'] = user_token
            # return redirect('poll_results', user_token=user_token)
            return render(request, 'poll_results.html', {'user_token': user_token})
    return render(request, 'user_verify_integrity.html', {'form': form})


@login_required
def poll_results(request):
    user_token = request.POST.get('user_token')
    # user_token = request.session.get('user_token2', None)
    if user_token:
        token_id = user_token[:10]
        user_email = request.user.email
        user_token_hash = user_token[10:]
        #TokenPolls matching query does not exist.
        if not TokenPolls.objects.filter(token_id=token_id):
            return render(request, 'user_verify_integrity.html', {'error': 'Błąd: Nieprawidłowy token. Skontaktuj się z administratorem.'})
        else:
            token = TokenPolls.objects.get(token_id=token_id)
        
        open_answers = []
        closed_answers = []
        poll_id = ''
        for key, value in json.loads(token.answers).items():
                        token_poll_id, question_type, question_id = key.split('_')
                        poll_id = token_poll_id
                        break
        database_hash = sec_hash(user_email + sec_hash(str(token_id)+str(poll_id)+str(token.answers))) 

        
        
        if database_hash == user_token_hash:
            if Polls.objects.filter(pk=token_poll_id):
                poll = Polls.objects.get(pk=token_poll_id)
                if not poll.poll_is_finished:
                    return render(request, 'user_verify_integrity.html', {'error': 'Ankieta nie została jeszcze zamknięta.'})
                else:
                    additional = json.loads(token.answers)
                    for key, value in json.loads(token.answers).items():
                        token_poll_id, question_type, question_id = key.split('_')
                                
                        if question_type == 'open':
                            open_answers.append(f'Pytanie: {value["question"]},\n Odpowiedź: {value["answer"]}')
                        elif question_type == 'closed':
                            closed_answers.append(f'Pytanie: {value["question"]},\n Odpowiedź: {value["answer"]}')

                         
                        else:
                            return render(request, 'user_verify_integrity.html', {'error': 'Błąd: Nieprawidłowy typ pytania. Skontaktuj się z administratorem.'})
                        
                        user_message = 'Weryfikacja danych przebiegła pomyślnie. \n Dane w bazie danych są zgodne z danymi przesłanymi przez użytkownika.'
                        user_fail_message = 'Weryfikacja danych nie powiodła się. \n Dane w bazie danych nie są zgodne z danymi przesłanymi przez użytkownika.'
                        return render(request, 'poll_results.html', {'additional':additional, 'open_answers':open_answers, 'closed_answers':closed_answers, 'poll_name': poll.poll_name, 'user_message': user_message})
            else:
                messages.error(request, f"Twoje dane zostały naruszone w bazie danych. Administrator został powiadomiony.\n")
                return render(request, 'user_verify_integrity.html', {'error': 'Brak takiej ankiety w bazie, została zmieniona lub usunięta. Administrator został powiadomiony.'})
        else:
            return render(request, 'user_verify_integrity.html', {'error': 'Weryfikacja danych nie powiodła się. \n Dane w bazie danych nie są zgodne z danymi przesłanymi przez użytkownika. Administrator został powiadomiony.'})
    else:
        return render(request, 'user_verify_integrity.html', {'error': 'Nieprawidłowy token. Upewnij się, że wprowadzono poprawny token.'})

@login_required
def poll_response(request):
    # kto ma dostęp do ankiety
    user_polls = PollRespondents.objects.filter(user_id=request.user)
    user_polls_pks = list(user_polls.values_list("poll_id", flat=True))
    polls = Polls.objects.filter(pk__in=user_polls_pks)
    # sprawdzenie czy ankietę można już wypełnić i usuniecie z listy ankiet, których nie można wypelnic
    for poll in polls:
        if poll.poll_is_finished:
            polls = polls.exclude(pk=poll.pk)

    if request.method == 'POST':
        poll_id = request.POST.get('poll_id')
        selected_poll = get_object_or_404(Polls, pk=poll_id)
        closed_questions = ClosedQuestions.objects.filter(poll_id=poll_id)
        open_questions = OpenQuestions.objects.filter(poll_id=poll_id)
        poll_data = {}
        for question in closed_questions:
            selected_answer = request.POST.get(f'closed_question_{question.id}')
            # selected_answer = ClosedAnswers.objects.get(id=selected_answer)         
            if not selected_answer:
                messages.error(request, "Proszę odpowiedzieć na wszystkie pytania zamknięte.")
                return redirect('poll_response', poll_id=poll_id)

            answer = ClosedAnswers.objects.get(id=selected_answer)
            poll_data[f'{poll_id}_closed_{question.id}'] = {'question': question.question_text, 'answer': answer.answer}

        for question in open_questions:
            answer = request.POST.get(f'open_question_{question.id}')
            if not answer:
                messages.error(request, "Proszę odpowiedzieć na wszystkie pytania otwarte.")
                return redirect('poll_response', poll_id=poll_id)
            poll_data[f'{poll_id}_open_{question.id}'] = {'question': question.question_text, 'answer': answer}
        
        if poll_data:
            user_email = request.user.email
            json_data = json.dumps(poll_data)
            user_token = generate_user_id_token()
            
            json_data_hash = sec_hash(str(user_token) + str(poll_id) + str(json_data))
            user_data_hash = sec_hash(user_email + json_data_hash)
            request.session[user_email.split('@')[0]+user_email.split('@')[1].split('.')[0]] = user_token
            if json_data_hash and json_data and user_token:
                cache.set(user_token, [json_data_hash, json_data])
            else:
                messages.error(request, "Wystąpił błąd podczas przetwarzania danych.")
                return redirect('poll_response', poll_id=poll_id)

            TokenPolls.objects.create(token_id=user_token, answers=json_data, answers_hash=json_data_hash)
            UserPollStatus.objects.filter(user_id=request.user, poll_id=poll_id).update(answered=True)
            PollRespondents.objects.filter(user_id=request.user, poll_id=poll_id).update(answered=True)
            
            test_variables = []
            hashes_list = []
            poll_respondents = PollRespondents.objects.filter(poll_id=poll_id)
            poll_respondents_pks = list(poll_respondents.values_list("user_id", flat=True))
            users = CustomUser.objects.filter(pk__in=poll_respondents_pks)
            users_pks = list(users.values_list("id", flat=True))
            test_variables.append(f'users_pks = {users_pks}')
            user_poll_status = PollRespondents.objects.filter(user_id__in=users_pks, poll_id=poll_id)
            # for id in users_pks:
            #     test_variables.append( f'{id} = {PollRespondents.objects.filter(user_id__in= users_pks , poll_id=poll_id).values_list("answered", flat=True)}'             
            #          )
            user_poll_status_pks = list(user_poll_status.values_list("answered", flat=True))
            test_variables.append(f'user_poll_status_pks = {user_poll_status_pks}')
            
            #user_poll_status_pks contains strings of numbers and users_pks contains True/False how to compare them? if False dont count it and if True count it
            test_variables.append(f'len(user_poll_status_pks) = {len([x for x in users_pks if x])}')
            test_variables.append(f'len([i for i in users_pks if i == True]) = {len([x for x in user_poll_status_pks if x])}')
            if len([x for x in user_poll_status_pks if x]) == len([x for x in users_pks if x]):
                Polls.objects.filter(pk=poll_id).update(poll_is_finished=True)
                
                test_variables.append(f'{poll_id} = poll_is_finished')
                
            if Polls.objects.get(pk=poll_id).poll_is_finished:
                token_list = []
                
                for token in TokenPolls.objects.filter(poll_ended=False):
                    # test_variables.append(token.token_id)
                    
                    json_data = json.loads(token.answers)
                    for key, value in json_data.items():
                        token_poll_id, question_type, question_id = key.split('_')
                        test_variables.append(token_poll_id)
                        test_variables.append(question_type)
                        test_variables.append(question_id)
                        if token_poll_id == poll_id:
                            if question_type == 'open':
                                open_question = OpenQuestions.objects.get(pk=question_id)
                                OpenAnswers.objects.create(
                                 question_id=open_question,
                                  answer=value['answer'])
                            elif question_type == 'closed':
                                closed_question = ClosedQuestions.objects.get(pk=question_id)
                                ClosedAnswers.objects.filter(
                                 question_id=closed_question,
                                  answer=value['answer']).update(times_chosen=F('times_chosen')+1)
                            # token.poll_ended = True
                            # token.save()
                            token_list.append(token.token_id)
                
                token_list = list(set(token_list))
                for item in token_list:
                    # hashes_list.append([item, cache.get(item)[0]])
                    # if TokenPolls.objects.get(token_id=item).answers_hash == cache.get(item)[0]:
                        x = cache.get(item, None)
                        y = TokenPolls.objects.get(token_id=item).answers
                        y = sec_hash(str(item) + str(poll_id) + str(y))
                        if x:
                            if x[0] != y:
                                hashes_list.append(TokenPolls.objects.get(token_id=item).answers)
                                if x:
                                    TokenPolls.objects.filter(token_id=item).update(answers_hash=x[0], answers=x[1])
                                
                                    #then delete the TokenPolls object from database
                            # cache.delete(item)
                        
                TokenPolls.objects.filter(token_id__in = token_list ).update(poll_ended=True)
                if hashes_list:
                    Polls.objects.filter(pk=poll_id).update(poll_conclusion=f"'Weryfikacja ankiety niepoprawna. \n Odpowiedzi użytkowników nie zgadzają się z odpowiedziami zapisanymi w bazie danych. \n Zmienione odpowiedzi to: {hashes_list}")
                else:
                    Polls.objects.filter(pk=poll_id).update(poll_conclusion="Ankieta została zakończona. Wszystkie odpowiedzi zostały poprawnie zweryfikowane.")
                    
                return render(request, 'poll_response_success.html', {'poll_id': poll_id, 'json_data_hash': user_token+user_data_hash,
                'token_id': user_token }) #, 'token_list': token_list})
            else:
                return render(request, 'poll_response_success.html', {'poll_id': poll_id, 'json_data_hash': user_token+user_data_hash,
                'token_id': user_token})

    # if request.method == 'POST':
    #     poll_id = request.POST.get('poll_id')
    #     selected_poll = get_object_or_404(Polls, pk=poll_id)
    #     closed_questions = ClosedQuestions.objects.filter(poll_id=poll_id)
    #     open_questions = OpenQuestions.objects.filter(poll_id=poll_id)
    #     poll_data = {}
    #     for question in closed_questions:
    #         selected_answer = request.POST.get(f'closed_question_{question.id}')
    #         if selected_answer:
    #             answer = ClosedAnswers.objects.get(pk=selected_answer)
    #             poll_data[f'{poll_id}'] = {'{question.id}': question.question_text, 'answer': selected_answer.answer}
                
    #     for question in open_questions:
    #         answer = request.POST.get(f'open_question_{question.id}')
    #         if answer:
    #             OpenAnswers.objects.create(question_id=question, answer=answer)
    #             poll_data[f'{poll_id}_{question.id}'] = {'question': question.question_text, 'answer': answer}
    #     if poll_data:
    #         user_email = request.user.email
    #         json_data = json.dumps(poll_data)
    #         TokenPolls.objects.create(token_id=user_email, answers=json_data)
    #         UserPollStatus.objects.filter(user_id=request.user, poll_id=poll_id).update(answered=True)
    #         return redirect('poll_response_success')
    #     else:
    #         messages.error(request, 'Please select at least one closed question and answer one open question.')
    #         return redirect('poll_response')
        
    if request.method == 'GET':
        poll_id = request.GET.get('poll_id')
        request.session['poll_id'] = poll_id
        if not poll_id:
            poll_id = request.POST.get('poll_id')
        if not poll_id:
            if polls:
                poll_id = polls[0].id
        
        current_poll = Polls.objects.get(pk=poll_id)
        closed_questions = ClosedQuestions.objects.filter(poll_id=poll_id)
        open_questions = OpenQuestions.objects.filter(poll_id=poll_id)

        # Render the template with the polls, closed questions, and open questions
        return render(request, 'poll_response.html', {'polls': polls, 'closed_questions': closed_questions,
         'open_questions': open_questions,'poll_id':poll_id,'current_poll':current_poll})


@login_required
def poll_response_download(request, poll_id):
    user_email = request.user.email
    token_id = request.session[user_email.split('@')[0]+user_email.split('@')[1].split('.')[0]]
    if token_id:
        json_data = cache.get(token_id)
        if json_data:
            json_data = json_data[1]
            json_data_hash = sec_hash(str(token_id) + str(poll_id) + str(json_data))
            user_data_hash = sec_hash(request.user.email + json_data_hash)
            hash_data = str(token_id) + str(user_data_hash)
            # request.session.pop('user_token', None)
            file = io.BytesIO(hash_data.encode())
            poll_name = Polls.objects.get(id=poll_id).poll_name
            user_first_and_last_name = request.user.first_name[0:1] +'_'+ request.user.last_name
            response = FileResponse(file, content_type='text/plain')
            
            response['Content-Disposition'] = f'attachment; filename="potwierdzenie_wypelnienia_({poll_name[0:10]})_{user_first_and_last_name}.txt"'
            return response
        else:
            return HttpResponse('Nie znaleziono danych do pobrania')
    else:
        return HttpResponse('Nie znaleziono danych do pobrania.')

    hash_data = token_id + sec_hash(request.user.email + json_data)
    # request.session.pop('user_token', None)
    file = io.BytesIO(hash_data.encode())
    poll_name = Polls.objects.get(id=poll_id).poll_name
    user_first_and_last_name = request.user.first_name +'_'+ request.user.last_name
    response = FileResponse(file, content_type='text/plain')
    
    response['Content-Disposition'] = f'attachment; filename="potwierdzenie_wypelnienia_({poll_name})_{user_first_and_last_name}.txt"'
    return response

@login_required
def open_question_responses_download(request, question_id):
    answers = OpenAnswers.objects.filter(question_id=question_id)
    question_text = OpenQuestions.objects.get(id=question_id).question_text[0:20]
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="odpowiedzi_na_pytanie_otwarte_{question_text}.txt"'
    for answer in answers:
        response.write(answer.answer + '\n')
    return response


@login_required
def poll_response_success(request, poll_id, json_data):
    token = request.session.get('token_id')
    json_data = cache.get(token) 
    hash_data = token + sec_hash(request.user.email + json_data)
    
    # request.session.pop('user_token', None)
    return render(request, 'poll_response_success.html', {'poll_id': poll_id, 'json_data_hash': hash_data})


class PollForm(forms.Form):
    poll_name = forms.CharField(max_length=200, label='Nazwa ankiety', widget=forms.Textarea(attrs={'rows': 1, 'cols': 40}))
    poll_text = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}), required=False, label='Opis ankiety')

class OpenQuestionForm(forms.Form):
    question = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}), required=True, label='Dodaj pytanie otwarte')

class ClosedQuestionForm(forms.Form):
    question = forms.CharField(max_length=200, required=True, label='Dodaj pytanie zamknięte')

class ClosedQuestionAnswerForm(forms.Form):
    answer = forms.CharField(max_length=200 , required=True, label='Dodaj odpowiedź')

class AddRespondentForm(forms.Form):
    users = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label='Użytkownik', empty_label=None)
    polls = forms.ModelChoiceField(queryset=Polls.objects.all(), label='Ankieta', empty_label=None ,to_field_name='poll_name' )

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


class ButtonAddRespondentForm(forms.Form):
    users = forms.ModelChoiceField(queryset=CustomUser.objects.all())

@login_required
def button_add_respondent(request, poll_id):
    poll = get_object_or_404(Polls, pk=poll_id)

    if request.method == 'POST':
        form = ButtonAddRespondentForm(request.POST)
        user_id = request.POST.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        poll_respondent = PollRespondents(poll_id=poll, user_id=user)
        poll_respondent.save()
         
        
        return redirect('poll_detail', poll_id=poll_id)
        
    else:
        form = ButtonAddRespondentForm()
        form.fields['users'].queryset = CustomUser.objects.exclude(id=request.user.id)

    return redirect('poll_detail', poll_id=poll_id)

@login_required
def button_add_respondent_edit(request, poll_id):
    poll = get_object_or_404(Polls, pk=poll_id)

    if request.method == 'POST':
        form = ButtonAddRespondentForm(request.POST)
        user_id = request.POST.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        poll_respondent = PollRespondents(poll_id=poll, user_id=user)
        poll_respondent.save()
         
        
        return redirect('poll_edit', poll_id=poll_id)
        
    else:
        form = ButtonAddRespondentForm()
        form.fields['users'].queryset = CustomUser.objects.exclude(id=request.user.id)

    return redirect('poll_edit', poll_id=poll_id)


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
    # create a dict of all respondents and if they answered the poll
    respondents_dict = {}
    for user_id in respondents_users_ids:
        this_respond = PollRespondents.objects.get(poll_id=poll, user_id = user_id)
        if this_respond.answered == True:
            respondents_dict[int(user_id)] = True
        else:
            respondents_dict[int(user_id)] = False

    users = CustomUser.objects.all()
    context = {
        'poll': poll,
        'open_questions': open_questions,
        'open_answers': open_answers,
        'closed_questions': closed_questions,
        'closed_answers': closed_answers,
        'respondents': respondents,
        'users': users,
        'respondents_dict': respondents_dict,
        
    }
    return render(request, 'poll_detail.html', context)



@staff_member_required
@login_required
def create_poll(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        

        if form.is_valid():
            end_time_string = request.POST.get('poll_end_time')
            tz = timezone.get_current_timezone()
            end_time = datetime.datetime.strptime(end_time_string, '%m/%d/%Y %I:%M %p')
            end_time = timezone.make_aware(end_time, tz)
            if end_time < timezone.now():
                messages.error(request, "Data zakończenia ankiety nie może być wcześniejsza niż aktualna.")
                # redirect('create_poll', form=form)
                return render(request, 'create_poll.html', {'form': form, 'error': 'Data zakończenia ankiety nie może być wcześniejsza niż aktualna.'})
            poll = Polls(poll_name=form.cleaned_data['poll_name'], poll_text=form.cleaned_data['poll_text'],
                         poll_end_time=end_time, poll_owner_id=request.user)
            poll.save()
            return redirect('user_home')
    else:
        form = PollForm()
    return render(request, 'create_poll.html', {'form': form})


@transaction.atomic
@login_required
def add_open_question(request, poll_id):
    if request.method == 'POST':
        form = OpenQuestionForm(request.POST)
        if form.is_valid():
            poll = get_object_or_404(Polls, pk=poll_id)
            question = OpenQuestions(poll_id=poll, question_text=form.cleaned_data['question'])
            question.save()

    return poll_edit(request, poll_id)

@transaction.atomic
@login_required
def add_closed_question(request, poll_id):
    if request.method == 'POST':
        form = ClosedQuestionForm(request.POST)
        if form.is_valid():
            poll = get_object_or_404(Polls, pk=poll_id)
            question = ClosedQuestions(poll_id=poll, question_text=form.cleaned_data['question'])
            question.save()

    return poll_edit(request, poll_id)

@transaction.atomic
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
    return redirect('user_home')

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
        return render(request, 'poll_list.html', {'polls': polls, 'error': 'Nie można edytować zakończonej ankiety'})
    if poll.poll_is_published:
        polls = Polls.objects.filter(poll_owner_id=request.user.id)
        return render(request, 'poll_list.html', {'polls': polls, 'error': 'Nie można edytować opublikowanej ankiety'})
    open_questions = OpenQuestions.objects.filter(poll_id=poll)
    closed_questions = ClosedQuestions.objects.filter(poll_id=poll)
    closed_questions_pks = list(ClosedQuestions.objects.filter(poll_id=poll).values_list("pk", flat=True))
    closed_answers = ClosedAnswers.objects.filter(question_id__in=closed_questions_pks)
    respondents_users_ids = PollRespondents.objects.filter(poll_id=poll).values_list("user_id", flat=True)
    respondents = CustomUser.objects.filter(pk__in=respondents_users_ids)
    respondents_dict = {}
    for user_id in respondents_users_ids:
        this_respond = PollRespondents.objects.get(poll_id=poll, user_id = user_id)
        if this_respond.answered == True:
            respondents_dict[int(user_id)] = True
        else:
            respondents_dict[int(user_id)] = False
    users = CustomUser.objects.all()
    context = {
        'poll': poll,
        'users': users,
        'respondents': respondents,
        'open_questions': open_questions,
        'respondents_dict': respondents_dict,
        'closed_questions': closed_questions,
        'closed_answers': closed_answers,
        'open_question_form': OpenQuestionForm(),
        'closed_question_form': ClosedQuestionForm(),
        'closed_question_answer_form': ClosedQuestionAnswerForm()
    }
    # request.session['poll_id'] = poll_id
    return render(request, 'poll_edit.html', context)

@login_required
def publish_poll(request, poll_id):
    # poll_id = request.session['poll_id']
    poll = get_object_or_404(Polls, pk=poll_id)
    poll.poll_is_published = True
    poll.save()
    if request.user.is_authenticated:
        return redirect('user_home')
    else:
        return redirect('index')

@login_required
def unpublish_poll(request, poll_id):
    poll = get_object_or_404(Polls, pk=poll_id)
    poll.poll_is_published = False
    poll.save()
    if request.user.is_authenticated:
        return redirect('poll_detail', poll_id=poll_id)
    else:
        return redirect('index')


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
def user_home(request):
    # form = PasswordChangeForm(request.user)
    hashed_email = sec_hash(request.user.email)
    is_users = Q(user_id=request.user)
    is_answered = Q(answered=True)
    is_not_answered = Q(answered=False)
    is_published = Q(poll_is_published=True)
    answered_polls_ids = PollRespondents.objects.filter(is_users & is_answered).values_list("poll_id")
    not_answered_polls_ids = PollRespondents.objects.filter(is_users & is_not_answered).values_list("poll_id")
    user_poll_ids = Polls.objects.filter(poll_owner_id_id=request.user).values_list("id")
    user_polls = Polls.objects.filter(id__in=user_poll_ids)
    answered_polls = Polls.objects.filter(id__in=answered_polls_ids)
    not_answered_polls = Polls.objects.filter(id__in=not_answered_polls_ids).filter(is_published)
    context = {
        'user': request.user,
        'hashed_email': hashed_email,
        # 'form': form,
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
            return render(request, 'change_password.html', {'form': form})
    else:
        form = PolishPasswordChangeForm(request.user)
        return render(request, 'change_password.html', {'form': form})

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

from django.contrib.auth.hashers import make_password
def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            
            user = form.save()
            login(request, user)
            return redirect('user_home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
    