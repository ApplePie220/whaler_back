# accounts/serializers.py

from rest_framework import serializers
from .models import User, File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['files_id', 'file', 'format_file', 'user_id']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'login', 'password']