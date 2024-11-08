import re
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
import firebase_admin
from firebase_admin import auth, firestore, exceptions
import requests
from datetime import datetime, timedelta
import pytz
import random
from django.http import JsonResponse
import os
from google.cloud import firestore
from google.oauth2 import service_account
from google.cloud.firestore_v1 import FieldFilter


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
key_path = os.path.join(BASE_DIR, 'footprint', 'Firebase', 'serviceAccountKey.json')
credentials = service_account.Credentials.from_service_account_file(key_path)
db = firestore.Client(credentials=credentials)


firebase_api_key = 'AIzaSyBrnuE0rPIse9NIoJiV0kw2FMEGDXShjBQ'
url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}'

def homepage_view(request):
    return render(request, 'home/homepage.html')

def example_view(request):
    return render(request, 'home/example.html')

def dashboard_view(request):
    return render(request, 'home/dashboard.html')

def profile_view(request):
    # Retrieve user information from the session
    full_name = request.session.get('full_name', 'Not available')
    email = request.session.get('email', 'Not available')
    apartment_name = 'Not available'  # Placeholder value for now

    # Render the profile template with the user's info
    return render(request, 'home/profile.html', {
        'full_name': full_name,
        'email': email,
        'apartment_name': apartment_name
    })



def logout_view(request):
    logout(request) 
    return redirect('login')

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
                # Retrieve the role and other user info from Firestore 'users' collection
                user_ref = db.collection('users').document(email)
                user_data = user_ref.get()

                if user_data.exists:
                    user_info = user_data.to_dict()
                    role = user_info.get('role', 'user')  # Default to 'user' if no role found
                    full_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}"
                    
                    # Store user info in session
                    request.session['uid'] = user.uid  # Firebase UID
                    request.session['role'] = role  # User role
                    request.session['full_name'] = full_name  # Full name
                    request.session['email'] = email  # User email

                    # Redirect based on user role
                    if role == 'admin':
                        return redirect('admin_dashboard')
                    else:
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


def password_reset_view(request):
    
    # The URL for sending the password reset request to Firebase API
    reset_password_url = f'https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={firebase_api_key}'

    # Check if the request method is POST (i.e., the form was submitted)
    if request.method == 'POST':
        # Retrieve the email address from the submitted form
        email = request.POST.get('email')

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
    
    # If the request method is not POST, render the password reset form
    return render(request, 'home/password_reset.html')


# Define the desired time zone (UTC-4)
desired_timezone = pytz.timezone("America/New_York")  # This is UTC-4 when in daylight saving time



def results_view(request):
    # Render the results page without any data
    return render(request, 'home/results.html')

def delete_email_view(request):
    if request.method == 'POST':
        session_email = request.session.get('email')
        user_email = request.POST.get('email')
        current_password = request.POST.get('current_password')

        if not user_email or not current_password:
            messages.error(request, "Email or password missing.")
            return redirect('/profile/?delete_error=email_missing')  # Full URL with query string

        # Check if the entered email matches the email in the session
        if user_email != session_email:
            messages.error(request, "The email you entered does not match the one associated with your account.")
            return redirect('/profile/?delete_error=email_mismatch')  # Full URL with query string

        try:
            # Re-authenticate the user by checking the current password
            payload = {
                'email': user_email,
                'password': current_password,
                'returnSecureToken': True
            }
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                # If the password is correct, delete the user from Firebase
                user = auth.get_user_by_email(user_email)
                auth.delete_user(user.uid)
                
                # Delete user document from Firestore
                db.collection('users').document(user_email).delete()

                messages.success(request, "Your account has been successfully deleted.")
                return logout_view(request)  # Log out the user and clear session
            else:
                # If password is incorrect or email not found
                messages.error(request, "Incorrect password or email.")
                return redirect('/profile/?delete_error=password_mismatch')  # Full URL with query string

        except firebase_admin.auth.UserNotFoundError:
            messages.error(request, "User not found.")
        except Exception as e:
            messages.error(request, f"Error deleting account: {str(e)}")

    return redirect('/profile/')



def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        retype_password = request.POST.get('retype_password')

        # Validate that new passwords match
        if new_password != retype_password:
            messages.error(request, 'New password and retyped password do not match.')
            return render(request, 'profile.html', {'keep_modal_open': True})  # Keep modal open on error

        # Validate new password format
        if not re.search(r'^(?=.*[a-z])(?=.*[A-Z]).{8,}$', new_password):
            messages.error(request, 'Password must be at least 8 characters with one lowercase and one uppercase letter.')
            return render(request, 'home/profile.html', {'keep_modal_open': True})  # Keep modal open on error

        try:
            # Re-authenticate the user with the current password using Firebase
            user_email = request.session.get('email')
            payload = {
                'email': user_email,
                'password': current_password,
                'returnSecureToken': True
            }
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                # If current password is correct, update to new password
                user = auth.get_user_by_email(user_email)
                auth.update_user(user.uid, password=new_password)
                messages.success(request, 'Password changed successfully.')
            else:
                # Handle incorrect current password case
                messages.error(request, 'Current password is incorrect.')
                return render(request, 'home/profile.html', {'keep_modal_open': True})  # Keep modal open on error

        except firebase_admin.auth.UserNotFoundError:
            messages.error(request, 'User not found.')
            return render(request, 'home/profile.html', {'keep_modal_open': True})  # Keep modal open on error

        except Exception as e:
            messages.error(request, f'Error occurred: {str(e)}')
            return render(request, 'home/profile.html', {'keep_modal_open': True})  # Keep modal open on error

        return redirect('profile')  # Redirect on success

    return redirect('profile')


def search_person(request, summary):
    # Extract attributes from the summary
    bottom_color = summary.get('bottom_color')
    bottom_type = summary.get('bottom_type')
    middle_color = summary.get('middle_color')
    middle_type = summary.get('middle_type')
    top_color = summary.get('top_color')
    top_type = summary.get('top_type')
    camera = summary.get('camera')  # Camera number
    start_time = summary.get('start_time')  # Start of the time frame (string in ISO format)
    end_time = summary.get('end_time')  # End of the time frame (string in ISO format)

    # Convert the start and end time to Firestore-friendly UTC timestamps
    start_timestamp = datetime.strptime(start_time, "%Y-%m-%dT%H:%M").replace(tzinfo=pytz.UTC)
    end_timestamp = datetime.strptime(end_time, "%Y-%m-%dT%H:%M").replace(tzinfo=pytz.UTC)

    # Convert start and end timestamps to the desired display format
    formatted_start_time = start_timestamp.strftime("%B %d, %Y at %I:%M:%S %p")
    formatted_end_time = end_timestamp.strftime("%B %d, %Y at %I:%M:%S %p")

    results2 = []

    # Step 1: Query Firestore based on attributes (without timestamp filtering)
    query = db.collection('search_test') \
              .where('bottom_color', '==', bottom_color) \
              .where('bottom_type', '==', bottom_type) \
              .where('middle_color', '==', middle_color) \
              .where('middle_type', '==', middle_type) \
              .where('top_color', '==', top_color) \
              .where('top_type', '==', top_type) \
              .where('camera', '==', camera)

    # Step 2: Manually filter by the timestamp
    for doc in query.stream():
        doc_data = doc.to_dict()

        # Retrieve the document's timestamp and convert it to UTC if needed
        raw_timestamp = doc_data.get('timestamp')

        if isinstance(raw_timestamp, str):
            # Convert string timestamp to datetime (assuming the format is consistent)
            detection_time = datetime.strptime(raw_timestamp, "%B %d, %Y at %I:%M:%S %p UTC%z")
        else:
            detection_time = raw_timestamp  # If it's already a Firestore timestamp object

        # Check if the timestamp falls within the desired timeframe
        if start_timestamp <= detection_time <= end_timestamp:
            # Convert the UTC timestamp to the desired timezone (UTC-4)
            local_timestamp = detection_time.astimezone(desired_timezone)
            formatted_timestamp = local_timestamp.strftime("%B %d, %Y at %I:%M:%S %p")

            # Append the result with the formatted timestamp and other details
            results2.append({
                'timestamp': formatted_timestamp,
                'photo': doc_data.get('photo'),
                'camera': camera,
                'bottom_color': bottom_color,
                'bottom_type': bottom_type,
                'middle_color': middle_color,
                'middle_type': middle_type,
                'top_color': top_color,
                'top_type': top_type,
            })

    # Step 3: Return results to the frontend
    return render(request, 'home/results.html', {
        'results2': results2,
        'summary': summary,
        'formatted_start_time': formatted_start_time,
        'formatted_end_time': formatted_end_time
    })


def demo_input(request):
    # Simulated summary input (attributes to match and timeframe)
    summary = {
    'bottom_color': "black",
    'bottom_type': "long_pants",
    'middle_color': "black",
    'middle_type': "long_shirt",
    'top_color': "black",
    'top_type': "medium_hair",
    'camera': "1",  # Only search for camera 1
    'start_time': '2024-10-14T00:01',  # Start of the day for October 14, 2024
    'end_time': '2024-10-14T23:59'  # End of the day for October 14, 2024
}

    # Call the search_person function with the summarized input
    return search_person(request, summary)

import os
import re
import subprocess
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .models import VideoUpload

# Function to execute Docker commands
def run_docker_command(command, cwd=None):
    try:
        subprocess.run(command, cwd=cwd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(e)

# Run these commands on boot if they haven't been run already
BOOT_COMMANDS_RUN = False  # Global flag to check if boot commands are run

def check_and_run_boot_commands():
    global BOOT_COMMANDS_RUN
    if not BOOT_COMMANDS_RUN:
        boot_directory = "C:\\Users\\17344\\Documents\\Capstone2\\CSC-4996-Footprint\\footprint"
        run_docker_command("docker-compose build", cwd=boot_directory)
        run_docker_command("docker-compose up -d", cwd=boot_directory)  # Run in detached mode
        BOOT_COMMANDS_RUN = True

@require_http_methods(["GET", "POST"])
def upload_view(request):
    check_and_run_boot_commands()  # Ensure boot commands run before proceeding

    message = None
    if request.method == 'POST':
        youtube_link = request.POST.get('youtube_link')
        processing_speed = request.POST.get('processing_speed')
        user_id = request.user.id  # Assume user authentication is enabled

        if youtube_link and processing_speed:
            # Validate YouTube URL
            youtube_regex = (
                r'^(https?://)?(www\.)?'
                r'(youtube\.com/watch\?v=|youtu\.be/)'
                r'([^&=%\?]{11})'
            )
            match = re.match(youtube_regex, youtube_link)
            if match:
                video_id = match.group(4)
                
                # Save the upload to the database
                video_upload = VideoUpload.objects.create(
                    youtube_link=youtube_link,
                    processing_speed=processing_speed,
                    status='Pending'
                )

                # Prepare parameters for the Docker command
                script_directory = "C:\\Users\\17344\\Documents\\Capstone2\\CSC-4996-Footprint\\footprint\\home\\static\\AI_Scripts"
                docker_command = f'docker-compose run --rm rq-worker python video_Enqueue.py "{youtube_link}" {processing_speed} "{user_id}"'
                
                # Run the Docker command to process the video
                run_docker_command(docker_command, cwd=script_directory)
                
                message = "Your video has been successfully submitted for processing."
                return redirect('upload')  # Redirect to prevent form resubmission
            else:
                message = "Invalid YouTube link. Please enter a valid YouTube video URL."
        else:
            message = "Please fill in all required fields."

    # Retrieve the list of uploads to display in the queue
    uploads = VideoUpload.objects.all().order_by('-uploaded_at')
    return render(request, 'home/upload.html', {'message': message, 'uploads': uploads})




def search_attributes(request):
    if request.method == 'POST':
        # Retrieve all selections from the form data
        top_attribute = request.POST.get('top_attribute')
        top_color = request.POST.get('top_color')
        middle_attribute = request.POST.get('middle_attribute')
        middle_color = request.POST.get('middle_color')
        bottom_attribute = request.POST.get('bottom_attribute')
        bottom_color = request.POST.get('bottom_color')
        from_date = request.POST.get('from_date')
        from_time = request.POST.get('from_time')
        to_date = request.POST.get('to_date')
        to_time = request.POST.get('to_time')
        camera = request.POST.get('camera')

        # Combine date and time into datetime objects
        try:
            from_datetime_str = f"{from_date} {from_time}"
            to_datetime_str = f"{to_date} {to_time}"
            from_datetime = datetime.strptime(from_datetime_str, '%Y-%m-%d %H:%M')
            to_datetime = datetime.strptime(to_datetime_str, '%Y-%m-%d %H:%M')

            # Convert to UTC timezone
            from_datetime = pytz.utc.localize(from_datetime)
            to_datetime = pytz.utc.localize(to_datetime)
        except Exception as e:
            messages.error(request, f"Error parsing dates: {str(e)}")
            return render(request, 'home/dashboard.html')

        # Build the query based on provided attributes and timestamp range
        query = db.collection('search_test')

        # query parameters for printing
        query_params = []

        # Include top attribute and color in the query
        if top_attribute:
            query = query.where(filter=FieldFilter('top_type', '==', top_attribute.lower()))
            query_params.append(f"top_type == {top_attribute.lower()}")
        if top_color:
            query = query.where(filter=FieldFilter('top_color', '==', top_color.lower()))
            query_params.append(f"top_color == {top_color.lower()}")

        # Include middle attribute and color
        if middle_attribute:
            query = query.where(filter=FieldFilter('middle_type', '==', middle_attribute.lower()))
            query_params.append(f"middle_type == {middle_attribute.lower()}")
        if middle_color:
            query = query.where(filter=FieldFilter('middle_color', '==', middle_color.lower()))
            query_params.append(f"middle_color == {middle_color.lower()}")

        # Include bottom attribute and color
        if bottom_attribute:
            query = query.where(filter=FieldFilter('bottom_type', '==', bottom_attribute.lower()))
            query_params.append(f"bottom_type == {bottom_attribute.lower()}")
        if bottom_color:
            query = query.where(filter=FieldFilter('bottom_color', '==', bottom_color.lower()))
            query_params.append(f"bottom_color == {bottom_color.lower()}")

        # Include camera
        if camera:
            query = query.where(filter=FieldFilter('camera', '==', camera))
            query_params.append(f"camera == {camera}")

        # Add timestamp filtering
        query = query.where(filter=FieldFilter('timestamp', '>=', from_datetime))
        query = query.where(filter=FieldFilter('timestamp', '<=', to_datetime))
        query_params.append(f"timestamp >= {from_datetime}")
        query_params.append(f"timestamp <= {to_datetime}")

        # Printing the search parameters to the terminal
        print("Search Parameters:")
        print(f"From datetime: {from_datetime}")
        print(f"To datetime: {to_datetime}")
        print(f"Camera: {camera}")
        print("Query Parameters:")
        for param in query_params:
            print(f"- {param}")

        # Execute the query
        results = []
        try:
            print("Entered the try block.")
            docs = query.stream()
            print("Query executed successfully.")
            for doc in docs:
                doc_data = doc.to_dict()
                print(f"Retrieved Document ID: {doc.id}, Data: {doc_data}")
                timestamp = doc_data.get('timestamp')
                if timestamp:
                    # Ensure timestamp is timezone-aware
                    if not timestamp.tzinfo:
                        timestamp = timestamp.replace(tzinfo=pytz.utc)
                    timestamp_dt = timestamp

                    results.append({
                        'timestamp': timestamp_dt,
                        'photo': doc_data.get('photo'),
                        'camera': doc_data.get('camera'),
                        'top_type': doc_data.get('top_type'),
                        'top_color': doc_data.get('top_color'),
                        'middle_type': doc_data.get('middle_type'),
                        'middle_color': doc_data.get('middle_color'),
                        'bottom_type': doc_data.get('bottom_type'),
                        'bottom_color': doc_data.get('bottom_color')
                    })
            print(f"Number of results found: {len(results)}")
        except Exception as e:
            print(f"Exception occurred: {e}")
            messages.error(request, f"Error querying database: {str(e)}")
            return render(request, 'home/dashboard.html')

        # Pass the results to the template
        context = {
            'results': results,
            'selections': {
                'top': {'attribute': top_attribute, 'color': top_color},
                'middle': {'attribute': middle_attribute, 'color': middle_color},
                'bottom': {'attribute': bottom_attribute, 'color': bottom_color},
                'timeframe': f"From {from_date} {from_time} to {to_date} {to_time}",
                'camera': camera
            },
            'from_date': from_date,
            'from_time': from_time,
            'to_date': to_date,
            'to_time': to_time
        }

        return render(request, 'home/dashboard.html', context)
    else:
        return redirect('dashboard')
    

from django.conf import settings
from redis import Redis
from rq import Queue

# Connect to Redis using settings
redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
q = Queue(connection=redis_conn)