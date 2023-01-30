from django_extensions.management.jobs import HourlyJob
from polls.models import Polls
from django.utils import timezone


class Job(HourlyJob):
    help = "Prune expired polls."

    def execute(self):
        now = timezone.now()
        expired_polls = Polls.objects.filter(poll_end_time__lte=now, poll_is_finished=False)
        for poll in expired_polls:
            poll.poll_is_finished = True
            poll.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully finished poll: {poll.poll_name}'))
