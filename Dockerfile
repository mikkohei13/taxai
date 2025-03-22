FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# installed on Dockerfile for caching
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu torch==2.5.1+cpu torchvision==0.20.1+cpu

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY ./app .

# Old:
#ENTRYPOINT gunicorn --chdir /app app:app -w 2 --threads 2 -b 0.0.0.0:8080

# With logs
#ENTRYPOINT ["gunicorn", "--chdir", "/app", "app:app", "-w", "2", "--threads", "2", "-b", "0.0.0.0:8080", "--log-level=debug"]

# Without logs
ENTRYPOINT ["gunicorn", "--chdir", "/app", "app:app", "-w", "2", "--threads", "2", "-b", "0.0.0.0:8080"]
