from asyncio import exceptions
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
import firebase_admin
from firebase_admin import auth, firestore, exceptions
import requests
from django.conf import settings
from django.core.mail import send_mail


db = firestore.client()

firebase_api_key = 'AIzaSyBrnuE0rPIse9NIoJiV0kw2FMEGDXShjBQ'
url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}'

def homepage_view(request):
    return render(request, 'home/homepage.html')

def dashboard_view(request):
    return render(request, 'home/dashboard.html')

def logout_view(request):
    logout(request)
    return render(request, 'home/login.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Check if the email exists in the pending_users collection
            pending_user_ref = db.collection('pending_users').document(email)
            pending_user = pending_user_ref.get()

            if pending_user.exists and not pending_user.to_dict().get('approved', False):
                # If the email is in pending_users and not approved
                messages.error(request, 'Your account is still pending approval. Please wait for admin approval.')
                return render(request, 'home/login.html', {'email': email})

            # Check if the user exists in Firebase Authentication
            user = auth.get_user_by_email(email)

            # Prepare payload and send request to Firebase REST API for authentication
            payload = {
                'email': email,
                'password': password,
                'returnSecureToken': True
            }
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                # Login successful, redirect to dashboard
                return redirect('dashboard')
            else:
                # If authentication fails, check the error response
                error_message = response.json().get('error', {}).get('message')
                if error_message == 'EMAIL_NOT_FOUND':
                    messages.error(request, 'This email is not registered. Please sign up first.')
                elif error_message == 'INVALID_PASSWORD':
                    messages.error(request, 'Incorrect password. Please try again.')
                else:
                    messages.error(request, 'Invalid login credentials.')

        except firebase_admin.auth.UserNotFoundError:
            # This will be caught if the email is not registered in Firebase Authentication
            messages.error(request, 'This email is not registered. Please sign up first.')
        except exceptions.FirebaseError as e:
            # This will catch any Firebase-related errors
            messages.error(request, f'Firebase error occurred: {str(e)}')

        return render(request, 'home/login.html', {'email': email})
    
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
        # Capture first name, last name, email, and password from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Step 1: Check if the email is already in the Firestore 'pending_users' collection
        pending_user_ref = db.collection('pending_users').document(email).get()
        if pending_user_ref.exists:
            return render(request, 'home/signup.html', {
                'invalid_password_message': 'This email is already pending approval.',
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            })

        # Step 2: Check if the user already exists by email in Firebase Authentication
        try:
            existing_user = auth.get_user_by_email(email)
            # If we reach this point, the email is already registered
            return render(request, 'home/signup.html', {
                'invalid_password_message': 'Email is already registered.',
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            })
        except firebase_admin.auth.UserNotFoundError:
            # If the user does not exist, proceed to the next step
            pass

        # Step 3: Validate the password using the validate_password function
        if not validate_password(password):
            return render(request, 'home/signup.html', {
                'invalid_password_message': 'Password must meet the requirements.',
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            })

        # Step 4: Store user in 'pending_users' collection for admin approval
        try:
            db.collection('pending_users').document(email).set({
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': password,
                'created_at': firestore.SERVER_TIMESTAMP,
                'approved': False,  # Set approved to False initially
                'role':'user'
            })

            messages.success(request, 'Registration successful! Your account is awaiting approval.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error creating user in Firestore: {str(e)}")

    # Render the signup page if the request method is GET
    return render(request, 'home/signup.html')


def admin_dashboard_view(request):
    # Fetch all pending users from Firestore where 'approved' is False
    pending_users_ref = db.collection('pending_users').where('approved', '==', False)
    pending_users = pending_users_ref.stream()

    # Prepare the context with pending users
    users_list = []
    for user in pending_users:
        user_data = user.to_dict()  # Convert Firestore document to dictionary
        users_list.append({
            'email': user_data.get('email', 'N/A'),
            'first_name': user_data.get('first_name', 'N/A'),
            'last_name': user_data.get('last_name', 'N/A'),
            'password': user_data.get('password', 'N/A'),  # Password will be hashed and not displayed
            'doc_id': user.id  # Document ID needed for approving the user
        })

    context = {'pending_users': users_list}

    # Render the admin dashboard template with the context
    return render(request, 'home/admin_dashboard.html', context)


def approve_user_view(request, email):
    # Get the user document from 'pending_users' collection
    pending_user_ref = db.collection('pending_users').where('email', '==', email).stream()
    user_doc = next(pending_user_ref, None)  # Get the first matching document

    if user_doc:
        user_data = user_doc.to_dict()  # Convert Firestore document to dictionary
        user_email = user_data['email']
        user_password = user_data['password']  # The hashed password should be securely handled
        
        try:
            # Create a new user in Firebase Authentication
            auth.create_user(
                email=user_email,
                password=user_password,
                display_name=f"{user_data['first_name']} {user_data['last_name']}"
            )

            user_role = user_data.get('role', 'user')
            
            # Move the user data to the 'users' collection in Firestore
            db.collection('users').document(user_doc.id).set({
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'email': user_data['email'],
                'role': user_role,
                'created_at': firestore.SERVER_TIMESTAMP,
                'approved': True  # Mark the user as approved
            })

            # Delete the user document from 'pending_users' collection
            db.collection('pending_users').document(user_doc.id).delete()

            messages.success(request, f"User {user_email} approved successfully!")

        except Exception as e:
            messages.error(request, f"Error approving user: {str(e)}")

    else:
        messages.error(request, f"User with email {email} not found in pending users.")

    # Redirect back to the admin dashboard
    return redirect('admin_dashboard')
