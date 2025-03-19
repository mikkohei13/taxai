
import requests
import base64
import os
import time

# Process specific image
image_directory = "./images_test1"

API_HOST = "taxai-api-1"

extensions = [".jpg", ".jpeg", ".JPG", ".JPEG"]

# Get list of images files from image directory
image_files = [f for f in os.listdir(image_directory) if any(f.endswith(ext) for ext in extensions)]
number_of_images = len(image_files)

# Start timer
start_time = time.time()

for image_file in image_files:
    with open(os.path.join(image_directory, image_file), "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode('utf-8')

        url = f'http://{API_HOST}:5000/predict'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.post(url, json={'image': img_data}, headers=headers)
        result = response.json()

        print("--------------------------------")
        print(f"Image: {image_file}")
        print(f"Prediction: {result}")

# End timer
end_time = time.time()

# Calculate time taken
time_taken = end_time - start_time

# Print time taken
print("--------------------------------")
print(f"Time taken: {time_taken} seconds")
print(f"Number of images: {number_of_images}")
print(f"Time per image: {time_taken / number_of_images} seconds")