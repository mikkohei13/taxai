
# Setup

    docker compose up --build; docker compose down;

The API will be available at http://localhost:5000/health

# Notes

Issue when building this:
- Tried to install full pytorch with GPU, which was very slow. Use CPU version instead.
-  Compatibility issues with CPU library versions.
- Called API from within Docker with localhost, which doesn't work. Use container name instead.
- Numpy not installed automatically, even though tensor transformation requires it.