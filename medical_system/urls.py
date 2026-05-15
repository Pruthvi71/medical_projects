"""
URL configuration for medical_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.http import JsonResponse
from django.urls import path, include
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def deploy_status(request):
    return JsonResponse({
        'app': 'VRAJ Care',
        'version': 'password-reset-diagnostic-a09a566',
        'email_backend': settings.EMAIL_BACKEND,
        'email_host': settings.EMAIL_HOST,
        'email_host_user_set': bool(settings.EMAIL_HOST_USER),
        'email_password_set': bool(settings.EMAIL_HOST_PASSWORD),
        'default_from_email': settings.DEFAULT_FROM_EMAIL,
        'public_site_url': settings.PUBLIC_SITE_URL,
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__deploy_status__/', deploy_status, name='deploy_status'),
    path('', home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('appointments/', include('appointments.urls')),
    path('doctor/', include('doctors.urls')),


]

#test
