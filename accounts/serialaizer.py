from rest_framework import serializers
from .models import User, File


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['file', 'format_file', 'user_id']