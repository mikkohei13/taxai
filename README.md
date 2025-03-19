
# Setup

    mkdir ./api/model_store

- Put model to model_store directory. 
- Add model name and settings to /.api/app.py

    docker compose up --build; docker compose down;

App will be available at http://localhost:3000/

API will be available at http://localhost:5000/health

# Notes

Issue when building this:
- Tried to install full pytorch with GPU, which was very slow. Use CPU version instead.
-  Compatibility issues with CPU library versions.
- Called API from within Docker with localhost, which doesn't work. Use container name instead.
- If Numpy version is too recent, PyTorch says Numpy is not available. Need to use version 1.26.4.
