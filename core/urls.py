# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('know-your-rights/', views.know_your_rights, name='know_your_rights'),
]