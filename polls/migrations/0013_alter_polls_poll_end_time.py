# Generated by Django 4.1.5 on 2023-01-29 23:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0012_polls_poll_conclusion_alter_polls_poll_end_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='polls',
            name='poll_end_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 5, 23, 52, 53, 829273, tzinfo=datetime.timezone.utc)),
        ),
    ]
