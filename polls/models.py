from django.db import models

class Polls(models.Model):
    poll_owner_id = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    poll_name = models.CharField(max_length=255)
    poll_text = models.TextField()
    poll_is_finished = models.BooleanField(default=False)
    class Meta:
        verbose_name = "Polls"
        verbose_name_plural = "Polls"    

class PollRespondents(models.Model):
    poll_id = models.ForeignKey('Polls', on_delete=models.CASCADE)
    user_id = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
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
    class Meta:
        verbose_name = "ClosedAnswers"
        verbose_name_plural = "ClosedAnswers"

class OpenAnswers(models.Model):
    question_id = models.ForeignKey('OpenQuestions', on_delete=models.CASCADE)
    answer = models.TextField()
    class Meta:
        verbose_name = "OpenAnswers"
        verbose_name_plural = "OpenAnswers"

class UserPollStatus(models.Model):
    user_id = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    poll_id = models.ForeignKey('Polls', on_delete=models.CASCADE)
    answered = models.BooleanField()
    class Meta:
        verbose_name = "UserPollStatus"
        verbose_name_plural = "UserPollStatus"