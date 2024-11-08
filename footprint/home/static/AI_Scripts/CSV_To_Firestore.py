import firebase_admin
from firebase_admin import credentials, firestore, storage
import csv
import os
from datetime import datetime, timedelta

# Initialize Firebase
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'footprint-2024.appspot.com'  # Correctly specify the storage bucket name
})

# Initialize Firestore and Storage
db = firestore.client()
bucket = storage.bucket()

def parse_and_save_clothing_data(csv_file):
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:

            image_hash = row['Image Hash']
            image_path = f'Identified_Person/{row['Image Name']}'

            # Upload image to Firebase Storage if it exists
            image_url = None
            storage_path = None
            
            if os.path.exists(image_path):
                try:
                    # Update the blob path to save images in the Identified_Persons folder
                    blob = bucket.blob(image_path)
                    blob.upload_from_filename(image_path) # Saving in folder, can change path to not save in folder
                    
                    # Make the file public
                    blob.make_public()
                    
                    storage_path = blob.name
                    image_url = blob.public_url
                except Exception as e:
                    print(f"Error uploading image {image_path}: {e}")
            else:
                print(f"Image path does not exist: {image_path}")
            
            data = {
                'top_type': row['Top Type'],
                'top_color': row['Top Color'],
                'middle_type': row['Middle Type'],
                'middle_color': row['Middle Color'],
                'bottom_type': row['Bottom Type'],
                'bottom_color': row['Bottom Color'],
                'detection_time': row['Time Detected'],
                'detection_time_link': row['TimeStamped Video URL'],
                'video_link': row['Original Link'],
                'speed': row['Frame Interval'],
                'user_email': row['User ID'],
                'photo': image_url # Use get_image_url for photo?
            }
            
            # Save to Firestore using image_hash as document ID
            db.collection('IdentifiedPersons').document(image_hash).set(data)
            print(f"Saved entry for image hash: {image_hash}")

parse_and_save_clothing_data('clothing_attributes.csv')
print("All data has been parsed and saved to Firestore.")