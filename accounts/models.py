from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from djongo import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    login = models.CharField(max_length=40, unique=True)
    email = models.EmailField(max_length=80)
    password = models.CharField(max_length=80)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def checkPassword(self, raw_password):
        return check_password(raw_password, self.password)


class File(models.Model):
    files_id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='files/')
    format_file = models.CharField(max_length=180)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
