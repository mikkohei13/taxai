from flask import Flask, request, jsonify
import torch
import torch.nn as nn
from torchvision import transforms
import numpy as np
from PIL import Image
import io
import base64
import os
#from dotenv import load_dotenv
import json

class Predictor:
    def __init__(self, model_path, model_version, size_pixels, device=None):
        # Set device
        self.device = device if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize model
        if model_version == "b4":
            from torchvision.models import efficientnet_b4
            self.model = efficientnet_b4()
        else:
            raise ValueError("Unsupported model version")

        # Define label mapping
        '''
        It should be like this:
        self.label_map = {
            0: "adult",
            1: "larva",
            2: "pupa",
            3: "egg",
            4: "indirect",
            5: "habitat"
        }
        '''

        # Load from json file
        raw_label_map = json.load(open('./model_store/20250315_0043_species_id_min_30_efficientnet_b4_epoch_19_label_map.json'))
        # Convert from label-number to number-label
        converted_label_map = {int(v): k for k, v in raw_label_map.items()}
        print("LABEL MAP: ", converted_label_map)
        self.label_map = converted_label_map

        # Get number of classes from label map
        num_classes = len(self.label_map)

        num_features = self.model.classifier[1].in_features
        self.model.classifier[1] = nn.Linear(num_features, num_classes)
        
        # Load trained weights
        self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
        self.model.to(self.device)
        self.model.eval()
        
        # Define transforms
        self.transform = transforms.Compose([
            transforms.Resize((size_pixels, size_pixels)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])


    def predict(self, image):
        # Transform and predict
        image = self.transform(image)
        image = image.unsqueeze(0)  # Add batch dimension
        
        # Move to device and predict
        image = image.to(self.device)
        
        with torch.no_grad():
            outputs = self.model(image)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()
        
        return {
            'class': self.label_map[predicted_class],
            'confidence': confidence,
            'probabilities': {self.label_map[i]: prob.item() 
                            for i, prob in enumerate(probabilities[0])}
        }

app = Flask(__name__)

# Initialize predictor
MODEL_PATH = os.getenv('MODEL_PATH', './model_store/20250315_0043_species_id_min_30_efficientnet_b4_epoch_19.pth')
MODEL_VERSION = os.getenv('MODEL_VERSION', 'b4')
SIZE_PIXELS = int(os.getenv('SIZE_PIXELS', '380'))

predictor = Predictor(MODEL_PATH, MODEL_VERSION, SIZE_PIXELS)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "No image data provided"}), 400

        # Decode base64 image
        image_bytes = base64.b64decode(data['image'])
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Get prediction
        result = predictor.predict(image)
        
        return jsonify({"prediction": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 