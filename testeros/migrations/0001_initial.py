# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-28 07:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectSf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_num', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=80)),
                ('comment', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path_to_gl', models.CharField(blank=True, max_length=250, null=True)),
                ('path_to_ro', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Testing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('os_name', models.CharField(blank=True, max_length=20, null=True)),
                ('os_version', models.CharField(blank=True, max_length=20, null=True)),
                ('os_release', models.CharField(blank=True, max_length=20, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('status', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TestJournal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('testing_id', models.IntegerField()),
                ('test_id', models.IntegerField(blank=True, null=True)),
                ('begin_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('status', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Tests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_sf_num', models.IntegerField()),
                ('serial_num', models.IntegerField()),
                ('name', models.CharField(blank=True, max_length=60, null=True)),
                ('prerequisites', models.TextField(blank=True, null=True)),
                ('expected_result', models.TextField(blank=True, null=True)),
                ('test_procedure', models.TextField(blank=True, null=True)),
                ('test_result', models.TextField(blank=True, null=True)),
                ('file1', models.CharField(blank=True, max_length=250, null=True)),
                ('file2', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
    ]
