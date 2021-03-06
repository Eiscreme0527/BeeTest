# Generated by Django 3.0.2 on 2020-02-04 16:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticate', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='exp_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 2, 5, 8, 53, 49, 507441), verbose_name='Token过期时间'),
        ),
        migrations.AlterField(
            model_name='member',
            name='last_login_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 2, 4, 8, 53, 49, 507441), verbose_name='上次登录时间'),
        ),
    ]
