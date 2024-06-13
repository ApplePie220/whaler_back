from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from djongo import models
from django_test_serv.settings import MAX_USER_FILE


class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=80)

    
    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)


class File(models.Model):
    file = models.FileField(upload_to='files/')
    format_file = models.CharField(max_length=180)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    files = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f'{self.file.name} ({self.format_file})'

    def save(self, *args, **kwargs):
        if self.user_id.files.count() >= MAX_USER_FILE:
            raise ValidationError('User cannot have more than 30 files.')
        super(File, self).save(*args, **kwargs)
