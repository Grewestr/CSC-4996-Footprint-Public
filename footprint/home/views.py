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
            
            #Akram here is wehre we need to integrrate the email and passwords into the database
            return redirect('homepage')  
        except firebase_admin.auth.AuthError:
            messages.error(request, 'Invalid login credentials.')
    
    return render(request, 'home/login.html')

# validating passwords
def validate_password(password):
    if len(password) < 8 or not any(c.islower() for c in password) or not any(c.isupper() for c in password):
        return False
    return True


#new fucntion needed for registering

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Validate password
        if not validate_password(password):
            return render(request, 'home/signup.html', {
                'invalid_password_message': 'Password does not meet the requirements.',
            })

        try:
            # Firebase Admin SDK: create user
            user = auth.create_user(email=email, password=password)
            messages.success(request, 'User created successfully!')
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
    return render(request, 'home/signup.html')