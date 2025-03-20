document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const resultArea = document.getElementById('resultArea');
    const speciesName = document.getElementById('speciesName');
    const confidence = document.getElementById('confidence');
    const spinner = document.getElementById('spinner');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when dragging over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    // Handle file input change
    fileInput.addEventListener('change', handleFileSelect, false);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                processImage(file);
            } else {
                alert('Please select an image file.');
            }
        }
    }

    function processImage(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const base64Image = e.target.result.split(',')[1];
            // Display the image
            const uploadedImage = document.getElementById('uploadedImage');
            uploadedImage.src = e.target.result;
            sendToAPI(base64Image);
        };
        reader.readAsDataURL(file);
    }

    function sendToAPI(base64Image) {
        const url = 'http://localhost:5000/predict';
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        // Show spinner and hide upload content
        spinner.style.display = 'block';
        document.querySelector('.upload-content').style.display = 'none';

        fetch(url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ image: base64Image })
        })
        .then(response => response.json())
        .then(data => {
            displayResult(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error processing image. Please try again.');
        })
        .finally(() => {
            // Hide spinner and show upload content
            spinner.style.display = 'none';
            document.querySelector('.upload-content').style.display = 'flex';
        });
    }

    function displayResult(data) {
        const bestSpecies = data.prediction.best_species;
        speciesName.textContent = bestSpecies.species;
        confidence.textContent = (bestSpecies.confidence).toFixed(3);
        resultArea.style.display = 'block';
    }
}); 