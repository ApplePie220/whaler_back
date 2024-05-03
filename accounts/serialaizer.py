# accounts/serializers.py

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User


class UserSerializer(serializers.ModelSerializer):
    login = serializers.CharField(max_length=40, validators=[UniqueValidator(queryset=User.objects.all())])
    class Meta:
        model = User
        fields = ['login','email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        login = validated_data.get('login')
        password = validated_data.get('password')
        email = validated_data.get('email')

        # Проверяем, существует ли пользователь с таким логином
        if User.objects.filter(login=login).exists():
            raise serializers.ValidationError("Пользователь с таким логином уже существует")

        user = User.objects.create(login=login, email=email)
        user.set_password(password)
        user.save()
        return user

# class FileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = File
#         fields = ['file', 'format_file', 'user_id']
