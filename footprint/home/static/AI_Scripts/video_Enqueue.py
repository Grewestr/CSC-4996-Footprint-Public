import sys
import os
import time
from Video_processing import q, process_video_url
from rq.job import Job
import Image_classification
import CSV_To_Firestore
from google.cloud import firestore
from google.oauth2 import service_account

# Paths for tempdata.csv and serviceAccountKey.json
tempdata_file = "/AI_Scripts/Identified_Person/tempdata.csv"
key_path = "/footprint/Firebase/serviceAccountKey.json"

# Set up Firestore client
credentials = service_account.Credentials.from_service_account_file(key_path)
db = firestore.Client(credentials=credentials)

def enqueue_video(video_url, frame_interval, user_id, document_id):
    print(f"Attempting to add {video_url} to the queue with interval of {frame_interval} for user {user_id}.")
    
    # Enqueue the video processing job
    job = q.enqueue(
        process_video_url, 
        video_url, 
        frame_interval, 
        user_id, 
        job_timeout=3600, 
        ttl=86400  
    )
    
    print(f"Enqueued Job ID: {job.id} and Firestore Document ID: {document_id}")
    return job

def update_status_in_firestore(document_id, status):
    """Update job status in Firestore using the document ID."""
    job_ref = db.collection('live_feeds').document(document_id)
    job_ref.update({
        'feed_status': status,
        'updated_at': firestore.SERVER_TIMESTAMP
    })

def wait_for_job_completion(job, document_id, timeout=600):
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        job_status = job.get_status()
        print(f"Current Job Status: {job_status}")
        
        # Update Firestore with the job status
        update_status_in_firestore(document_id, job_status)

        if job_status == 'finished':
            print("Job completed successfully.")
            return True
        elif job_status in ('failed', 'stopped'):
            print("Job failed or was stopped.")
            return False
        time.sleep(5)  # Wait 5 seconds before checking again
    
    print("Timeout waiting for job to complete.")
    return False

def wait_for_tempdata(max_retries=20, delay=5):
    """Wait until tempdata.csv is populated or timeout occurs."""
    print(f"Waiting for tempdata.csv to populate...")
    for attempt in range(max_retries):
        if os.path.exists(tempdata_file):
            with open(tempdata_file, 'r') as file:
                lines = file.readlines()
                if len(lines) > 1:
                    print("tempdata.csv is populated and ready.")
                    return True
        print(f"Waiting for tempdata.csv to be populated (Attempt {attempt + 1}/{max_retries})...")
        time.sleep(delay)
    print("Warning: tempdata.csv was not populated in time.")
    return False

def debug_tempdata_file():
    """Output contents of tempdata.csv for debugging."""
    if os.path.exists(tempdata_file):
        print("tempdata.csv exists. Contents:")
        with open(tempdata_file, 'r') as file:
            print(file.read())
    else:
        print("tempdata.csv does not exist at the time of reading.")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python video_Enqueue.py <video_url> <interval> <user_id> <document_id>")
        sys.exit(1)

    video_url = sys.argv[1]
    interval = int(sys.argv[2])
    user_id = sys.argv[3]
    document_id = sys.argv[4]  # Receive document ID

    # Enqueue the video processing job
    job = enqueue_video(video_url, interval, user_id, document_id)
    
    # Wait for video processing job to complete
    if wait_for_job_completion(job, document_id):
        # Wait for tempdata.csv to be populated, only after job completion
        if wait_for_tempdata():
            # Debugging output for tempdata.csv contents
            debug_tempdata_file()
            
            # Start image classification once tempdata.csv is ready
            print("Starting image classification...")
            Image_classification.main()
            print("Image classification completed.")
            
            # Start CSV to Firestore upload
            print("Starting CSV to Firestore upload...")
            CSV_To_Firestore.main()
            print("CSV to Firestore upload completed.")
        else:
            print("Error: tempdata.csv was not ready, skipping image classification.")
    else:
        print("Error: Video processing job did not complete successfully, skipping image classification.")
