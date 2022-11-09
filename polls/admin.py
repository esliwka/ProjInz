# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import UserData, Polls, UserAnswers, AvailableAnswers


@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_data')


@admin.register(Polls)
class PollsAdmin(admin.ModelAdmin):
    list_display = ('id', 'poll_name', 'poll_text')


@admin.register(UserAnswers)
class UserAnswersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'poll_id', 'answer')
    list_filter = ('user_id', 'poll_id')


@admin.register(AvailableAnswers)
class AvailableAnswersAdmin(admin.ModelAdmin):
    list_display = ('id', 'poll_id', 'answer', 'times_chosen')
    list_filter = ('poll_id',)
