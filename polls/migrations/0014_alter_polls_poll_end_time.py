# Generated by Django 4.1.5 on 2023-01-30 18:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0013_alter_polls_poll_end_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='polls',
            name='poll_end_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 6, 18, 33, 23, 692612, tzinfo=datetime.timezone.utc)),
        ),
    ]