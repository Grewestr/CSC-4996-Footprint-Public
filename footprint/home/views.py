
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
import firebase_admin
from firebase_admin import auth, firestore, exceptions
import requests
from datetime import datetime, timedelta
import pytz
import random


db = firestore.client()

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

def test_attribute_search(request):
    # Define the criteria for matching attributes
    bottom_color = "blue"
    bottom_type = "pants"
    middle_color = "red"
    middle_type = "short shirt"  
    top_color = "black"
    top_type = "short"
    camera = "1"  # Specify the camera as a string to match Firestore storage

    results = []

    # Step 1: Query documents based on the specified attributes and camera
    query = db.collection('search_test') \
              .where('bottom_color', '==', bottom_color) \
              .where('bottom_type', '==', bottom_type) \
              .where('middle_color', '==', middle_color) \
              .where('middle_type', '==', middle_type) \
              .where('top_color', '==', top_color) \
              .where('top_type', '==', top_type) \
              .where('camera', '==', camera)

    # Step 2: Retrieve matching documents and append timestamp and photo to results
    for doc in query.stream():
        doc_data = doc.to_dict()

        # Retrieve and format the timestamp
        raw_timestamp = doc_data.get('timestamp')

        # Convert Firestore UTC timestamp to local timezone (UTC-4)
        if isinstance(raw_timestamp, datetime):
            # Convert the UTC timestamp to the desired time zone (UTC-4)
            local_timestamp = raw_timestamp.astimezone(desired_timezone)
            formatted_timestamp = local_timestamp.strftime("%B %d, %Y at %I:%M:%S %p UTC%z")
        else:
            formatted_timestamp = raw_timestamp  # In case it's already a string

        results.append({
            'timestamp': formatted_timestamp,
            'photo': doc_data.get('photo'),
            'camera': camera
        })

    # Render the results page with the retrieved data
    return render(request, 'home/results.html', {'results': results})

def results_view(request):
    # Render the results page without any data
    return render(request, 'home/results.html')

def delete_email_view(request):
    if request.method == 'POST':
        user_email = request.session.get('email')
        
        if not user_email:
            messages.error(request, "No email found in session.")
            return redirect('profile')

        try:
            # Delete the user from Firebase Authentication
            user = auth.get_user_by_email(user_email)
            auth.delete_user(user.uid)
            
            # Delete the user document from Firestore
            db.collection('users').document(user_email).delete()

            messages.success(request, "Your account has been successfully deleted.")
            # Call logout_view to handle session clearing and redirection
            return logout_view(request)
        
        except firebase_admin.auth.UserNotFoundError:
            messages.error(request, "User not found.")
        except Exception as e:
            messages.error(request, f"Error deleting account: {str(e)}")
    
    return redirect('profile')


def change_password_view(request):
    if request.method == 'POST':
        # Retrieve the user's email and new password from the session and form
        user_email = request.session.get('email')
        new_password = request.POST.get('new_password')

        if not user_email:
            messages.error(request, "No email found in session.")
            return redirect('profile')

        try:
            # Retrieve the user by email and update the password
            user = auth.get_user_by_email(user_email)
            auth.update_user(user.uid, password=new_password)

            messages.success(request, "Your password has been successfully changed.")
            return redirect('profile')
        
        except firebase_admin.auth.UserNotFoundError:
            messages.error(request, "User not found.")
        except Exception as e:
            messages.error(request, f"Error changing password: {str(e)}")
    
    return redirect('profile')



def generate_persons(request):
    # Define the possible attribute values
    top_types = ["short_hair", "medium_hair", "long_hair", "hat", "bald"]
    top_colors = ["red", "yellow", "green", "orange", "black", "white", "purple", "blue"]
    middle_types = ["short_shirt", "long_shirt", "no_shirt", "tank top", "no shirt"]
    middle_colors = ["red", "yellow", "green", "orange", "black", "white", "purple", "blue", "pink"]
    bottom_types = ["short_pants", "long_pants", "skirt", "dress"]
    bottom_colors = ["red", "yellow", "green", "orange", "black", "white", "purple", "blue", "pink"]
    camera_numbers = ["1", "2"]

    # Define the time range for timestamps
    start_date = datetime(2024, 10, 20, tzinfo=pytz.UTC)
    end_date = datetime(2024, 10, 23, tzinfo=pytz.UTC)

    # Function to generate a random timestamp between two dates
    def random_timestamp(start, end):
        delta = end - start
        random_seconds = random.randint(0, int(delta.total_seconds()))
        return start + timedelta(seconds=random_seconds)

    # Function to generate a random document with the specified attribute ranges
    def generate_random_document():
        return {
            'bottom_color': random.choice(bottom_colors),
            'bottom_type': random.choice(bottom_types),
            'camera': random.choice(camera_numbers),
            'middle_color': random.choice(middle_colors),
            'middle_type': random.choice(middle_types),
            'photo': "URL",
            'timestamp': random_timestamp(start_date, end_date),
            'top_color': random.choice(top_colors),
            'top_type': random.choice(top_types),
        }

    # Generate and add 20 documents to the 'search_test' collection
    for _ in range(10):
        doc_data = generate_random_document()
        db.collection('search_test').add(doc_data)  # Automatically generate ID
        print(f"Added document with data: {doc_data}")

    # Provide feedback to the user
    messages.success(request, "20 random documents have been successfully added to Firestore.")
    
    # Redirect back to the dashboard or any other appropriate page
    return render(request, 'home/homepage.html')



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