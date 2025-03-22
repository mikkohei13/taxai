
import requests
import base64
import os
import time
import json
# Process specific image
image_path = "./static/test_nysius.jpg"

API_HOST = "taxai-api-1"

with open(image_path, "rb") as img_file:
    img_data = base64.b64encode(img_file.read()).decode('utf-8')

    url = f'http://{API_HOST}:8080/predict'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    json_request = {
        'image': img_data
    }
    response = requests.post(url, json=json_request, headers=headers)
    result = response.json()

    pretty_json = json.dumps(result, indent=2)

    print("--------------------------------")
    print(f"Image: {image_path}")
    print(f"Response: {pretty_json}")

