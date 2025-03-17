# Script that calls http://localhost:5000/predict API with images in the ./images directory.

import os
import requests
from pathlib import Path
import base64
import socket

def test_prediction(image_path):
    # Read image as binary data
    with open(image_path, 'rb') as img_file:
        img_data = base64.b64encode(img_file.read()).decode('utf-8')
    
    print(f"Running from hostname: {socket.gethostname()}")
    print(f"Image data size (base64): {len(img_data)} bytes")
    
    # Try both the container name and service name
    api_hosts = ['taxai-api-1', 'api']
    
    for API_HOST in api_hosts:
        print(f"\nTrying to connect to API at {API_HOST}...")
        
        # First check if API is available
        health_url = f'http://{API_HOST}:5000/health'
        torchserve_health_url = f'http://{API_HOST}:5000/torchserve-health'
        
        try:
            # Check API health
            print(f"Attempting to connect to {health_url}")
            health_response = requests.get(health_url)
            print(f"API health check status: {health_response.status_code}")
            print(f"API health check response: {health_response.json()}")
            
            # Check TorchServe health
            print(f"Attempting to connect to {torchserve_health_url}")
            torchserve_response = requests.get(torchserve_health_url)
            print(f"TorchServe health check status: {torchserve_response.status_code}")
            print(f"TorchServe health check response: {torchserve_response.json()}")
            
            # If we get here, we found a working host
            break
            
        except requests.exceptions.ConnectionError as e:
            print(f"Error: Could not connect to API server at {API_HOST}:5000")
            print(f"Error details: {str(e)}")
            continue
    else:
        print("Failed to connect to API using any hostname")
        return
    
    # Send request to API
    url = f'http://{API_HOST}:5000/predict'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    print(f"\nSending prediction request to {url}")
    print(f"Request headers: {headers}")
    
    try:
        response = requests.post(url, json={'image': img_data}, headers=headers)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Raw response content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nImage: {image_path}")
            print(f"Prediction: {result}")
        else:
            print(f"\nError for {image_path}")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError as e:
        print(f"\nConnection error: {e}")
        print("Is the API server running? Is TorchServe running on port 8080?")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        print(f"Error type: {type(e)}")

def main():
    # Get the directory containing test images
    image_dir = Path('./images')
    
    # Ensure the images directory exists
    if not image_dir.exists():
        print("Error: ./images directory not found")
        return
    
    # Process specific image
    image_file = "./images/Adelphocoris seticornis SMALL.jpg"
    test_prediction(image_file)

if __name__ == '__main__':
    main()