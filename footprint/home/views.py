from django.shortcuts import render, redirect
from django.contrib import messages
import firebase_admin
from firebase_admin import auth
import requests

def homepage_view(request):
    return render(request, 'home/homepage.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = auth.get_user_by_email(email)
            firebase_api_key = 'AIzaSyBrnuE0rPIse9NIoJiV0kw2FMEGDXShjBQ'
            url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}'
            payload = {
                'email': email,
                'password': password,
                'returnSecureToken': True
            }
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                # Login successful, redirect to homepage
                return redirect('homepage')
            else:
                # If authentication fails
                messages.error(request, 'Invalid login credentials.')

        except exceptions.FirebaseError as e:
            messages.error(request, 'Firebase error occurred: {}'.format(str(e)))

    return render(request, 'home/login.html')

# validating passwords
def validate_password(password):
     # Password must be at least 8 characters, with one lowercase and one uppercase letter
    if len(password) < 8 or not any(c.islower() for c in password) or not any(c.isupper() for c in password):
        return False
    return True


#new fucntion needed for registering

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Validate password using the validate_password function
        if not validate_password(password):
            return render(request, 'home/signup.html', {
                'invalid_password_message': 'Password must meet the requirements.',
            })

        try:
            # Check if the user already exists by email
            existing_user = auth.get_user_by_email(email)
            return render(request, 'home/signup.html', {
                'invalid_password_message': 'Email is already registered.',
            })
        except auth.UserNotFoundError:
            # If user does not exist, create a new user
            try:
                user = auth.create_user(email=email, password=password)
                messages.success(request, 'User created successfully!')
                return redirect('login')  # Redirect to the login page after successful sign-up
            except Exception as e:
                messages.error(request, f"Error creating user: {str(e)}")

    # Render the signup page if the request method is GET
    return render(request, 'home/signup.html')