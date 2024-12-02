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
from .views import login_view, homepage_view, delete_upload_view, check_job_status,  signup_view, dashboard_view, logout_view, admin_dashboard_view, upload_view,  password_reset_view, profile_view, change_password, delete_email_view ,search_attributes1,update_account_status,format_time_detected, generate_detection_time_link

urlpatterns = [
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('', homepage_view, name='homepage'),  
    path('logout/', logout_view, name='logout'),
    path('admin_dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('update_account_status/<str:email>/', update_account_status, name='update_account_status'),
    path('password_reset/', password_reset_view, name='password_reset'),
    path('profile/', profile_view, name='profile'),
    path('change_password/', change_password, name='change_password'),
    path('delete_email/', delete_email_view, name='delete_email'),
    path('search_attributes1/', search_attributes1, name='search_attributes1'),
    path('upload/', upload_view, name='upload'),
    path('format_time_detected/', format_time_detected, name='format_time_detected'),
    path('generate_detection_time_link/', generate_detection_time_link, name='generate_detection_time_link'),
    path('delete-upload/', delete_upload_view, name='delete_upload_view'),
    path('check-status/', check_job_status, name='check_job_status'),     
     
]