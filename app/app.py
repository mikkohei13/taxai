from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

import predict
import taxon

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/favicon.ico')
def serve_favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

@app.route('/static/<path:filename>')
def serve_static(filename):
    response = send_from_directory('static', filename)
    # Add cache control headers to prevent caching during development
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/taxon/<string:taxon_name>', methods=['GET'])
def taxon_endpoint(taxon_name):
    api_response = taxon.main(taxon_name)
    return jsonify(api_response)

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    data = request.get_json()
    api_response = predict.main(data)
    return jsonify(api_response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 