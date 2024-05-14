from django.shortcuts import render
from rest_framework import generics, permissions, status
from django.contrib.auth.hashers import check_password
from django.contrib.sessions.models import Session
from rest_framework.response import Response
from django.http import JsonResponse
from .serialaizer import UserSerializer
from .models import User
from .parser import DockerfileParser, DockercomposeParser, DockerfileToJsonParser, DockercomposeToJsonParser
import json
import yaml
import uuid 
import os



#регистрация пользователя на сайте
class UserRegistration(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        request.session.save()  # Save the session to generate a session ID
        response.set_cookie('sessionid', request.session.session_key)  # Set the session ID in the response headers
        return response

#авторизация пользователя на сайте
class UserLogin(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if email and password:
            user = User.objects.filter(email=email).first()
            if user and check_password(password, user.password):
                user_id = user.id
                request.session['user_id'] = user_id
                return Response({'message': 'Login successful'}, status=200)
        
        return Response({'error': 'Invalid credentials'}, status=400)

# выход пользователя с сайта
class UserLogout(generics.GenericAPIView):
    def post(self, request):
        # Получаем идентификатор сессии из куки
        session_id = request.COOKIES.get('sessionid')

        # Если идентификатор сессии есть, удаляем сессию из базы данных
        if session_id:
            try:
                session = Session.objects.get(session_key=session_id)
                session.delete()
            except Session.DoesNotExist:
                pass

        # Очищаем куки
        response = JsonResponse({"message": "Logged out successfully"})
        response.delete_cookie('sessionid')

        return response

# парсер из dockerfile в json
class DockerfileToJsonView(generics.GenericAPIView):
    def post(self, request):
        try:
            dockerfile_input = """
            FROM ubuntu
            COPY . /app
            ADD . /app/app
            CMD ["python"]
            """
            if dockerfile_input:
                json_data = DockerfileToJsonParser.parse_dockerfile_to_json(dockerfile_input)
                return Response(json_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Dockerfile data not provided'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'error': 'Failed to parse Dockerfile'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# парсер из docker-compose.yml в json
class DockerCompToJsonView(generics.GenericAPIView):
    def post(self, request):
        try:
            dockercompose_input = """
            services:
                postgres:
                    restart: always
                web:
                    build: .
                    image: node
            version: '3'
            """
            if dockercompose_input:
                json_data = DockercomposeToJsonParser.parse_dockercompose_to_json(dockercompose_input)
                return Response(json_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Dockercompose data not provided'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'error': 'Failed to parse Dockercompose'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# парсер и сохранения dockerfile
class DockerfileGeneratorView(generics.GenericAPIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            # parser = DockerfileParser(data)
            dockerfile = DockerfileParser.parse_json_to_dockerfile(data)
            dockerfile_path = os.path.join('dockerfiles', 'Dockerfile')
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile)
            return Response({'message': 'Dockerfile generated successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'error': 'Failed to generate Dockerfile'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# парсер и сохранения docker-compose.yml
class DockerComposeGeneratorView(generics.GenericAPIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            docker_compose = DockercomposeParser.parse_json_to_docker_compose(data)
            docker_compose_path = os.path.join('dockercomposefiles', 'docker-compose.yml')
            with open(docker_compose_path, 'w') as f:
                yaml.dump(docker_compose, f, indent=4)
            return Response({'message': 'docker-compose.yml has been generated and saved successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'error': 'Failed to generate docker-compose.yml'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class DockerfileGeneratorView1(generics.GenericAPIView):
#     def post(self, request):
#         try:
#             data = json.loads(request.body)
#             user_id = request.session.get('user_id')
#             if user_id:
#                 user_folder = os.path.join('dockerfiles', str(user_id))
#                 os.makedirs(user_folder, exist_ok=True)
#                 # Генерируем уникальное имя для Dockerfile с помощью UUID
#                 dockerfile_name = f'Dockerfile_{uuid.uuid4().hex[:8]}'  # Пример: Dockerfile_12345678
#                 dockerfile_path = os.path.join(user_folder, dockerfile_name)
#                 dockerfile = DockerfileParser.parse_json_to_dockerfile(data)
#                 with open(dockerfile_path, 'w') as f:
#                     f.write(dockerfile)
#                 return Response({'message': 'Dockerfile успешно создан и сохранен'}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response({'error': 'Пользователь не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)
#         except Exception as e:
#             print(e)
#             return Response({'error': 'Ошибка при создании Dockerfile'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

