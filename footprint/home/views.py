import re
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
import firebase_admin
from firebase_admin import auth, firestore, exceptions, storage
import requests
import pytz
import random
from django.http import JsonResponse
import os
from google.cloud import firestore
from google.oauth2 import service_account
from google.cloud.firestore_v1 import FieldFilter
from collections import defaultdict
from django.urls import reverse
from datetime import timedelta, datetime
import csv
from django.core.paginator import Paginator
from urllib.parse import urlencode
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from urllib.parse import urlencode

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
key_path = os.path.join(BASE_DIR, 'footprint', 'Firebase', 'serviceAccountKey.json')
credentials = service_account.Credentials.from_service_account_file(key_path)
db = firestore.Client(credentials=credentials)


firebase_api_key = 'AIzaSyBrnuE0rPIse9NIoJiV0kw2FMEGDXShjBQ'
url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}'

# Define the desired time zone (UTC-4)
desired_timezone = pytz.timezone("America/New_York")  # This is UTC-4 when in daylight saving time

def homepage_view(request):
    return render(request, 'home/homepage.html')




def dashboard_view(request):
    # Get the user's email from the session
    user_email = request.session.get('email')
    live_feed_names = []

    # Retrieve the live feeds if the email is available
    if user_email:
        try:
            # Query the live_feeds collection for documents with matching user_email and finished feed status
            feeds_query = db.collection('live_feeds').where('user_email', '==', user_email).where('feed_status', '==', 'finished').stream()

            # Extract only the feed name for each matching document
            live_feed_names = [feed.to_dict().get('feed_name') for feed in feeds_query if 'feed_name' in feed.to_dict()]

        except Exception as e:
            messages.error(request, f"Error retrieving user feed names: {str(e)}")

    # Pass live feed names to the template for the dropdown
    return render(request, 'home/dashboard.html', {'feeds': live_feed_names})



def profile_view(request):
    # Retrieve user information from the session
    full_name = request.session.get('full_name', 'Not available')
    email = request.session.get('email', 'Not available')
    department_name = request.session.get('department_name', 'Not available')

    # Render the profile template with the user's info
    return render(request, 'home/profile.html', {
        'full_name': full_name,
        'email': email,
        'department_name': department_name,
    })


def logout_view(request):
    logout(request) 
    return redirect('login')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
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
                # Retrieve the user info from Firestore 'accounts' collection
                user_ref = db.collection('accounts').document(email)
                user_data = user_ref.get()

                if user_data.exists:
                    user_info = user_data.to_dict()
                    account_status = user_info.get('account_status', 'pending')  # Default to 'pending' if not found
                    department_name = user_info.get('department_name', 'N/A')  # Store department_name

                    # Check account status and handle accordingly
                    if account_status == 'denied':
                        messages.error(request, 'Your registration was denied. Please contact support.')
                        return render(request, 'home/login.html', {'email': email})
                    elif account_status == 'pending':
                        messages.error(request, 'Your account is pending approval.')
                        return render(request, 'home/login.html', {'email': email})
                    elif account_status == 'approved':
                        # Store user info in session
                        role = user_info.get('role', 'user')  # Default to 'user' if no role found
                        full_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}"

                        request.session['uid'] = user.uid  # Firebase UID
                        request.session['role'] = role  # User role
                        request.session['full_name'] = full_name  # Full name
                        request.session['email'] = email  # User email
                        request.session['department_name'] = department_name  # Store department name

                        # Redirect based on user role
                        if role == 'admin':
                            return redirect('homepage')
                        else:
                            return redirect('homepage')

            else:
                # If authentication fails, check the error response
                error_message = response.json().get('error', {}).get('message')
                if error_message == 'EMAIL_NOT_FOUND':
                    messages.error(request, 'This email is not registered. Please sign up first.')
                elif error_message == 'INVALID_PASSWORD':
                    messages.error(request, 'Incorrect password. Please try again.')
                else:
                    messages.error(request, 'Incorrect password. Please try again.')

        except firebase_admin.auth.UserNotFoundError:
            # This will be caught if the email is not registered in Firebase Authentication
            messages.error(request, 'This email is not registered. Please sign up first.')
        except exceptions.FirebaseError as e:
            # This will catch any Firebase-related errors
            messages.error(request, f'Firebase error occurred: {str(e)}')

        return render(request, 'home/login.html', {'email': email})

    return render(request, 'home/login.html')


def validate_password(password):
     # Password must be at least 8 characters, with one lowercase and one uppercase letter
    if len(password) < 8 or not any(c.islower() for c in password) or not any(c.isupper() for c in password):
        return False
    return True


def signup_view(request):
    if request.method == 'POST':
        # Capture first name, last name, email, and password from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        department_name = request.POST.get('department_name')

         # Step 1: Check if the email is already in the Firestore 'accounts' collection
        account_ref = db.collection('accounts').document(email).get()
        if account_ref.exists:
            account_data = account_ref.to_dict()
            account_status = account_data.get('account_status')

            # Check the account status and show the appropriate message
            if account_status == 'approved':
                return render(request, 'home/signup.html', {
                    'invalid_password_message': 'This account is already registered and approved.',
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'department_name': department_name
                })
            elif account_status == 'pending':
                return render(request, 'home/signup.html', {
                    'invalid_password_message': 'Your account is pending approval. Please wait for admin approval.',
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'department_name': department_name
                })
            elif account_status == 'denied':
                return render(request, 'home/signup.html', {
                    'invalid_password_message': 'Your registration was denied. Please contact support.',
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'department_name': department_name
                })

        # Step 2: Check if the user already exists by email in Firebase Authentication
        try:
            existing_user = auth.get_user_by_email(email)
            # If we reach this point, the email is already registered
            return render(request, 'home/signup.html', {
                'invalid_password_message': 'Email is already registered.',
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'department_name': department_name
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
                'last_name': last_name,
                'department_name': department_name
            })

        # Step 4: Store user in 'accounts' collection for admin approval
        try:

            # Create the user in Firebase Authentication
            user = auth.create_user(
                email=email,
                password=password,
                display_name=f"{first_name} {last_name}"
            )

            # Store user data in Firestore accounts collection (without password)
            db.collection('accounts').document(email).set({
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'created_at': firestore.SERVER_TIMESTAMP,
                'account_status': 'pending',  # Default to pending
                'role': 'user',  # Default role is user
                'department_name': department_name
            })

            messages.success(request, 'Registration successful! Your account is awaiting approval.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f"Error creating user in Firestore: {str(e)}")

    # Render the signup page if the request method is GET
    return render(request, 'home/signup.html')

def admin_dashboard_view(request):
    # Get filtering parameters from the GET request
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '').strip().lower()
    department_filter = request.GET.get('department', '')
    date_sort = request.GET.get('date_sort', 'newest')  # Default to 'newest'
    page_number = int(request.GET.get('page', 1))
    items_per_page = 10  # users shown per page

    # Fetch all unique departments from the 'accounts' collection
    department_names = set()
    users_ref = db.collection('accounts').where('role', '==', 'user')  # Only get 'user' roles
    for doc in users_ref.stream():
        user_data = doc.to_dict()
        department_name = user_data.get('department_name')
        if department_name:
            department_names.add(department_name)  # Add department to the set

    # Convert the set to a sorted list
    department_names = sorted(department_names)

    # Apply account status filter if needed
    if status_filter != 'all':
        users_ref = users_ref.where('account_status', '==', status_filter)

    # Stream the users with the applied filters
    users = users_ref.stream()
    
    # Prepare filtered list
    users_list = []
    for user in users:
        user_data = user.to_dict()
        created_at = user_data.get("created_at")

        # Adjust the timezone if needed
        if created_at:
            created_at = created_at - timedelta(hours=5)

        # Filter by department if specified
        if department_filter == '' or user_data.get('department_name') == department_filter:
            # Apply search filter on first name, last name, or email
            if (
                search_query == '' or 
                search_query in user_data.get('first_name', '').lower() or 
                search_query in user_data.get('last_name', '').lower() or 
                search_query in user_data.get('email', '').lower()
            ):
                users_list.append({
                    'email': user_data.get('email', 'N/A'),
                    'first_name': user_data.get('first_name', 'N/A'),
                    'last_name': user_data.get('last_name', 'N/A'),
                    'department_name': user_data.get('department_name', 'N/A'),
                    'account_status': user_data.get('account_status', 'N/A'),
                    'account_created': created_at,
                    'doc_id': user.id
                })

    # Sort users by account creation date based on the date_sort filter
    if date_sort == 'newest':
        users_list.sort(key=lambda x: x['account_created'], reverse=True)
    else:  # Sort by oldest
        users_list.sort(key=lambda x: x['account_created'])

    # Paginate the users list
    paginator = Paginator(users_list, items_per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'users_list': page_obj.object_list,
        'total_count': paginator.count,
        'status_filter': status_filter,
        'search_query': search_query,
        'department_filter': department_filter,
        'department_names': department_names,
        'date_sort': date_sort,  
        'page_number': page_number,
        'num_pages': paginator.num_pages,  
    }
    return render(request, 'home/admin_dashboard.html', context)

def update_account_status(request, email):
    new_status = request.POST.get('new_status')  # Get the status from the form

    # Get the current filters and page from POST
    status_filter = request.POST.get('status', 'all')
    department_filter = request.POST.get('department', '')
    search_query = request.POST.get('search', '')
    page = request.POST.get('page', '1')  

    try:
        # Reference to the user's document in Firestore
        user_ref = db.collection('accounts').document(email)

        # Update the account status to the new status (approved, pending, or denied)
        user_ref.update({'account_status': new_status})

        # Display a success message with a custom tag
        messages.success(request, f'Account status for {email} updated to {new_status}.', extra_tags='status_update')
        
    except Exception as e:
        # If there was an error, display an error message with a custom tag
        messages.error(request, f'Error updating account status: {str(e)}', extra_tags='status_update')
       

    url = f"{reverse('admin_dashboard')}?page={page}&status={status_filter}&department={department_filter}&search={search_query}"
    return redirect(url)

def password_reset_view(request):

    # The URL for sending the password reset request to Firebase API
    reset_password_url = f'https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={firebase_api_key}'

    if request.method == 'POST':
        # Retrieve the email address from the submitted form
        email = request.POST.get('email')

        # Step 1: Check if the email exists in Firebase Authentication
        try:
            # Try to retrieve the user from Firebase Authentication
            firebase_user = auth.get_user_by_email(email)
        except firebase_admin.auth.UserNotFoundError:
            # If the email is not found in Firebase Authentication, show a message
            messages.error(request, 'Email not found. Please register first.')
            return render(request, 'home/password_reset.html', {'email': email})

        # Step 2: Check the account status in Firestore
        account_ref = db.collection('accounts').document(email).get()
        if account_ref.exists:
            account_data = account_ref.to_dict()
            account_status = account_data.get('account_status', 'pending')  # Default to 'pending' if not found

            # Check the account status and show the appropriate message
            if account_status == 'denied':
                messages.error(request, 'Your registration was denied. Please contact support.')
                return render(request, 'home/password_reset.html', {'email': email})
            elif account_status == 'pending':
                messages.error(request, 'Your account is pending approval. Please wait for admin approval.')
                return render(request, 'home/password_reset.html', {'email': email})
            elif account_status == 'approved':
                # If account is approved, proceed with sending the password reset email

                # Prepare the payload that will be sent to Firebase for the password reset request
                payload = {
                    'requestType': 'PASSWORD_RESET',  # Specify the type of request as a password reset
                    'email': email  # Include the user's email address in the payload
                }

                # Send the password reset request to Firebase API
                response = requests.post(reset_password_url, json=payload)

                # Check if the request was successful (HTTP status 200)
                if response.status_code == 200:
                    # If successful, show a success message to the user
                    messages.success(request, 'A password reset email has been sent to your email address.')
                    # Redirect the user back to the login page
                    return redirect('login')
                else:
                    # If there was an error, extract the error message from Firebase's response
                    error_message = response.json().get('error', {}).get('message', 'Error sending reset email')
                    # Display the error message to the user
                    messages.error(request, f'Error: {error_message}')

        else:
            # If the email is not found in Firestore, display an error message
            messages.error(request, 'Email not found in our system. Please make sure you entered the correct email address.')

    # If the request method is not POST, render the password reset form
    return render(request, 'home/password_reset.html')


def delete_email_view(request):
    # Handle requests to delete a user's email account.
    if request.method == 'POST':  # Check if the request is a POST request
        session_email = request.session.get('email')  # Retrieve the logged-in user's email from the session
        current_password = request.POST.get('current_password')  # Get the current password from the POST data

        # Check if the password is missing in the request
        if not current_password:
            messages.error(request, "Password missing.", extra_tags='delete_email')  # Display an error message
            # Redirect back to the profile page with an error
            return redirect('/profile/?modal=open&error=email_or_password_missing')

        try:
            # Prepare the payload for authentication
            payload = {
                'email': session_email,  # User's email from session
                'password': current_password,  # Password provided by the user
                'returnSecureToken': True  # Firebase flag for secure token handling
            }
            # Send a POST request to authenticate the user's credentials
            response = requests.post(url, json=payload)

            if response.status_code == 200:  # Authentication was successful
                user = auth.get_user_by_email(session_email)  # Retrieve the Firebase user object
                auth.delete_user(user.uid)  # Delete the user's Firebase account
                db.collection('accounts').document(session_email).delete()  # Remove user data from Firestore

               # Query and delete documents from the live_feeds collection where user_email matches session_email and feed_status is "finished"
                live_feeds_query = db.collection('live_feeds')\
                                      .where('user_email', '==', session_email)\
                                      .where('feed_status', '==', 'finished')\
                                      .stream()

                for doc in live_feeds_query:
                    db.collection('live_feeds').document(doc.id).delete()  # Delete each matching document

                # Query and delete "pending" live feeds
                pending_feeds_query = db.collection('live_feeds')\
                                        .where('user_email', '==', session_email)\
                                        .where('feed_status', '==', 'pending')\
                                        .stream()

                for doc in pending_feeds_query:
                    db.collection('live_feeds').document(doc.id).delete()


                # Query and delete documents from the IdentifiedPersons collection where user_email matches session_email
                identified_persons_query = db.collection('IdentifiedPersons')\
                                              .where('user_email', '==', session_email)\
                                              .stream()

                for doc in identified_persons_query:
                    db.collection('IdentifiedPersons').document(doc.id).delete()  # Delete each matching document

         
                messages.success(request, "Your account has been successfully deleted.", extra_tags='delete_email')
                return logout_view(request)  # Log out the user after deletion
            else:
                # Authentication failed due to incorrect password
                messages.error(request, "Incorrect password", extra_tags='delete_email')
                # Redirect back to the profile page with an error
                return redirect('/profile/?modal=open&error=password_or_email_incorrect')

        except firebase_admin.auth.UserNotFoundError:  # Handle cases where the user does not exist
            messages.error(request, "User not found.", extra_tags='delete_email')  # Display an error message
            return redirect('/profile/?modal=open&error=user_not_found')  # Redirect back to the profile page

        except Exception as e:  # Catch any other unexpected errors
            messages.error(request, f"Error deleting account: {str(e)}", extra_tags='delete_email')
            return redirect('/profile/?modal=open&error=general_error')  # Redirect with a general error

    # Redirect to the profile page if the request is not a POST
    return redirect('/profile/')



def change_password(request):
    # Handle requests to change a user's password.
    if request.method == 'POST':  # Check if the request is a POST request
        # Retrieve form data from the POST request
        current_password = request.POST.get('current_password')  # Current password entered by the user
        new_password = request.POST.get('new_password')  # New password entered by the user
        retype_password = request.POST.get('retype_password')  # Retyped new password for confirmation

        # Gather user information from the session for rendering back to the profile page
        user_info = {
            'full_name': request.session.get('full_name', 'Not available'),
            'email': request.session.get('email', 'Not available'),
            'department_name': request.session.get('department_name', 'Not available'),
            'keep_modal_open': True  # Flag to keep the modal open in the frontend
        }

        # Check if the new password and retyped password match
        if new_password != retype_password:
            messages.error(request, 'New password and retyped password do not match.', extra_tags='change_password_match_error')
            return render(request, 'home/profile.html', user_info)  # Return to profile page with an error

        # Validate the new password format (at least 8 characters, one lowercase, one uppercase)
        if not re.search(r'^(?=.*[a-z])(?=.*[A-Z]).{8,}$', new_password):
            messages.error(request, 'Password must be at least 8 characters with one lowercase and one uppercase letter.', extra_tags='change_password_format_error')
            return render(request, 'home/profile.html', user_info)  # Return to profile page with an error

        try:
            # Retrieve the user's email from the session
            user_email = user_info['email']

            # Prepare the payload to authenticate the current password
            payload = {
                'email': user_email,  # User's email
                'password': current_password,  # Current password for validation
                'returnSecureToken': True  # Firebase flag for secure token handling
            }
            # Send a POST request to authenticate the current password
            response = requests.post(url, json=payload)

            if response.status_code == 200:  # Authentication successful
                user = auth.get_user_by_email(user_email)  # Get the user's Firebase record
                auth.update_user(user.uid, password=new_password)  # Update the password in Firebase
                messages.success(request, 'Password changed successfully.', extra_tags='change_password_success')
                return render(request, 'home/profile.html', user_info)  # Return to profile page with a success message
            else:
                # Current password is incorrect
                messages.error(request, 'Current password is incorrect.', extra_tags='change_password_current_error')
                return render(request, 'home/profile.html', user_info)  # Return to profile page with an error

        except firebase_admin.auth.UserNotFoundError:  # Handle cases where the user is not found in Firebase
            messages.error(request, 'User not found.', extra_tags='change_password_user_not_found_error')
            return render(request, 'home/profile.html', user_info)  # Return to profile page with an error

        except Exception as e:  # Catch any other unexpected errors
            messages.error(request, f'Error occurred: {str(e)}', extra_tags='change_password_general_error')
            return render(request, 'home/profile.html', user_info)  # Return to profile page with a general error

    # Redirect to the profile page if the request is not a POST
    return redirect('profile')


import threading
import re
import subprocess
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils.timezone import localtime
from google.cloud import firestore
from .models import VideoUpload

# Function to execute Docker commands
def run_docker_command(command, cwd=None):
    try:
        print(f"Running Docker command: {command}")
        subprocess.run(command, cwd=cwd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(e)

def run_docker_command_async(command, cwd=None):
    """Run Docker command asynchronously in a new thread."""
    thread = threading.Thread(target=run_docker_command, args=(command, cwd))
    thread.start()

# Run these commands on boot if they haven't been run already
BOOT_COMMANDS_RUN = False  # Global flag to check if boot commands are run

def check_and_run_boot_commands():
    global BOOT_COMMANDS_RUN
    if not BOOT_COMMANDS_RUN:
        boot_directory = R"C:\Users\17344\Documents\Capstone2\CSC-4996-Footprint\footprint"
        run_docker_command("docker-compose build", cwd=boot_directory)
        run_docker_command("docker-compose up -d", cwd=boot_directory)  # Run in detached mode
        BOOT_COMMANDS_RUN = True

from django.http import JsonResponse
def clear_live_feeds_collection():
    # Reference the 'live_feeds' collection
    live_feeds_ref = db.collection('live_feeds')

    # Stream all documents in the collection
    docs = live_feeds_ref.stream()

    # Loop through each document and delete it
    for doc in docs:
        print(f"Deleting document {doc.id}")
        doc.reference.delete()

    print("All documents in 'live_feeds' collection have been deleted.")


@require_http_methods(["GET", "POST"])
def upload_view(request):
    # Ensure boot commands run before proceeding
    check_and_run_boot_commands()

    if request.method == 'POST':
        feed_name = request.POST.get('feed_name')
        youtube_link = request.POST.get('youtube_link')
        processing_speed = request.POST.get('processing_speed')
        
        # Retrieve the user's email from the session
        user_email = request.session.get('email')
        
        if not user_email:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "message": "User email not found in session. Please log in again."})
            else:
                messages.error(request, 'User email not found in session. Please log in again.')
                return redirect('login')

        if feed_name and youtube_link and processing_speed:
            # Validate YouTube URL
            youtube_regex = (
                r'^(https?://)?(www\.)?'
                r'(youtube\.com/watch\?v=|youtu\.be/)'
                r'([^&=%\?]{11})'
            )
            match = re.match(youtube_regex, youtube_link)
            if match:
                # Prepare data for Firestore
                feed_data = {
                    'feed_name': feed_name,
                    'speed': processing_speed,
                    'video_link': youtube_link,
                    'user_email': user_email,
                    'feed_status': 'queued',
                    'uploaded_at': firestore.SERVER_TIMESTAMP
                }
                
                # Save to Firestore and get the document reference and ID
                try:
                    doc_ref = db.collection('live_feeds').add(feed_data)
                    document_id = doc_ref[1].id
                    print(f"Feed added to Firestore successfully with ID: {document_id}")
                    
                    # Save the upload to the database
                    video_upload = VideoUpload.objects.create(
                        youtube_link=youtube_link,
                        processing_speed=processing_speed,
                        status='Pending',
                        user_email=user_email
                    )

                    # Prepare parameters for the Docker command and pass the document ID
                    script_directory = R"C:\Users\17344\Documents\Capstone2\CSC-4996-Footprint\footprint\home\static\AI_Scripts"
                    docker_command = f'docker-compose run --rm rq-worker python video_Enqueue.py "{youtube_link}" {processing_speed} "{user_email}" "{document_id}"'
                    
                    # Run the Docker command asynchronously
                    run_docker_command_async(docker_command, cwd=script_directory)

                    # For AJAX request, return a JSON response
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        # Format uploaded_at to match existing format
                        uploaded_at = datetime.now().strftime("%m/%d %I:%M %p")  
                        
                        return JsonResponse({
                            "success": True,
                            "message": "Feed added successfully to Firestore.",
                            "upload": {
                                "feed_name": feed_name,
                                "youtube_link": youtube_link,  # Include the YouTube link
                                "processing_speed": processing_speed,
                                "status": "queued",  # Default status for new uploads
                                "uploaded_at": uploaded_at,  # Use the formatted time
                                "job_id": document_id  # Include the job ID for dynamic updates
                            }
                        })

                    # For regular form submission, redirect
                    messages.success(request, "Feed added successfully to Firestore.")
                    return redirect('upload')

                except Exception as e:
                    error_message = f"Error adding feed to Firestore: {str(e)}"
                    print(error_message)
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({"success": False, "message": error_message})
                    else:
                        messages.error(request, error_message)
                        return redirect('dashboard')
            else:
                error_message = "Invalid YouTube link. Please enter a valid YouTube video URL."
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({"success": False, "message": error_message})
                else:
                    messages.error(request, error_message)
                    return redirect('upload')
        else:
            error_message = "Please fill in all required fields."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "message": error_message})
            else:
                messages.error(request, error_message)
                return redirect('upload')

    # Query live feeds and split them into "Upload Queue" and "Upload History"
    user_email = request.session.get('email')
    if user_email:
        live_feeds = db.collection("live_feeds").where("user_email", "==", user_email).order_by("uploaded_at", direction=firestore.Query.DESCENDING).stream()
    else:
        live_feeds = []
    
    upload_queue = []
    upload_history = []

    for feed in live_feeds:
        feed_data = feed.to_dict()
        feed_data['job_id'] = feed.id  # Add the document ID for reference
        feed_data['uploaded_at'] = feed_data['uploaded_at'].strftime("%m/%d %I:%M %p") if 'uploaded_at' in feed_data else "N/A"
        feed_data['updated_at'] = feed_data['updated_at'].strftime("%m/%d %I:%M %p") if 'updated_at' in feed_data else "N/A"
        feed_data['youtube_link'] = feed_data['video_link'] if 'video_link' in feed_data else None

        if feed_data['feed_status'] == 'finished':
            upload_history.append(feed_data)
        else:
            upload_queue.append(feed_data)

    return render(request, 'home/upload.html', {
        'upload_queue': upload_queue,
        'upload_history': upload_history
    })

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from google.cloud import firestore

@csrf_exempt
@require_POST
def delete_upload_view(request):
    job_id = request.POST.get('job_id')

    if not job_id:
        return JsonResponse({"success": False, "message": "Missing job ID."})

    try:
        # Reference Firestore and attempt to delete the job document
        job_ref = db.collection('live_feeds').document(job_id)
        job_data = job_ref.get()

        if job_data.exists:
            job_ref.delete()
            return JsonResponse({"success": True, "message": "Job deleted successfully."})
        else:
            return JsonResponse({"success": False, "message": "Job ID does not exist."})

    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error deleting job: {str(e)}"})
    

from django.http import JsonResponse
from google.cloud import firestore  # Firestore client
from google.cloud.firestore_v1 import _helpers  # Correct way to access Timestamp
from datetime import datetime

def check_job_status(request):
    try:
        # Fetch documents from Firestore ordered by "updated_at"
        live_feeds = db.collection("live_feeds").order_by("updated_at", direction=firestore.Query.DESCENDING).stream()
        upload_queue = []
        upload_history = []

        for feed in live_feeds:
            feed_data = feed.to_dict()
            uploaded_at = feed_data.get("uploaded_at")
            
            # Handle Firestore Timestamp conversion
            if uploaded_at and isinstance(uploaded_at, _helpers.Timestamp):
                uploaded_at = uploaded_at.to_datetime()
                uploaded_at = uploaded_at.strftime("%Y-%m-%d %H:%M")

            # Create job object
            job = {
                "job_id": feed.id,
                "feed_name": feed_data.get("feed_name"),
                "processing_speed": feed_data.get("speed"),
                "status": feed_data.get("feed_status"),
                "uploaded_at": uploaded_at or "",
            }

            # Categorize job into queue or history
            if feed_data.get("feed_status") == "finished":
                upload_history.append(job)
            else:
                upload_queue.append(job)

        # Return the JSON response
        return JsonResponse({"upload_queue": upload_queue, "upload_history": upload_history}, status=200)

    except Exception as e:
        # Log and return error response
        print(f"Error fetching job statuses: {e}")
        return JsonResponse({"error": "Could not fetch job statuses. Please try again later."}, status=500)






def search_attributes1(request):
    # Mapping for human-readable names
    attribute_names = {
        "short_hair": "Short Hair",
        "medium_hair": "Medium Hair",
        "long_hair": "Long Hair",
        "no_hair": "No Hair",
        "short_shirt": "Short Sleeved",
        "long_shirt": "Long Sleeved",
        "sleeveless_shirt": "Sleeveless Shirt",
        "no_shirt": "No Shirt",
        "short_pants": "Shorts",
        "long_pants": "Pants",
        "skirt": "Skirt",
        "black": "Black",
        "brown": "Brown",
        "red": "Red",
        "gray": "Gray",
        "blonde": "Blonde",
        "unnatural": "Unnatural",
        "green": "Green",
        "blue": "Blue",
        "white": "White",
        "orange": "Orange",
        "yellow": "Yellow",
        "purple": "Purple",
        "pink": "Pink",
        "beige": "Beige",
        "NULL": "Undetected",
        "Unknown": "Undetected"
    }

    # Helper function to format attributes
    def format_attribute(value):
        return attribute_names.get(value, value)  # Default to raw value if no mapping exists

    # Existing code
    user_email = request.session.get('email')
    live_feed_names = []
    items_per_page = 6

    # Validate page number
    page_number = request.GET.get('page', 1)
    try:
        page_number = int(page_number)
        if page_number < 1:
            page_number = 1
    except ValueError:
        page_number = 1

    if user_email:
        try:
            feeds_query = db.collection('live_feeds').where('user_email', '==', user_email).where('feed_status', '==', 'finished').stream()
            live_feed_names = [feed.to_dict().get('feed_name') for feed in feeds_query if 'feed_name' in feed.to_dict()]
        except Exception as e:
            messages.error(request, f"Error retrieving user feed names: {str(e)}")

    if request.method == 'POST':
        form_data = {
            'top_attribute': request.POST.get('top_attribute'),
            'top_color': request.POST.get('top_color'),
            'middle_attribute': request.POST.get('middle_attribute'),
            'middle_color': request.POST.get('middle_color'),
            'bottom_attribute': request.POST.get('bottom_attribute'),
            'bottom_color': request.POST.get('bottom_color'),
            'feed_name': request.POST.get('feed_name'),
        }
        query_string = urlencode(form_data)
        return redirect(f"{request.path}?{query_string}")

    top_attribute = request.GET.get('top_attribute')
    top_color = request.GET.get('top_color')
    middle_attribute = request.GET.get('middle_attribute')
    middle_color = request.GET.get('middle_color')
    bottom_attribute = request.GET.get('bottom_attribute')
    bottom_color = request.GET.get('bottom_color')
    feed_name = request.GET.get('feed_name')

    if not feed_name:
        return render(request, 'home/dashboard.html', {'feeds': live_feed_names})

    video_link = None
    speed = None
    try:
        feeds_query = db.collection('live_feeds').where('user_email', '==', user_email).where('feed_name', '==', feed_name).stream()
        for feed_doc in feeds_query:
            feed_data = feed_doc.to_dict()
            video_link = feed_data.get('video_link')
            speed = feed_data.get('speed')
            break

        if not video_link or not speed:
            messages.error(request, "No matching feed found for the given name.")
            return render(request, 'home/dashboard.html', {'feeds': live_feed_names})

    except Exception as e:
        messages.error(request, f"Error retrieving feed data: {str(e)}")
        return render(request, 'home/dashboard.html', {'feeds': live_feed_names})

    weights = {
        'top_type': 20,
        'top_color': 10,
        'middle_type': 25,
        'middle_color': 15,
        'bottom_type': 20,
        'bottom_color': 10
    }

    query = db.collection('IdentifiedPersons').where('user_email', '==', user_email).where('video_link', '==', video_link).where('speed', '==', speed)

    results = []
    try:
        docs = query.stream()
        for doc in docs:
            doc_data = doc.to_dict()

            # Generate detection_time_link dynamically
            video_link = doc_data.get('video_link')
            detection_time = doc_data.get('detection_time')
            detection_time_link = generate_detection_time_link(video_link, detection_time)
            
            doc_data['detection_time_link'] = detection_time_link


            score = 0
            unmatched_attributes = []

            if top_attribute:
                if doc_data.get('top_type') == top_attribute.lower():
                    score += weights['top_type']
                else:
                    unmatched_attributes.append('top_type')
            if top_color:
                if doc_data.get('top_color') == top_color.lower():
                    score += weights['top_color']
                else:
                    unmatched_attributes.append('top_color')
            if middle_attribute:
                if doc_data.get('middle_type') == middle_attribute.lower():
                    score += weights['middle_type']
                else:
                    unmatched_attributes.append('middle_type')
            if middle_color:
                if doc_data.get('middle_color') == middle_color.lower():
                    score += weights['middle_color']
                else:
                    unmatched_attributes.append('middle_color')
            if bottom_attribute:
                if doc_data.get('bottom_type') == bottom_attribute.lower():
                    score += weights['bottom_type']
                else:
                    unmatched_attributes.append('bottom_type')
            if bottom_color:
                if doc_data.get('bottom_color') == bottom_color.lower():
                    score += weights['bottom_color']
                else:
                    unmatched_attributes.append('bottom_color')

            if score == 100:
                match_percentage = "100%"
                priority = 0
            elif 70 <= score < 100:
                match_percentage = "70-90%"
                priority = 1
            elif 50 <= score < 70:
                match_percentage = "50-70%"
                priority = 2
            elif 30 <= score < 50:
                match_percentage = "30-50%"
                priority = 3
            elif 10 <= score < 30:
                match_percentage = "10-30%"
                priority = 4      
            else:
                continue

            results.append({
                'detection_time': format_time_detected(float(doc_data.get('detection_time'))),
                'detection_time_link': detection_time_link,
                'photo': doc_data.get('photo'),
                'feed_name': format_attribute(doc_data.get('feed_name')),
                'top_type': format_attribute(doc_data.get('top_type')),
                'top_color': format_attribute(doc_data.get('top_color')),
                'middle_type': format_attribute(doc_data.get('middle_type')),
                'middle_color':format_attribute(doc_data.get('middle_color')),
                'bottom_type': format_attribute(doc_data.get('bottom_type')),
                'bottom_color': format_attribute(doc_data.get('bottom_color')),
                'match_percentage': match_percentage,
                'priority': priority
            })

    except Exception as e:
        messages.error(request, f"Error querying database: {str(e)}")
        return render(request, 'home/dashboard.html', {'feeds': live_feed_names})


    results.sort(key=lambda x: x['priority'])
    paginator = Paginator(results, items_per_page)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'results': page_obj.object_list,
        'feeds': live_feed_names,
        'selections': {
            'top': {'attribute': top_attribute, 'color': top_color},
            'middle': {'attribute': middle_attribute, 'color': middle_color},
            'bottom': {'attribute': bottom_attribute, 'color': bottom_color},
            'feed_name': feed_name
        },
        'num_pages': paginator.num_pages,
        'page_number': page_obj.number,
    }
    return render(request, 'home/dashboard.html', context)


def format_time_detected(decimal_seconds):
    # Convert decimal seconds to total seconds
    total_seconds = int(decimal_seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Format time as hh:mm:ss
    return f"{hours:02}:{minutes:02}:{seconds:02}"



def generate_detection_time_link(video_link, detection_time):
    """
    Generates a YouTube link with embedded timestamp in seconds.
    :param video_link: Original YouTube link.
    :param detection_time: Time in seconds as a string.
    :return: Modified link with timestamp.
    """
    if not video_link or not detection_time:
        return None
    if "?" in video_link:
        return video_link + "&t=" + detection_time + "s"
    return video_link + "?t=" + detection_time + "s"

from django.conf import settings
from redis import Redis
from rq import Queue

# Connect to Redis using settings
redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
q = Queue(connection=redis_conn)