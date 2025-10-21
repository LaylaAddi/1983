# core/views.py
from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    """Home page view"""
    return render(request, 'core/home.html')

def know_your_rights(request):
    """Home page view"""
    return render(request, 'core/know-your-rights.html')

def uptrend(request):
    """Uptrend page view"""
    return render(request, 'core/uptrend.html')

def downtrend(request):
    """Uptrend page view"""
    return render(request, 'core/downtrend.html')

def albrooks(request):
    return render(request, 'core/albrooks.html')

def setups(request):
    return render(request, 'core/setups.html')

def pwa_demo(request):
    """PWA Demo and Installation Guide"""
    return render(request, 'core/pwa_demo.html')

def install(request):
    """Installation instructions for PWA"""
    return render(request, 'core/install.html')

