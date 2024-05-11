from django.urls import path
from .views import UserRegistration, UserLogin, DockerfileGeneratorView, UserLogout, DockerComposeGeneratorView

urlpatterns = [
        path('createuser/', UserRegistration.as_view(), name='user-registration'),
        path('authuser/', UserLogin.as_view(), name='user-auth'),
        path('dockerfileparse/', DockerfileGeneratorView.as_view(), name='dock-parse'),
        path('dockercompparse/', DockerComposeGeneratorView.as_view(), name='dock-comp-parse'),
        path('logout/', UserLogout.as_view(), name='user-logout')
]