import os
import cv2
import torch
import numpy as np
import yt_dlp
from rq import Queue
from redis import Redis
import csv
import hashlib

# Redis connection
redis_conn = Redis(host='redis-server', port=6379)
q = Queue(connection=redis_conn)

# Resize image for uniformity
target_size = (256, 256)

# Delete all contents of the Identified_Person folder
def clear_identified_person_folder(folder="Identified_Person"):
    if os.path.exists(folder):
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

clear_identified_person_folder()  # Clear folder at the start of the program

# Generate a 16 length hash for each image - used for database
def generate_image_hash(image):
    _, img_encoded = cv2.imencode(".jpg", image)
    image_data = img_encoded.tobytes()
    md5_hash = hashlib.md5(image_data).hexdigest()
    return md5_hash[:16]

# resizes the image based off the target_size of the prediction boxes
def resize_with_padding(image, target_size):
    height, width = image.shape[:2]
    scale = min(target_size[0] / height, target_size[1] / width)

    # Adding to the Width / Height of the original bounding box predictions
    new_w, new_h = int(width * scale), int(height * scale)
    resized_image = cv2.resize(image, (new_w, new_h))

    padded_image = np.full((target_size[1], target_size[0], 3), 255, dtype=np.uint8)
    pad_w = (target_size[0] - new_w) // 2
    pad_h = (target_size[1] - new_h) // 2
    padded_image[pad_h:pad_h + new_h, pad_w:pad_w + new_w] = resized_image

    #return modificed padded image
    return padded_image

# Augment image data with relevent information to pass to image_classification.py for additional modification
def augment_and_save(image, idx, user_id, timestamp, video_url, frame_interval, output_folder="Identified_Person"):
    os.makedirs(output_folder, exist_ok=True)
    # Add additional padding
    resized_image = resize_with_padding(image, target_size)
    # Create Unique Hash Value
    image_hash = generate_image_hash(image)
    # Make the image name the same as the hash
    image_name = f"{image_hash}.jpg"

    save_path = os.path.join(output_folder, image_name)

    cv2.imwrite(save_path, resized_image)
    print(f"Saved image: {save_path}")

    with open(f"{output_folder}/tempdata.csv", 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([image_name, user_id, timestamp, video_url, frame_interval])

# Process User Video with frame interval (Ex. 1 , 5, or 10)
def process_video_url(video_url, frame_interval, user_id):
    # Used for Debugging
    print(f"Processing video URL: {video_url} with frame interval of {frame_interval} for user ID {user_id}")
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    model.classes = [0] # Person Class  Yolov5s

    #Retrieving youtube video with the "best" quality possible
    ydl_opts = {'format': 'best', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        best_video_url = info['url']

    cap = cv2.VideoCapture(best_video_url)
    if not cap.isOpened():
        print(f"Error: Could not open video source {video_url}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * frame_interval)

    person_idx = 0
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frames_to_skip == 0:
            frame = cv2.resize(frame, (640, 480)) # resize image
            timestamp = round(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000, 2)

            results = model(frame)
            person_detections = results.pred[0] # calling person prediction

            confidence_threshold = 0.70 # threshold for person detected at 70%
            for detection in person_detections:
                if detection[-1] == 0:
                    x_min, y_min, x_max, y_max, confidence = detection[:5]
                    if confidence >= confidence_threshold:
                        x_min, y_min, x_max, y_max = map(int, [x_min, y_min, x_max, y_max])
                        margin = 20
                        # extending the margin of the bounding box for person detection
                        x_min_extended = max(0, x_min - margin)
                        y_min_extended = max(0, y_min - margin)
                        x_max_extended = min(frame.shape[1], x_max + margin)
                        y_max_extended = min(frame.shape[0], y_max + margin)
                        #cropping person out of original video fram
                        person_crop = frame[y_min_extended:y_max_extended, x_min_extended:x_max_extended]
                        augment_and_save(person_crop, person_idx, user_id, timestamp, video_url, frame_interval)
                        person_idx += 1
        # Interval for frame detection (minimum value as 1 frame per-second)
        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()
