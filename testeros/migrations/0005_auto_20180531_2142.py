# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-31 18:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testeros', '0004_auto_20180531_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionlog',
            name='replace',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='actionlog',
            name='stapel',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='actionlog',
            name='status',
            field=models.IntegerField(null=True),
        ),
    ]
