from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import torch
import torchvision.transforms as transforms
from PIL import Image
import io
import base64
import logging
import numpy as np

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = app.logger

TORCHSERVE_URL = os.getenv('TORCHSERVE_URL', 'http://localhost:8080')
logger.info(f"TorchServe URL configured as: {TORCHSERVE_URL}")

def preprocess_image(image_data):
    logger.debug("Starting image preprocessing")
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        logger.debug(f"Image loaded successfully, size: {image.size}")
        
        # Standard EfficientNet-b4 preprocessing
        transform = transforms.Compose([
            transforms.Resize(380),  # EfficientNet-b4 default size
            transforms.CenterCrop(380),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Transform image
        image_tensor = transform(image)
        logger.debug(f"Image tensor shape: {image_tensor.shape}, type: {type(image_tensor)}")
        
        # Convert to numpy with detailed logging
        logger.debug("Converting tensor to numpy array...")
        numpy_array = image_tensor.cpu().detach().numpy()
        logger.debug(f"Numpy array shape: {numpy_array.shape}, type: {type(numpy_array)}")
        
        # Convert to list
        result = numpy_array.tolist()
        logger.debug(f"Final list type: {type(result)}, length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"Error in image preprocessing: {str(e)}", exc_info=True)
        raise

@app.before_request
def log_request_info():
    logger.debug("=== New Request ===")
    logger.debug(f"Method: {request.method}")
    logger.debug(f"Path: {request.path}")
    logger.debug(f"Headers: {dict(request.headers)}")
    if request.is_json:
        logger.debug(f"JSON keys received: {request.json.keys() if request.json else 'No JSON data'}")

@app.route('/health', methods=['GET'])
def health_check():
    logger.info("Health check endpoint called")
    return jsonify({"status": "healthy"})

@app.route('/predict', methods=['POST'])
def predict():
    logger.info("Predict endpoint called")
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            logger.error("No image data provided in request")
            return jsonify({"error": "No image data provided"}), 400

        logger.debug("Image data received, starting preprocessing")
        processed_data = preprocess_image(data['image'])
        logger.debug(f"Processed data type: {type(processed_data)}")

        # Forward the request to TorchServe
        request_data = {"data": processed_data}
        logger.debug(f"Sending request to TorchServe at {TORCHSERVE_URL} with data shape: {len(processed_data)}x{len(processed_data[0]) if processed_data else 0}")
        torchserve_response = requests.post(
            f"{TORCHSERVE_URL}/predictions/model",
            json=request_data
        )
        
        logger.debug(f"TorchServe response status: {torchserve_response.status_code}")
        logger.debug(f"TorchServe response content: {torchserve_response.text}")
        prediction = torchserve_response.json()
        logger.info("Prediction completed successfully")
        return jsonify({"prediction": prediction})

    except Exception as e:
        logger.error(f"Error in prediction endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/torchserve-health', methods=['GET'])
def torchserve_health():
    logger.info("TorchServe health check endpoint called")
    try:
        # Check basic health
        ping_response = requests.get(f"{TORCHSERVE_URL}/ping")
        logger.debug(f"TorchServe ping response: {ping_response.text}")
        
        # Check model status
        models_response = requests.get(f"{TORCHSERVE_URL}/models")
        logger.debug(f"TorchServe models response: {models_response.text}")
        
        if ping_response.status_code == 200:
            response_data = {
                "status": "TorchServe is healthy",
                "ping_response": ping_response.text,
                "models": models_response.json() if models_response.status_code == 200 else "Unable to get model status"
            }
            logger.info("TorchServe health check successful")
            return jsonify(response_data)
        else:
            logger.error(f"TorchServe health check failed with status {ping_response.status_code}")
            return jsonify({
                "status": "TorchServe is not healthy",
                "code": ping_response.status_code,
                "ping_response": ping_response.text,
                "models_response": models_response.text if models_response.status_code == 200 else "Unable to get model status"
            }), 500
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Failed to connect to TorchServe: {str(e)}")
        return jsonify({
            "status": "Cannot connect to TorchServe",
            "url": TORCHSERVE_URL
        }), 500

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True) 