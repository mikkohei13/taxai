import torch
import torch.nn as nn

class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.linear = nn.Linear(10, 1)
    
    def forward(self, x):
        return self.linear(x)

def get_model():
    model = SimpleModel()
    return model

# For TorchServe handler
def handle(data, context):
    if not data:
        return None
    
    # Convert input data to tensor
    input_data = torch.tensor(data[0].get("data") or data[0].get("body")).float()
    
    # Get model
    model = get_model()
    
    # Make prediction
    with torch.no_grad():
        prediction = model(input_data)
    
    return [prediction.tolist()] 