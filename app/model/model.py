import torch
import torch.nn as nn
import json
import os

class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.linear = nn.Linear(10, 1)
    
    def forward(self, x):
        return self.linear(x)

def get_model():
    model = SimpleModel()
    # Load the saved model weights
    model_path = os.path.join(os.path.dirname(__file__), "model_store/20250315_0043_species_id_min_30_efficientnet_b4_epoch_19.pth")
    model.load_state_dict(torch.load(model_path))
    model.eval()  # Set to evaluation mode
    return model

def load_label_map():
    label_map_path = os.path.join(os.path.dirname(__file__), "model_store/20250315_0043_species_id_min_30_efficientnet_b4_epoch_19_label_map.json")
    with open(label_map_path, 'r') as f:
        class_to_idx = json.load(f)
        # Create reverse mapping (index to class name)
        idx_to_class = {v: k for k, v in class_to_idx.items()}
    return idx_to_class

# For TorchServe handler
def handle(data, context):
    if not data:
        return None
    
    # Convert input data to tensor
    input_data = torch.tensor(data[0].get("data") or data[0].get("body")).float()
    
    # Get model and label map
    model = get_model()
    idx_to_class = load_label_map()
    
    # Make prediction
    with torch.no_grad():
        prediction = model(input_data)
        
    # Convert prediction to label using the label map
    pred_value = prediction.item()
    pred_idx = round(pred_value)  # or int(pred_value) depending on your model's output
    pred_label = idx_to_class.get(pred_idx, "Unknown")
    
    return [{"prediction": pred_value, "label": pred_label}] 