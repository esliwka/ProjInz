from django.db import models
#from project.settings import AUTH_USER_MODEL


class Users(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=50)

    def __str__(self):
        return self.email


class TokenPolls(models.Model):
    token_id = models.CharField(max_length=100)
    answers = models.CharField(max_length=250)

    def __str__(self):
        return self.token_id


class Polls(models.Model):
    poll_name = models.CharField(max_length=250)
    poll_text = models.TextField()
    poll_owner = models.OneToOneField(Users, on_delete=models.CASCADE)

    def __str__(self):
        return self.poll_name


class PollRespondents(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    poll_id = models.ForeignKey(Polls, on_delete=models.CASCADE)


class UserPollStatus(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    poll_id = models.ForeignKey(Polls, on_delete=models.CASCADE)
    answered = models.BooleanField()

    def __str__(self):
        return self.answered


class ClosedQuestions(models.Model):
    poll_id = models.ForeignKey(Polls, on_delete=models.CASCADE)
    question_text = models.TextField()

    def __str__(self):
        return self.question_text


class ClosedAnswers(models.Model):
    question_id = models.ForeignKey(ClosedQuestions, on_delete=models.CASCADE)
    answer = models.TextField()
    times_chosen = models.IntegerField(default=0)

    def __str__(self):
        return self.times_chosen


class OpenQuestions(models.Model):
    poll_id = models.ForeignKey(Polls, on_delete=models.CASCADE)
    answer = models.TextField()
    question_text = models.TextField()

    def __str__(self):
        return self.question_text


class OpenAnswers(models.Model):
    question_id = models.ForeignKey(ClosedQuestions, on_delete=models.CASCADE)
    answer = models.TextField()

    def __str__(self):
        return self.answer
