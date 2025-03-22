from flask import Flask, request, jsonify
import json

import logging
import torch
import torch.nn as nn
from torchvision import transforms
import numpy as np
from PIL import Image
import io
import base64
import os

def get_notes(genus):
    corixidae = ['Hesperocorixa', 'Callicorixa', 'Sigara', 'Cymatia', 'Arctocorisa', 'Glaenocorisa', 'Micronecta']

    if genus == 'Phytocoris':
        return "Tämä sovellus ei tunnista luotettavasti Phytocoris-suvun lajeja. Luotettava tunnistaminen edellyttää pienten yksityiskohtien tutkimista."
    elif genus in corixidae:
        return "Tämä sovellus ei tunnista luotettavasti pikkumalluaisia (Corixidae). Luotettava tunnistaminen edellyttää pienten yksityiskohtien tutkimista."
    else:
        return ""

def get_confidence_text(confidence):
    '''
    - Almost certain / Melkein varma (0.99 - 1.0)
    - Likely / Todennäköinen (0.95 - 0.99)
    - Possible / Mahdollinen (0.85 - 0.95)
    - Uncertain / Epävarma (0.7 - 0.85)
    - Just a guess / Pelkkä arvaus (0.5 - 0.7)
    - Cannot identify / En osaa tunnistaa (0 - 0.5)    
    '''
    if confidence >= 0.99:
        return "melkein varma"
    elif confidence >= 0.95:
        return "todennäköinen"
    elif confidence >= 0.85:
        return "mahdollinen"
    elif confidence >= 0.7:
        return "epävarma"
    elif confidence >= 0.5:
        return "pelkkä arvaus"
    else:
        return "en osaa tunnistaa"
    

class Predictor:
    def __init__(self, MODEL_PATH, MODEL_VERSION, SIZE_PIXELS, device=None):
        # Set device
        self.device = device if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize model
        if MODEL_VERSION == "b4":
            from torchvision.models import efficientnet_b4
            self.model = efficientnet_b4()
            print("Using EfficientNet B4")
        elif MODEL_VERSION == "b5":
            from torchvision.models import efficientnet_b5
            self.model = efficientnet_b5()
            print("Using EfficientNet B5")
        else:
            raise ValueError("Unsupported model version")

        # Load from json file
        LABEL_MAP_PATH = "./model_store/20250315_0043_species_id_min_30_efficientnet_b4_epoch_19_label_map.json"
        raw_label_map = json.load(open(LABEL_MAP_PATH))

        # Convert from label-number to number-label
        converted_label_map = {int(v): k for k, v in raw_label_map.items()}
        self.label_map = converted_label_map

        # Get number of classes from label map
        NUM_CLASSES = len(self.label_map)

        num_features = self.model.classifier[1].in_features
        self.model.classifier[1] = nn.Linear(num_features, NUM_CLASSES)
        
        # Load trained weights
        self.model.load_state_dict(torch.load(MODEL_PATH, map_location=self.device, weights_only=True))
        self.model.to(self.device)
        self.model.eval()
        
        # Define transforms
        self.transform = transforms.Compose([
            transforms.Resize((SIZE_PIXELS, SIZE_PIXELS)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        print(f"API initialized with model {MODEL_PATH} and {NUM_CLASSES} classes")


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

# Global predictor initialization
MODEL_PATH = './model_store/20250319_0038_species_id_min_30_efficientnet_b5_epoch_38.pth'
MODEL_VERSION = 'b5'
SIZE_PIXELS = 456
predictor = None

def init_predictor():
    global predictor
    if predictor is None:
        predictor = Predictor(MODEL_PATH, MODEL_VERSION, SIZE_PIXELS)

# Initialize predictor when module is loaded
init_predictor()

def generate_response(raw_result):
    predictions = raw_result['probabilities']
    
    # Create a list of (species, confidence) tuples
    prediction_list = []
    for species, confidence in predictions.items():
        prediction_list.append({
            'taxon': species.capitalize(),
            'confidence': confidence
        })
    
    # Sort the list by confidence in descending order
    prediction_list.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Take top 10 predictions
    top_species_predictions = prediction_list[:10]

    top_genus_predictions = []

    # Get top genus predictions
    for prediction in prediction_list:
        # Split species by space
        species_parts = prediction['taxon'].split(' ')
        if len(species_parts) > 1:
            genus = species_parts[0]
            # If top_genus_predictions already contains the genus, add confidence to it. If not, add new genus. Continue until there are 10 genus.
            if any(pred['taxon'] == genus for pred in top_genus_predictions):
                for pred in top_genus_predictions:
                    if pred['taxon'] == genus:
                        pred['confidence'] += prediction['confidence']
            else:
                top_genus_predictions.append({'taxon': genus, 'confidence': prediction['confidence']})
            if len(top_genus_predictions) >= 10:
                break

    # Sort top genus predictions by confidence in descending order
    top_genus_predictions.sort(key=lambda x: x['confidence'], reverse=True)

    # Calculate difference between top species and top genus
    genus_superiority = top_genus_predictions[0]['confidence'] - top_species_predictions[0]['confidence']

    # Round confidence values just before returning
    for pred in top_species_predictions:
        pred['confidence'] = round(pred['confidence'], 3)
    
    for pred in top_genus_predictions:
        pred['confidence'] = round(pred['confidence'], 3)
    
    genus_superiority = round(genus_superiority, 3)

    notes = get_notes(top_genus_predictions[0]['taxon'])

    best_species = {
        'taxon': top_species_predictions[0]['taxon'],
        'confidence': top_species_predictions[0]['confidence'],
        'confidence_text': get_confidence_text(top_species_predictions[0]['confidence'])
    }

    best_genus = {
        'taxon': top_genus_predictions[0]['taxon'],
        'confidence': top_genus_predictions[0]['confidence'],
        'confidence_text': get_confidence_text(top_genus_predictions[0]['confidence'])
    }

    prediction_response = {
        'best_species': best_species,
        'best_genus': best_genus,
        'top_species': top_species_predictions,
        'top_genus': top_genus_predictions,
        'genus_superiority': genus_superiority,
        'notes': notes
    }

    return {
        'prediction': prediction_response
    }


def main(data):
    try:
        if not data or 'image' not in data:
            return jsonify({"error": "No image data provided"}), 400

        # Decode base64 image
        image_bytes = base64.b64decode(data['image'])
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Use global predictor instance
        raw_result = predictor.predict(image)

        # Finalize API response
        api_response = generate_response(raw_result)
        return api_response

    except Exception as e:
        return jsonify({"error": str(e)}), 500
