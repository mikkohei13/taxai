
<img align="right" src="./app/static/logo_medium.png" alt="alt text" style="margin-left: 1em; margin-top: -2em;"/>

Taxai is a web app that helps to identify insect species from images using machine learning. Built with Python and PyTorch, it runs well on CPU and can be deployed either locally with Docker Compose or on Google Cloud Run. See background information about making the app and its underlying model: https://www.biomi.org/2025/03/25/insect-identification-with-machine-learning/

First public version released 2025-03-22.


# Setup (untested)

- Clone this repository.
- Create a directory for the model:

    mkdir ./app/model_store

- Put model to model_store directory. 
- Add model name and settings to /.api/app.py
- Start with:

    docker compose up --build; docker compose down;

App will be available at http://localhost:8080/

API health check endpoint will be available at http://localhost:8080/health

# Deploy to Google Cloud Run using Artifact Repository

Build new version:

    gcloud builds submit --tag europe-north1-docker.pkg.dev/havistin/taxai-repo-north/taxai .

Deploy new version. Note that the app needs >1GB memory if the model is large. Having less memory might result in random startup errors.

    gcloud run deploy taxai \
    --project=havistin \
    --image=europe-north1-docker.pkg.dev/havistin/taxai-repo-north/taxai \
    --max-instances=1 \
    --concurrency=5 \
    --memory=2048Mi \
    --timeout=40 \
    --region=europe-north1

Adjust options if needed:

    gcloud run services update taxai --min-instances=1

# Usage

When calling the API you must provide an image.

    json_request = {
        'image': img_data,
    }

# Notes

Issue when building this:
- Tried to install full pytorch with GPU, which was very slow. Use CPU version instead.
-  Compatibility issues with CPU library versions.
- Called API from within Docker with localhost, which doesn't work. Use container name instead.
- If Numpy version is too recent, PyTorch says Numpy is not available. Need to use version 1.26.4.

Possible terms:

- Almost certain / Melkein varma (0.99 - 1.0)
- Likely / Todennäköinen (0.95 - 0.99)
- Possible / Mahdollinen (0.85 - 0.95)
- Uncertain / Epävarma (0.7 - 0.85)
- Just a guess / Pelkkä arvaus (0.5 - 0.7)
- Cannot identify / En osaa tunnistaa (0 - 0.5)

# Todo: Cleanup

.dockerignore
model
.env

