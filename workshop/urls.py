"""
URL configuration for workshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from apps.QA.views import ChatView, get_ai_response
from apps.users.views import user_login, user_logout
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',user_login,name='login'),
    path('logout/',user_logout,name='dashboard'),
    path('',ChatView.as_view(),name='chat'),
    path('api/get-ai-response/',get_ai_response,name='get_ai_response'),
]
