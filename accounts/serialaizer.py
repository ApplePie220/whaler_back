# accounts/serializers.py

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=40, validators=[UniqueValidator(queryset=User.objects.all())])
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.get('password')
        email = validated_data.get('email')

        # Проверяем, существует ли пользователь с таким логином
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")

        user = User.objects.create(email=email)
        user.set_password(password)
        user.save()
        return user

# class FileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = File
#         fields = ['file', 'format_file', 'user_id']
