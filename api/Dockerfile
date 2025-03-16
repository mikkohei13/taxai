FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Install numpy with all dependencies
RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    setuptools \
    wheel

# Install PyTorch-related packages
COPY requirements-torch.txt .
RUN pip install --no-cache-dir -r requirements-torch.txt

# Install other requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"] 