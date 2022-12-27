# -*- coding: utf-8 -*-
from django.contrib import admin

import users.models
from .models import Polls, OpenQuestions, OpenAnswers, ClosedQuestions, ClosedAnswers
# from project.settings import AUTH_USER_MODEL


@admin.register(Polls)
class PollsAdmin(admin.ModelAdmin):
    list_display = ('id', 'poll_name', 'poll_text')


@admin.register(OpenQuestions)
class UserAnswersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'poll_id', 'answer')
    list_filter = ('user_id', 'poll_id')


@admin.register(OpenAnswers)
class AvailableAnswersAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_id', 'answer', 'times_chosen')
    list_filter = ('question_id',)


@admin.register(ClosedQuestions)
class UserAnswersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'poll_id', 'answer')
    list_filter = ('user_id', 'poll_id')


@admin.register(ClosedAnswers)
class AvailableAnswersAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_id', 'answer', 'times_chosen')
    list_filter = ('question_id',)
