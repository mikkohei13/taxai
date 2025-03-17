FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# First install base dependencies that others need
RUN pip install --no-cache-dir \
    setuptools \
    wheel \
    numpy==1.26.4

# Remove numpy from requirements.txt if present
COPY requirements.txt .
RUN sed -i '/numpy/d' requirements.txt

# Install other base requirements first
RUN pip install --no-cache-dir -r requirements.txt

# Now install PyTorch-related packages
COPY requirements-torch.txt .
RUN pip install --no-cache-dir -r requirements-torch.txt

# Copy application files
COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"] 