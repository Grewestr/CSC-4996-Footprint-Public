import sys
import os
import time
from Video_processing import q, process_video_url
from rq.job import Job
import Image_classification
import CSV_To_Firestore  # Import CSV_To_Firestore for final processing

# Path to tempdata.csv
tempdata_file = "/AI_Scripts/Identified_Person/tempdata.csv"

def enqueue_video(video_url, frame_interval, user_id):
    print(f"Adding {video_url} to the queue with interval of {frame_interval} for user {user_id}.")
    
    # Enqueue the video processing job
    job = q.enqueue(
        process_video_url, 
        video_url, 
        frame_interval, 
        user_id, 
        job_timeout=3600,        # Timeout execution 1 hour
        ttl=86400                # TTL 1 day - used for debugging for processing job status
    )
    
    print(f"Enqueued Job ID: {job.id}")
    return job

def wait_for_job_completion(job, timeout=600):
    start_time = time.time()
    while time.time() - start_time < timeout:
        job_status = job.get_status()
        print(f"Current Job Status: {job_status}")
        if job_status == 'finished':
            print("Job completed successfully.")
            time.sleep(5)
            return True
        elif job_status in ('failed', 'stopped'):
            print("Job failed or was stopped.")
            return False
        time.sleep(5)  # Wait 5 seconds before checking again
    print("Timeout waiting for job to complete.")
    return False

def wait_for_tempdata(max_retries=10, delay=3):
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
    # Check if tempdata.csv exists and output its contents for debugging
    if os.path.exists(tempdata_file):
        print("tempdata.csv exists. Contents:")
        with open(tempdata_file, 'r') as file:
            print(file.read())
    else:
        print("tempdata.csv does not exist at the time of reading.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python video_Enqueue.py <video_url> <interval> <user_id>")
        sys.exit(1)

    video_url = sys.argv[1]
    interval = int(sys.argv[2])
    user_id = sys.argv[3]

    # Step 1: Enqueue the video processing job
    job = enqueue_video(video_url, interval, user_id)
    
    # Step 2: Wait for video processing job to complete
    if wait_for_job_completion(job):
        # Step 3: Wait for tempdata.csv to be populated
        if wait_for_tempdata():
            # Debugging output for tempdata.csv contents
            debug_tempdata_file()
            
            # Step 4: Start image classification once tempdata.csv is ready
            print("Starting image classification...")
            Image_classification.main()
            print("Image classification completed.")
            
            # Step 5: Start CSV to Firestore upload
            print("Starting CSV to Firestore upload...")
            CSV_To_Firestore.main()
            print("CSV to Firestore upload completed.")
        else:
            print("Error: tempdata.csv was not ready, skipping image classification.")
    else:
        print("Error: Video processing job did not complete successfully, skipping image classification.")
