from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serialaizer import UserSerializer
from .models import User
import logging
import uuid


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

class UserView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            login = request.GET.get('login')
            password = request.GET.get('password')

            # Проверяем, существует ли пользователь с таким логином
            user = User.objects.filter(login=login).first()

            if user:
                # Проверяем, верен ли введенный пароль
                if user.checkPassword(password):
                    return Response({"message": "Аутентификация успешна"})
                else:
                    return Response({"error": "Неверный пароль"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"error": "Пользователь с таким логином не найден"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            user_data = {
                'login': request.data.get('login'),
                'email': request.data.get('email'),
                'password': request.data.get('password')  # Хешируем пароль
            }

            user_serializer = UserSerializer(data=user_data)
            if user_serializer.is_valid(raise_exception=True):
                user = user_serializer.save()
                if user:
                    session_id = str(uuid.uuid4())

                    # Устанавливаем куки в ответе
                    response = Response("Пользователь успешно создан", status=status.HTTP_201_CREATED)
                    response.set_cookie('sessionId', session_id)
                    return response

            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"An error occurred while creating user: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['POST'])
# def createUser(request):


# class FileViewSet(viewsets.ModelViewSet):
#     queryset = File.objects.all()
#     serializer_class = FileSerializer
