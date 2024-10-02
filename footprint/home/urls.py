"""
URL configuration for footprint project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from .views import login_view, homepage_view, signup_view, dashboard_view, logout_view, admin_dashboard_view,approve_user_view, example_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('', homepage_view, name='homepage'),  
    path('logout/', logout_view, name='logout'),
    path('admin_dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('approve_user/<str:email>/', approve_user_view, name='approve_user'),
    path('example/', example_view, name='example'),
    
    
]