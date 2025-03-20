# Template for a frontend web app
from flask import Flask, send_from_directory, send_file, render_template
import os

app = Flask(__name__, static_folder='static')

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    response = send_from_directory('static', filename)
    # Add cache control headers to prevent caching during development
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)