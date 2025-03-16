from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TORCHSERVE_URL = os.getenv('TORCHSERVE_URL', 'http://localhost:8080')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data or 'input' not in data:
            return jsonify({"error": "No input data provided"}), 400

        # Forward the request to TorchServe
        torchserve_response = requests.post(
            f"{TORCHSERVE_URL}/predictions/model",
            json={"data": data['input']}
        )
        
        prediction = torchserve_response.json()
        return jsonify({"prediction": prediction})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 