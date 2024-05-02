from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, File
from .serialaizer import UserSerializer, FileSerializer


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


@api_view(['POST'])
def createUser(request):
    user_data = request.data.get('user')
    # file_data = request.data.get('files')

    user_serializer = UserSerializer(data=user_data)
    if user_serializer.is_valid():
        user_serializer.save()
        # user = user_serializer.instance

        # file_serializers = [FileSerializer(data=file) for file in file_data]
        # for file_serializer in file_serializers:
        #     if file_serializer.is_valid():
        #         file_serializer.save(user=user)

        return Response(status=status.HTTP_201_CREATED)

    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class FileViewSet(viewsets.ModelViewSet):
#     queryset = File.objects.all()
#     serializer_class = FileSerializer
