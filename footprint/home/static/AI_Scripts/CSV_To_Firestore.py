import firebase_admin
from firebase_admin import credentials, firestore, storage
import csv
import os

# Initialize Firebase
cred = credentials.Certificate('/AI_Scripts/serviceAccountKey.json')  # Ensure the key file is available within Docker
firebase_admin.initialize_app(cred, {
    'storageBucket': 'footprint-2024.appspot.com'
})

# Initialize Firestore and Storage
db = firestore.client()
bucket = storage.bucket()

# Load tempdata with normalized keys
def load_tempdata(temp_file_path):
    tempdata = {}
    with open(temp_file_path, 'r') as temp_file:
        temp_reader = csv.reader(temp_file)
        for row in temp_reader:
            if len(row) >= 5:
                image_name, user_id, timestamp, video_url, frame_interval = row
                tempdata[image_name] = {
                    'user_email': user_id,
                    'detection_time': timestamp,
                    'video_link': video_url,
                    'speed': frame_interval
                }
    return tempdata

# Parse clothing data, update with tempdata, and upload to Firebase
def parse_and_save_clothing_data(clothing_csv, tempdata):
    updated_rows = []

    with open(clothing_csv, 'r') as file:
        csv_reader = csv.DictReader(file)
        fieldnames = csv_reader.fieldnames

        # Extend fieldnames with any new keys in tempdata
        additional_fields = {'detection_time', 'speed', 'video_link', 'photo', 'user_email'}
        fieldnames = list(set(fieldnames) | additional_fields)  # Union of original fieldnames and additional fields

        for row in csv_reader:
            image_name = row['Image Name']
            image_path = f"Identified_Person/{image_name}"
            image_url = None

            # Update row with tempdata if available
            if image_name in tempdata:
                row.update(tempdata[image_name])
            else:
                print(f"No matching data in tempdata for {image_name}")

            # Upload image to Firebase Storage if it exists
            if os.path.exists(image_path):
                try:
                    blob = bucket.blob(image_path)
                    blob.upload_from_filename(image_path)
                    blob.make_public()
                    image_url = blob.public_url
                    row['photo'] = image_url
                except Exception as e:
                    print(f"Error uploading image {image_path}: {e}")
            else:
                print(f"Image path does not exist: {image_path}")

            # Prepare data for Firestore
            data = {
                'top_type': row['Top Type'],
                'top_color': row['Top Color'],
                'middle_type': row['Middle Type'],
                'middle_color': row['Middle Color'],
                'bottom_type': row['Bottom Type'],
                'bottom_color': row['Bottom Color'],
                'detection_time': row.get('detection_time', 'Unknown'),
                'detection_time_link': row.get('detection_time_link', 'Unknown'),
                'video_link': row.get('video_link', 'Unknown'),
                'speed': row.get('speed', 'Unknown'),
                'user_email': row.get('user_email', 'Unknown'),
                'photo': image_url
            }

            # Save to Firestore using image_hash as document ID
            image_hash = row['Image Hash']
            db.collection('IdentifiedPersons').document(image_hash).set(data)
            print(f"Saved entry for image hash: {image_hash}")

            # Append updated row to save back to clothing_attributes.csv
            updated_rows.append(row)

    # Write updated data back to clothing_attributes.csv
    with open(clothing_csv, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    print("Updated clothing_attributes.csv with data from tempdata.csv.")

def main():
    clothing_csv = '/AI_Scripts/clothing_attributes.csv'
    tempdata_csv = '/AI_Scripts/Identified_Person/tempdata.csv'

    # Load tempdata
    tempdata = load_tempdata(tempdata_csv)

    # Parse, update, and save clothing data
    parse_and_save_clothing_data(clothing_csv, tempdata)
    print("All data has been parsed, updated, and saved to Firestore.")

if __name__ == "__main__":
    main()
