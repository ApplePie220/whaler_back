from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serialaizer import UserSerializer
import logging


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


@api_view(['POST'])
def createUser(request):
    try:
        user_data = {
            'login': request.data.get('login'),
            'password': request.data.get('password')  # Хешируем пароль
        }
        # file_data = request.data.get('files')

        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            errors = []
            for field, messages in user_serializer.errors.items():
                for message in messages:
                    errors.append(f"{field}: {message}")
                    logging.error(errors)
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class FileViewSet(viewsets.ModelViewSet):
#     queryset = File.objects.all()
#     serializer_class = FileSerializer
