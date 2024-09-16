from django.shortcuts import render, redirect
from django.contrib import messages
import firebase_admin
from firebase_admin import auth

def homepage_view(request):
    return render(request, 'home/homepage.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            # Firebase Admin SDK: authenticate the user
            user = auth.get_user_by_email(email)
            
            # Perform password validation with Firebase Authentication API
            # Redirect to the homepage after successful login
            return redirect('homepage')  # Replace with the name of your homepage view
        except firebase_admin.auth.AuthError:
            messages.error(request, 'Invalid login credentials.')
    
    return render(request, 'home/login.html')

