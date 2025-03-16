FROM python:3.9-slim

WORKDIR /app

# Install PyTorch-related packages first
COPY requirements-torch.txt .
RUN pip install --no-cache-dir -r requirements-torch.txt

# Install other requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"] 