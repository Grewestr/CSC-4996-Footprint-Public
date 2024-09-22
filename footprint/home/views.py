from asyncio import exceptions
from django.shortcuts import render, redirect
from django.contrib import messages
import firebase_admin
from firebase_admin import auth
import requests
from django.conf import settings

firebase_api_key = 'AIzaSyBrnuE0rPIse9NIoJiV0kw2FMEGDXShjBQ'
url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}'

def homepage_view(request):
    return render(request, 'home/homepage.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Check if the user exists in Firebase
            user = auth.get_user_by_email(email)

            # Prepare payload and send request to Firebase REST API
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
                # If authentication fails, check the error response
                error_message = response.json().get('error', {}).get('message')
                if error_message == 'EMAIL_NOT_FOUND':
                    messages.error(request, 'This email is not registered. Please sign up first.')
                elif error_message == 'INVALID_LOGIN_CREDENTIALS':
                    messages.error(request, 'Incorrect password. Please try again.')
                else:
                    messages.error(request, 'Invalid login credentials.')

        except firebase_admin.auth.UserNotFoundError:
            # This will be caught if the email is not registered in Firebase
            messages.error(request, 'This email is not registered. Please sign up first.')
        except exceptions.FirebaseError as e:
            messages.error(request, f'Firebase error occurred: {str(e)}')

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

        # Step 1: Check if the user already exists by email
        try:
            existing_user = auth.get_user_by_email(email)
            # If we reach this point, the email is already registered
            return render(request, 'home/signup.html', {
                'invalid_password_message': 'Email is already registered.',
            })
        except firebase_admin.auth.UserNotFoundError:
            # If the user does not exist, we move on to password validation
            pass  # Continue to the next step if the user is not found

        # Step 2: Validate password using the validate_password function
        if not validate_password(password):
            return render(request, 'home/signup.html', {
                'invalid_password_message': 'Password must meet the requirements.',
                'email': email
            })

        # Step 3: Create a new user
        try:
            user = auth.create_user(email=email, password=password)
            messages.success(request, 'User created successfully! Please log in.')
            return redirect('login')  # Redirect to the login page after successful sign-up
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")

    # Render the signup page if the request method is GET
    return render(request, 'home/signup.html')
