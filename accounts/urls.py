from django.urls import path
from .views import UserRegistration, UserLogin, DockerfileGeneratorView, UserLogout, DockerComposeGeneratorView, DockerfileToJsonView, DockerCompToJsonView

urlpatterns = [
        path('createuser/', UserRegistration.as_view(), name='user-registration'),
        path('authuser/', UserLogin.as_view(), name='user-auth'),
        path('dockerfileparse/', DockerfileGeneratorView.as_view(), name='dock-parse'),
        path('dockercompparse/', DockerComposeGeneratorView.as_view(), name='dock-comp-parse'),
        path('logout/', UserLogout.as_view(), name='user-logout'),
        path('dockerfile-to-json/', DockerfileToJsonView.as_view(), name='dockfile-tojson'),
        path('dockercompose-to-json/', DockerCompToJsonView.as_view(), name='dockcompose-tojson'),
]

