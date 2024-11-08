import firebase_admin
from firebase_admin import credentials, firestore, storage
import csv
import os
from datetime import datetime, timedelta

# Initialize Firebase
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'gs://footprint-2024.appspot.com': 'footprint-test-ad8e7.appspot.com'  # Replace with your bucket name
})

# Initialize Firestore and Storage
db = firestore.client()
bucket = storage.bucket()

def parse_and_save_clothing_data(csv_file):
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:

            image_hash = row['Image Hash']
            image_path = row['Image']

            # Upload image to Firebase Storage if it exists
            image_url = None
            if os.path.exists(image_path):
                blob = bucket.blob(f'Identified_People/{image_hash}.jpg')
                blob.upload_from_filename(image_path)
                
                # Make the file publicly accessible (optional)
                blob.make_public()
                
                storage_path = blob.name
            
            data = {
                'top_type': row['Top Type'],
                'top_color': row['Top Color'],
                'middle_type': row['Middle Type'],
                'middle_color': row['Middle Color'],
                'bottom_type': row['Bottom Type'],
                'bottom_color': row['Bottom Color'],
                'time_detected': row['Time Detected'], # Keep as string?
                'video_link': row['Video Link'],
                'user_id': row['User ID']
            }
            
            # Save to Firestore using image_hash as document ID
            db.collection('IdentifiedPersons').document(image_hash).set(data)
            print(f"Saved entry for image hash: {image_hash}")

def get_image_url(storage_path, expiration_minutes=15):
    if storage_path:
        blob = bucket.blob(storage_path)
        # Generate a signed URL that expires in specified minutes
        url = blob.generate_signed_url(
            version='v4',
            expiration=datetime.now(datetime.UTC) + timedelta(minutes=expiration_minutes),
            method='GET'
        )
        return url
    return None

def get_clothing_data_with_image(image_hash):
    doc_ref = db.collection('clothing_attributes').document(image_hash)
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        if 'storage_path' in data and data['storage_path']:
            # Generate a temporary signed URL when needed
            data['image_url'] = get_image_url(data['storage_path'])
        return data
    return None

parse_and_save_clothing_data('clothing_attributes.csv')
print("All data has been parsed and saved to Firestore.")