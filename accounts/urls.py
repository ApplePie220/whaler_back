from django.urls import path
from .views import UserRegistration, UserLogin

urlpatterns = [
        path('createuser/', UserRegistration.as_view(), name='user-registration'),
        path('authuser/', UserLogin.as_view(), name='user-auth'),
]