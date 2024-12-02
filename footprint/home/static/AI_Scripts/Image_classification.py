import os
import cv2
import base64
import csv
import numpy as np
from inference_sdk import InferenceHTTPClient
from sklearn.metrics.pairwise import euclidean_distances
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from color_diff import delta_e_cie2000

# Define paths relative to the container’s working directory
input_folder = "/AI_Scripts/Identified_Person"
output_file = "/AI_Scripts/clothing_attributes.csv"

# Define color labels for hair as top color
HAIR_COLOR_LABELS = {
    "black_hair": "black",
    "brown_hair": "brown",
    "unnatural_hair": "unnatural",
    "blonde_hair": "blonde",
    "red_hair": "red",
    "gray_hair": "gray"
}

# API key from Roboflow
api_key = "Pfw3FTgzvlGSZu4M5pPj"
CLIENT = InferenceHTTPClient(api_url="https://detect.roboflow.com", api_key=api_key)

# Detect clothing attributes from Identified_Person
def detect_clothing_attributes(person_crop):
    _, img_encoded = cv2.imencode(".jpg", person_crop)
    img_base64 = base64.b64encode(img_encoded).decode("utf-8")
    try:
        result = CLIENT.infer(img_base64, model_id="clothing-detection-2/11") #Clothing Detection Model
        return result['predictions']
    except Exception as e:
        print(f"Inference for clothing attributes failed: {e}")
        return []

# Detect top color from person_crop
def detect_top_color(person_crop):
    _, img_encoded = cv2.imencode(".jpg", person_crop)
    img_base64 = base64.b64encode(img_encoded).decode("utf-8")
    try:
        result = CLIENT.infer(img_base64, model_id="hair_color_detection/10") # Hair Color Detection Model
        return result['predictions']
    except Exception as e:
        print(f"Inference for top color failed: {e}")
        return []

# Map hair color class to top color
def map_top_color(hair_color_class):
    return HAIR_COLOR_LABELS.get(hair_color_class, "Unknown")

# Function to get bounding box
def get_bounding_box(prediction):
    return [
        prediction['x'],
        prediction['y'],
        prediction['width'],
        prediction['height']
    ]

# Calculate dominant color in a bounding box
def dominant_color_detection(image, bbox, middle_or_bottom):
    x, y, width, height = bbox

    if middle_or_bottom == 'pants':
        x_start = max(0, x - width // 2)
        y_start = max(0, y - height // 2)
        x_end = min(image.shape[1], x + width // 2)
        y_end = min(image.shape[0], y)
    else:
        x_start = max(0, x - width // 2)
        y_start = max(0, y - height // 2)
        x_end = min(image.shape[1], x + width // 2)
        y_end = min(image.shape[0], y + height // 2)

    x_start = int(x_start * 1.1)
    y_start = int(y_start * 1.1)
    x_end = int(x_end * 1.1)
    y_end = int(y_end * 1.1)
    
    subimage = image[y_start:y_end, x_start:x_end]
    subimage = cv2.cvtColor(subimage, cv2.COLOR_BGR2RGB)
    pixels = subimage.reshape(-1, 3)
    _, labels, centers = cv2.kmeans(data=np.float32(pixels), K=3, bestLabels=None,
                                    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.2),
                                    attempts=10, flags=cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    dominant_color = centers[np.argmax(np.bincount(labels.flatten()))]
    return dominant_color

# Convert RGB to Lab color space
def rgb_to_lab(rgb):
    srgb = sRGBColor(rgb[0], rgb[1], rgb[2], is_upscaled=True)
    lab = convert_color(srgb, LabColor)
    return lab.lab_l, lab.lab_a, lab.lab_b

# Detect color based on Lab values
def detect_color(rgb_tuple):
    l, a, b = rgb_to_lab(rgb_tuple)
    color_ranges = [
        ("black", 0, 0, 0),
        ("white", 100, 0, 0),
        ("gray", 50, 0, 0),
        ("gray", 25, 0, 0), # Dark gray
        ("brown", 30, 19, 25),
        ("brown", 45, 5, 14), # Light brown but not beige
        ("beige", 70, 10, 20),
        ("red", 53, 80, 67),
        ("red", 25, 50, 40), # Dark red
        ("orange", 62, 34, 62),
        ("orange", 64, 56, 50), # Peachy orange 
        ("orange", 58, 65, 75), # Dark orange
        ("yellow", 97, -21, 94),
        ("yellow", 85, 0, 60), # Light yellow
        ("green", 46, -51, 50),
        ("green", 75, -30, 30), # Light green
        ("blue", 32, 79, -108),
        ("blue", 65, -10, -30), # Light blue
        ("blue", 45.84, -0.65, -15.4),# Jean blue
        ("purple", 29, 58, -36),
        ("purple", 50, 60, -68), # Light purple
        ("purple", 40, 83, -93), # Purple with blue tint
        ("pink", 75, 31, -6)
    ]
    
    # Create a LabColor object for the input color
    color_to_detect = LabColor(lab_l=l, lab_a=a, lab_b=b)
    
    # Calculate Delta-E for each predefined color
    min_distance = float('inf')
    closest_color = None
    for color_name, l2, a2, b2 in color_ranges:
        reference_color = LabColor(lab_l=l2, lab_a=a2, lab_b=b2)
        delta_e = delta_e_cie2000(color_to_detect, reference_color)
        if delta_e < min_distance:
            min_distance = delta_e
            closest_color = color_name

    return closest_color

# Process image for clothing attributes
def process_image_for_attributes(image_path):
    image = cv2.imread(image_path)
    
    # Default Values 
    top_type = "NULL"
    top_color = "Unknown"
    middle_type = "NULL"
    middle_color = "Unknown"
    bottom_type = "NULL"
    bottom_color = "Unknown"

    predictions = detect_clothing_attributes(image)
    # Retrieve predictions and filter prediction values to category (Top,Middle,Bottom)
    for prediction in predictions:
        label = prediction.get("class", "")
        confidence = prediction.get("confidence", 0.01)
        bbox = get_bounding_box(prediction)
        if confidence >= 0.02:
            if "hair" in label:
                top_type = label
            elif "shirt" in label:
                middle_type = label
                middle_color = detect_color(dominant_color_detection(image, bbox, "shirt"))
            elif "pants" in label or "skirt" in label:
                bottom_type = label
                bottom_color = detect_color(dominant_color_detection(image, bbox, "pants"))

    top_color_predictions = detect_top_color(image)
    if top_color_predictions:
        top_color_label = top_color_predictions[0].get("class", "unknown_hair")
        top_color = map_top_color(top_color_label)

    # Return values for found results
    return {
        "Image Name": os.path.basename(image_path),
        "Image Hash": os.path.splitext(os.path.basename(image_path))[0],
        "Top Type": top_type,
        "Top Color": top_color,
        "Middle Type": middle_type,
        "Middle Color": middle_color,
        "Bottom Type": bottom_type,
        "Bottom Color": bottom_color,
    }

# Saved stored values and transfer to .csv file
def save_to_csv(results):
    fieldnames = ["Image Name", "Image Hash", "Top Type", "Top Color", "Middle Type", "Middle Color",
                  "Bottom Type", "Bottom Color"]
    with open(output_file, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

def main():
    all_results = []
    for image_name in os.listdir(input_folder):
        if image_name.endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(input_folder, image_name)
            result = process_image_for_attributes(image_path)
            all_results.append(result)
    save_to_csv(all_results)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
