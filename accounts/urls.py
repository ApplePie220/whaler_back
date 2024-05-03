from django.urls import path
from . import views

urlpatterns = [
        path('createuser/', views.UserView.as_view()),
]