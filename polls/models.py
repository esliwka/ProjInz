from django.db import models
from django.utils import timezone
import datetime

class Polls(models.Model):
    poll_owner_id = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    poll_name = models.CharField(max_length=255)
    poll_text = models.TextField()
    poll_is_finished = models.BooleanField(default=False)
    poll_end_time = models.DateTimeField(default=timezone.now() + datetime.timedelta(days=7))
    poll_is_published = models.BooleanField(default=False)
    class Meta:
        verbose_name = "Polls"
        verbose_name_plural = "Polls"
 
    def __str__(self):
        return self.poll_name

class PollRespondents(models.Model):
    poll_id = models.ForeignKey('Polls', on_delete=models.CASCADE)
    user_id = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    answered = models.BooleanField(default=False)
    class Meta:
        verbose_name = "PollRespondents"
        verbose_name_plural = "PollRespondents"

class ClosedQuestions(models.Model):
    poll_id = models.ForeignKey('Polls', on_delete=models.CASCADE)
    question_text = models.TextField()
    class Meta:
        verbose_name = "ClosedQuestions"
        verbose_name_plural = "ClosedQuestions"

class OpenQuestions(models.Model):
    poll_id = models.ForeignKey('Polls', on_delete=models.CASCADE)
    question_text = models.TextField()
    class Meta:
        verbose_name = "OpenQuestions"
        verbose_name_plural = "OpenQuestions"    

class TokenPolls(models.Model):
    token_id = models.CharField(max_length=255)
    answers = models.TextField()
    class Meta:
        verbose_name = "TokenPolls"
        verbose_name_plural = "TokenPolls"

class ClosedAnswers(models.Model):
    question_id = models.ForeignKey('ClosedQuestions', on_delete=models.CASCADE)
    answer = models.TextField()
    times_chosen = models.IntegerField()
    order = models.IntegerField(default=0)
    class Meta:
        ordering = ['order']
        verbose_name = "ClosedAnswers"
        verbose_name_plural = "ClosedAnswers"
    def __str__(self):
        return self.answer

class OpenAnswers(models.Model):
    question_id = models.ForeignKey('OpenQuestions', on_delete=models.CASCADE)
    answer = models.TextField()
    class Meta:
        verbose_name = "OpenAnswers"
        verbose_name_plural = "OpenAnswers"

class UserPollStatus(models.Model):
    user_id = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    poll_id = models.ForeignKey('Polls', on_delete=models.CASCADE)
    answered = models.BooleanField(default=False)
    class Meta:
        verbose_name = "UserPollStatus"
        verbose_name_plural = "UserPollStatus"