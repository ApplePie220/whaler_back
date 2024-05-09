from django.shortcuts import render
from rest_framework import generics, permissions
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from .serialaizer import UserSerializer
from .models import User
import logging
import uuid



class UserRegistration(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        session_id = str(uuid.uuid4())
        response.data['session_id'] = session_id
        response.status_code = 201
        return response

class UserLogin(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if email and password:
            user = User.objects.filter(email=email).first()
            if user and check_password(password, user.password):
                return Response({'message': 'Login successful'}, status=200)
        
        return Response({'error': 'Invalid credentials'}, status=400)




# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


# class AuthUser(generics.GenericAPIView):
#     permission_classes = []
#     serializer_class = UserSerializer

#     def post(self, request):
#         try:
#             email = request.GET.get('email')
#             password = request.GET.get('password')
            
#             if email and password:
#                 user = User.objects.filter(email=email).first()
#                 if user and user.check_password(password):
#                     return Response(status=status.HTTP_200_OK)
#                 else:
#                     return Response({"error": "Неверный пароль или пользователь не найден"}, status=status.HTTP_401_UNAUTHORIZED)
#             else:
#                 return Response({"error": "Должны быть заполнены все поля"}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class UserView(generics.CreateAPIView):
#     permission_classes = (permissions.AllowAny,)
#     serializer_class = UserSerializer
    # permission_classes = []

    # def post(self, request):
    #     try:
    #         user_data = {
    #             'email': request.data.get('email'),
    #             'password': request.data.get('password')  # Хешируем пароль
    #         }

    #         user_serializer = UserSerializer(data=user_data)
    #         if user_serializer.is_valid(raise_exception=True):
    #             user = user_serializer.save()
    #             if user:
    #                 session_id = str(uuid.uuid4())

    #                 # Устанавливаем куки в ответе
    #                 response = Response("Пользователь успешно создан", status=status.HTTP_201_CREATED)
    #                 response.set_cookie('sessionId', session_id)
    #                 return response

    #         return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         logging.error(f"An error occurred while creating user: {str(e)}")
    #         return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['POST'])
# def createUser(request):


# class FileViewSet(viewsets.ModelViewSet):
#     queryset = File.objects.all()
#     serializer_class = FileSerializer
