document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const resultArea = document.getElementById('resultArea');
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

    function clearPreviousImageData() {
        // Clear image
        const uploadedImage = document.getElementById('uploadedImage');
        uploadedImage.src = '';
        
        // Clear result area and hide it
        resultArea.style.display = 'none';
        
        // Clear all text content fields
        document.getElementById('species-name').textContent = '';
        document.getElementById('species-confidence').textContent = '';
        document.getElementById('species-confidence-text').textContent = '';
        document.getElementById('genus-name').textContent = '';
        document.getElementById('genus-confidence').textContent = '';
        document.getElementById('genus-confidence-text').textContent = '';
        document.getElementById('notes').textContent = '';
        document.getElementById('species-name-fi').textContent = '';
        document.getElementById('occurrence-count').textContent = '';
        document.getElementById('description').textContent = '';
    }

    function handleFiles(files) {
        // Clear previous image data before processing new image
        clearPreviousImageData();
        
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
        const url = '/predict';
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
        if (!data || !data.prediction) {
            alert('Invalid response from the server');
            return;
        }
        
        const bestSpecies = data.prediction.best_species || { taxon: 'Unknown', confidence: 0 };
        const bestGenus = data.prediction.best_genus || { taxon: 'Unknown', confidence: 0 };
        const notes = data.prediction.notes || '';
        
        document.getElementById('species-name').textContent = bestSpecies.taxon;
        document.getElementById('species-confidence').textContent = bestSpecies.confidence.toFixed(3);
        document.getElementById('species-confidence-text').textContent = bestSpecies.confidence_text;
        
        document.getElementById('genus-name').textContent = bestGenus.taxon;
        document.getElementById('genus-confidence').textContent = bestGenus.confidence.toFixed(3);
        document.getElementById('genus-confidence-text').textContent = bestGenus.confidence_text;
        
        document.getElementById('notes').textContent = notes;
        
        resultArea.style.display = 'block';
        
        // When on mobile, scroll to the result section
        if (window.innerWidth <= 768) {
            document.querySelector('.section-2').scrollIntoView({ behavior: 'smooth' });
        }

        // Make additional API call to get Finnish name if we have a valid taxon
        if (bestSpecies.taxon && bestSpecies.taxon !== 'Unknown') {
            fetch(`/taxon/${bestSpecies.taxon}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(taxonData => {
                    if (taxonData) {
                        document.getElementById('species-name-fi').textContent = taxonData.fi_name;
                        document.getElementById('occurrence-count').textContent = taxonData.occurrence_count;
                        if (taxonData.has_descriptions) {
                            document.getElementById('description').innerHTML = taxonData.description;
                        } else {
                            document.getElementById('description').textContent = '-';
                        }
                    } else {
                        document.getElementById('species-name-fi').textContent = '-';
                        document.getElementById('occurrence-count').textContent = '-';
                    }
                })
                .catch(error => {
                    console.error('Error fetching Finnish name:', error);
                    document.getElementById('species-name-fi').textContent = '-';
                });
        } else {
            document.getElementById('species-name-fi').textContent = '-';
        }
    }
}); 