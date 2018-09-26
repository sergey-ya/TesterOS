# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-09 14:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testeros', '0008_buildisosettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildIso_Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('process_id', models.IntegerField(null=True)),
                ('user_id', models.IntegerField(null=True)),
                ('setting_id', models.IntegerField(null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('close_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.IntegerField(null=True)),
            ],
        ),
    ]
