from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from djongo import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=80)
    
    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)


# class File(models.Model):
#     files_id = models.AutoField(primary_key=True)
#     file = models.FileField(upload_to='files/')
#     format_file = models.CharField(max_length=180)
#     user_id = models.ForeignKey(User, on_delete=models.CASCADE)
