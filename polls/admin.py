from django.contrib import admin
from .models import Polls, PollRespondents, ClosedQuestions, OpenQuestions, TokenPolls, ClosedAnswers, OpenAnswers, UserPollStatus

class PollsAdmin(admin.ModelAdmin):
    list_display = ['poll_name', 'poll_text', 'poll_owner_id']
    list_filter = ['poll_name','poll_owner_id']

class PollRespondentsAdmin(admin.ModelAdmin):
    list_display = ['poll_id', 'user_id']
    list_filter = ['poll_id', 'user_id']

class ClosedQuestionsAdmin(admin.ModelAdmin):
    list_display = ['poll_id', 'question_text']
    list_filter = ['poll_id']

class OpenQuestionsAdmin(admin.ModelAdmin):
    list_display = ['poll_id', 'question_text']
    list_filter = ['poll_id']

class TokenPollsAdmin(admin.ModelAdmin):
    list_display = ['token_id', 'answers']
    list_filter = ['token_id']

class ClosedAnswersAdmin(admin.ModelAdmin):
    list_display = ['question_id', 'answer', 'times_chosen']
    list_filter = ['question_id']

class OpenAnswersAdmin(admin.ModelAdmin):
    list_display = ['question_id', 'answer']
    list_filter = ['question_id']

class UserPollStatusAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'poll_id', 'answered']
    list_filter = ['user_id', 'poll_id']

admin.site.register(Polls, PollsAdmin)
admin.site.register(PollRespondents, PollRespondentsAdmin)
admin.site.register(ClosedQuestions, ClosedQuestionsAdmin)
admin.site.register(OpenQuestions, OpenQuestionsAdmin)
admin.site.register(TokenPolls, TokenPollsAdmin)
admin.site.register(ClosedAnswers, ClosedAnswersAdmin)
