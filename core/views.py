# core/views.py
from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    """Home page view"""
    return render(request, 'core/home.html')

