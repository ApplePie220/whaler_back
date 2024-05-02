# accounts/serializers.py

from rest_framework import serializers
from .models import User, File


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['login', 'password']


# class FileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = File
#         fields = ['file', 'format_file', 'user_id']
