from django.db import models
from project.settings import AUTH_USER_MODEL


class UserData(models.Model):
    user_data = models.CharField(max_length=250)

    def __str__(self):
        return self.user_data


class Polls(models.Model):
    poll_name = models.CharField(max_length=250)
    poll_text = models.TextField()

    def __str__(self):
        return self.poll_name


class UserAnswers(models.Model):
    user_id = models.ForeignKey(UserData, on_delete=models.CASCADE)
    poll_id = models.ForeignKey(Polls, on_delete=models.CASCADE)
    answer = models.TextField()

    def __str__(self):
        return self.answer


class AvailableAnswers(models.Model):
    poll_id = models.ForeignKey(Polls, on_delete=models.CASCADE)
    answer = models.TextField()
    times_chosen = models.IntegerField(default=0)

    def __str__(self):
        return self.answer
