from django.db import models
from django.contrib.auth.models import User



class UserProfile(models.Model):
    username = models.CharField(max_length=150, blank=True, unique=True)
    note = models.TextField(blank=True)


class ObjectSf(models.Model):
    serial_num = models.IntegerField(unique=True)
    name = models.CharField(max_length=80)
    comment = models.TextField(blank=True, null=True)


class Tests(models.Model):
    object_sf_num = models.IntegerField()
    serial_num = models.IntegerField()
    name = models.CharField(max_length=60, blank=True, null=True)
    prerequisites = models.TextField(blank=True, null=True)
    expected_result = models.TextField(blank=True, null=True)
    test_procedure = models.TextField(blank=True, null=True)
    test_result = models.TextField(blank=True, null=True)
    file1 = models.CharField(max_length=250, blank=True, null=True)
    file2 = models.CharField(max_length=250, blank=True, null=True)


class Testing(models.Model):
    begin_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    os_name = models.CharField(max_length=20, blank=True, null=True)
    os_version = models.CharField(max_length=20, blank=True, null=True)
    os_release = models.CharField(max_length=20, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    status = models.IntegerField()


class TestJournal(models.Model):
    testing_id = models.IntegerField()
    test_id = models.IntegerField(blank=True, null=True)
    begin_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    status = models.IntegerField()


class Settings(models.Model):
    path_to_gl_iso = models.CharField(max_length=250, blank=True, null=True)
    path_to_ro_iso = models.CharField(max_length=250, blank=True, null=True)
    stapel = models.TextField(blank=True, null=True)
    repo = models.TextField(blank=True, null=True)


class ActionLog(models.Model):
    user_name = models.CharField(max_length=25, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(null=True)
    message = models.CharField(max_length=250, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    stapel = models.CharField(max_length=25, blank=True, null=True)
    repo = models.CharField(max_length=25, blank=True, null=True)
    tag = models.CharField(max_length=25, blank=True, null=True)
    packages = models.TextField(blank=True, null=True)
    replace = models.BooleanField(default=False)
    entire = models.BooleanField(default=False)
    update = models.BooleanField(default=False)
    sign = models.BooleanField(default=False)

class BuildIsoSettings(models.Model):
    name = models.CharField(max_length=25, blank=True, null=True)
    comment = models.TextField(max_length=250, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    dir = models.CharField(max_length=250, blank=True, null=True)
    label = models.CharField(max_length=25, blank=True, null=True)
    rel_name = models.CharField(max_length=25, blank=True, null=True)
    rel_short_name = models.CharField(max_length=25, blank=True, null=True)
    rel_ver = models.CharField(max_length=25, blank=True, null=True)
    comps_file_path = models.CharField(max_length=250, blank=True, null=True)
    var_file_path = models.CharField(max_length=250, blank=True, null=True)
    pkgset_repos = models.TextField(blank=True, null=True)

class BuildIso_Log(models.Model):
    process_id = models.IntegerField(null=True)
    user_id = models.IntegerField(null=True)
    inform = models.CharField(max_length=250, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    close_at = models.DateTimeField(null=True)
    status = models.IntegerField(null=True)