# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-17 09:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testeros', '0011_auto_20180711_1015'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buildiso_log',
            name='setting_id',
        ),
        migrations.AddField(
            model_name='buildiso_log',
            name='inform',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
