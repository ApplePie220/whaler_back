from django.db import models
from djongo import models as djongo_models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    login = models.CharField(max_length=40)
    password = models.CharField(max_length=80)


class File(models.Model):
    files_id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='files/')
    format_file = models.CharField(max_length=255)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
