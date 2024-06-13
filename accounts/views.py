from rest_framework import generics, permissions, status
from django.contrib.auth.hashers import check_password
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate, logout, login
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from django.http import JsonResponse
from .serialaizer import UserSerializer, FileSerializer
from .models import User, File
from .parser import DockerfileParser, DockercomposeParser, DockerfileToJsonParser, DockercomposeToJsonParser
import json
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
            user = authenticate(request, email=email)
            if user is not None and check_password(password, user.password):
                login(request, user)
                request.session['user_id'] = user.id
                if request.user.is_authenticated:
                    return Response({'message': 'Успешная авторизация'}, status=200)
                else:
                    return Response({'error': 'Ошибка аутентификации'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({'error': 'Неверные данные или ошибка аутентификации'}, status=400)

# выход пользователя с сайта
class UserLogout(generics.GenericAPIView):
    def get(self, request):
        # Получаем идентификатор сессии из куки
        logout(request)
        # Очищаем куки
        response = JsonResponse({"message": "Успешный выход"})
        response.delete_cookie('sessionid')

        return response

# считывание файла dockerfile и превращение его в json
class DockerfileToJsonView(generics.GenericAPIView):
    def post(self, request):
        try:
            # Получение текущего авторизованного пользователя
            user = request.user
            if not user.is_authenticated:
                return Response({'error': 'Пользователь не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

            # Получение названия Dockerfile из запроса
            request_data = request.data
            dockerfile_name = request_data.get('dockerfile_name', None)

            if not dockerfile_name:
                return Response({'error': 'Название Dockerfile не предоставлено'}, status=status.HTTP_400_BAD_REQUEST)

            # Поиск файла в базе данных
            try:
                file_record = File.objects.get(user_id=user, file__icontains=dockerfile_name)
            except ObjectDoesNotExist:
                return Response({'error': 'Файл Dockerfile не найден'}, status=status.HTTP_404_NOT_FOUND)

            # Проверка наличия файла на сервере
            dockerfile_path = file_record.file.path
            if not os.path.exists(dockerfile_path):
                return Response({'error': 'Файл Dockerfile отсутствует на сервере'}, status=status.HTTP_404_NOT_FOUND)

            # Считывание содержимого файла
            with open(dockerfile_path, 'r') as file:
                dockerfile_content = file.read()

            json_data = dockerfile_content
            return Response(json_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': 'Ошибка парсинга Dockerfile'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# считывание файла Докер компоуза и превращение его в json
class DockerCompToJsonView(generics.GenericAPIView):
    def post(self, request):
        try:
            # Получение текущего авторизованного пользователя
            user = request.user
            if not user.is_authenticated:
                return Response({'error': 'Пользователь не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

            # Получение названия docker-compose файла из запроса
            request_data = request.data
            dockercompose_name = request_data.get('dockercompose_name', None)

            if not dockercompose_name:
                return Response({'error': 'Название docker-compose файла не предоставлено'}, status=status.HTTP_400_BAD_REQUEST)

            # Поиск файла в базе данных
            try:
                file_record = File.objects.get(user_id=user, file__icontains=dockercompose_name)
            except ObjectDoesNotExist:
                return Response({'error': 'Файл docker-compose не найден'}, status=status.HTTP_404_NOT_FOUND)

            # Проверка наличия файла на сервере
            dockercompose_path = file_record.file.path
            if not os.path.exists(dockercompose_path):
                return Response({'error': 'Файл docker-compose отсутствует на сервере'}, status=status.HTTP_404_NOT_FOUND)

            # Считывание содержимого файла
            with open(dockercompose_path, 'r') as file:
                dockercompose_content = file.read()

            json_data = dockercompose_content
            return Response(json_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': 'Ошибка парсинга docker-compose'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# сохранение джсон в docker-compose файлик
class DockerComposeGeneratorView(generics.GenericAPIView):
    def post(self, request):
        try:
            user = request.user
            if not user.is_authenticated:
                return Response({'error': 'Пользователь не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

            data = json.loads(request.body)

            user_id = request.session.get('user_id')
            user_data = User.objects.get(id=user_id)
            user_folder = os.path.join('dockercomposefiles', str(user_id))

            docker_compose_name = f'docker-compose_{uuid.uuid4().hex[:8]}.json'
            docker_compose_path = os.path.join(user_folder, docker_compose_name)

            os.makedirs(os.path.dirname(docker_compose_path), exist_ok=True)

            with open(docker_compose_path, 'w') as f:
                json.dump(data, f, indent=4)

            file_instance = File(file=docker_compose_path, format_file='json', user_id=user_data)
            file_instance.save()

            return Response({'message': 'docker-compose.json был успешно создан', 'file_name': docker_compose_name},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'error': 'Ошибка при создании docker-compose.json'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#сохранение джсон в dockerfile файлик
class DockerfileGeneratorView(generics.GenericAPIView):
    def post(self, request):
        try:
            user = request.user
            if not user.is_authenticated:
                return Response({'error': 'Пользователь не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

            data = json.loads(request.body)

            user_id = request.session.get('user_id')
            user_data = User.objects.get(id=user_id)
            user_folder = os.path.join('dockerfiles', str(user_id))
            os.makedirs(user_folder, exist_ok=True)

            dockerfile_name = f'Dockerfile_{uuid.uuid4().hex[:8]}.json'
            dockerfile_path = os.path.join(user_folder, dockerfile_name)

            with open(dockerfile_path, 'w') as f:
                json.dump(data, f, indent=4)

            file_instance = File(file=dockerfile_path, format_file='json', user_id=user_data)
            file_instance.save()

            return Response({'message': 'Dockerfile.json успешно создан и сохранен'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'error': 'Ошибка при создании docker-compose.json'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# удаление файла
class FileDeleteView(generics.GenericAPIView):
    def delete(self, request):
        try:
            # Получение текущего авторизованного пользователя
            user = request.user
            if not user.is_authenticated:
                return Response({'error': 'Пользователь не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

            # Получение названия файла из запроса
            request_data = request.data
            file_name = request_data.get('file_name', None)

            if not file_name:
                return Response({'error': 'Название файла не предоставлено'}, status=status.HTTP_400_BAD_REQUEST)

            # Поиск файла в базе данных
            try:
                file_record = File.objects.get(user_id=user, file__icontains=file_name)
            except ObjectDoesNotExist:
                return Response({'error': 'Файл не найден'}, status=status.HTTP_404_NOT_FOUND)

            # Проверка наличия файла на сервере и его удаление
            file_path = file_record.file.path
            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                return Response({'error': 'Файл отсутствует на сервере'}, status=status.HTTP_404_NOT_FOUND)

            # Удаление записи о файле из базы данных
            file_record.delete()

            return Response({'message': 'Файл успешно удален'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': 'Ошибка при удалении файла'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# парсинг докерфайла в Json для всех, даже для неавторизованных
class DockerfileParseAllView(generics.GenericAPIView):
    authentication_classes = []  # Отключаем аутентификацию
    permission_classes = []  # Отключаем проверки разрешений

    def post(self, request):
        try:
            # Получение содержимого Dockerfile из запроса
            dockerfile_content = request.data.get('dockerfile_content', None)

            if not dockerfile_content:
                return Response({'error': 'Данные Dockerfile не предоставлены'}, status=status.HTTP_400_BAD_REQUEST)

            # Парсинг содержимого Dockerfile в JSON
            json_data = DockerfileToJsonParser.parse_dockerfile_to_json(dockerfile_content)
            return Response(json_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': 'Ошибка парсинга Dockerfile'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# парсинг докер компоуза в Json для всех, даже для неавторизованных
class DockerComposeParseAllView(generics.GenericAPIView):
    authentication_classes = []  # Отключаем аутентификацию
    permission_classes = []  # Отключаем проверки разрешений

    def post(self, request):
        try:
            # Получение содержимого docker-compose.yml из запроса
            dockercompose_content = request.data.get('dockercompose_content', None)

            if not dockercompose_content:
                return Response({'error': 'Данные docker-compose не предоставлены'}, status=status.HTTP_400_BAD_REQUEST)

            # Парсинг содержимого docker-compose.yml в JSON
            json_data = DockercomposeToJsonParser.parse_dockercompose_to_json(dockercompose_content)
            return Response(json_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': 'Ошибка парсинга docker-compose'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#json в docker-compose Для неавторизованных
class DockerComposeGeneratorAllView(generics.GenericAPIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            docker_compose = DockercomposeParser.parse_json_to_docker_compose(data)
            return Response({'message': 'docker-compose.yml был успешно создан', 'docker_compose': docker_compose},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'error': 'Ошибка при создании docker-compose.yml'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#json в dockerfile Для неавторизованных
class DockerfileGeneratorAllView(generics.GenericAPIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            dockerfile = DockerfileParser.parse_json_to_dockerfile(data)
            return Response({'message': 'Dockerfile успешно создан', 'dockerfile': dockerfile},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'error': 'Ошибка при создании Dockerfile'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# отображение списка файлов для пользователя
class FileListView(generics.GenericAPIView):
    serializer_class = FileSerializer

    def get(self, request):
        try:
            # Получение текущего авторизованного пользователя
            user = request.user
            if not user.is_authenticated:
                return Response({'error': 'Пользователь не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

            # Получение всех файлов пользователя
            files = File.objects.filter(user_id=user)

            # Сериализация данных о файлах
            serializer = self.serializer_class(files, many=True)

            return Response({'files': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': 'Ошибка при получении списка файлов'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)