// Store the selected tiles for both current and proposed views
let keyBuffer = "";
let firstParam = localStorage.getItem("firstParam") || "";
let secondParam = localStorage.getItem("secondParam") || null;

let selectedTiles = {
    current: null,
    preview: new Set()
};

// Update the military time every second
function updateTime() {
    const timeDisplay = document.getElementById("time-display");
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    timeDisplay.innerText = `${hours}:${minutes}:${seconds}`;
}

// Call updateTime every 1000 milliseconds (1 second)
setInterval(updateTime, 1000);

function saveSelectedTiles() {
    const selectedTilesArray = Array.from(selectedTiles.preview); // Convert the Set to an array
    localStorage.setItem('selectedTiles', JSON.stringify(selectedTilesArray));
}

function selectTile(tileIndices) {
    tileIndices.forEach(tileIndex => {
        const previewTile = document.getElementById(`preview-tile-${tileIndex}`);
        if (selectedTiles.preview.has(tileIndex)) {
            previewTile.style.backgroundColor = ""; // Reset color if already selected
            selectedTiles.preview.delete(tileIndex); // Remove tile from the selected set
        } else {
            previewTile.style.backgroundColor = "#ffeb3b"; // Yellow for selected
            selectedTiles.preview.add(tileIndex); // Add tile to the selected set
        }
    });

    saveSelectedTiles();
}

function loadSelectedTiles() {
    const savedTiles = JSON.parse(localStorage.getItem('selectedTiles')) || [];
    savedTiles.forEach(tileIndex => {
        const previewTile = document.getElementById(`preview-tile-${tileIndex}`);
        if (previewTile) {
            previewTile.style.backgroundColor = "#ffeb3b"; // Restore color
            selectedTiles.preview.add(tileIndex); // Restore the set of selected tiles
        }
    });
}

// Call this function when the page loads
window.onload = function() {
    loadSelectedTiles(); // Load selected tiles on page load
    updateTime(); // Initialize the time
    document.getElementById('first-param').textContent = `Zone: ${firstParam}`;
    document.getElementById('second-param').textContent = `Activation: ${secondParam}`;
    const tileIndices = Array.from({ length: 14 }, (_, index) => index + 1);
    const fetchPromises = tileIndices.map(tileIndex => {
        return fetch(`/device-output/${tileIndex}/`) // Adjust endpoint as necessary
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to fetch image for tile ${tileIndex}`);
                }
                return response.json(); // Assuming the response is JSON containing a data URL
            })
            .then(data => {
                const tileElement = document.getElementById(`current-tile-${tileIndex}`);
                if (tileElement && data.src && data.src.startsWith("data:image/")) {
                    // Apply the image as the tile background
                    tileElement.style.backgroundImage = `url(${data.src})`;
                    tileElement.style.backgroundSize = "cover";
                    tileElement.style.backgroundPosition = "center";
                } else {
                    console.error(`Invalid image data for tile ${tileIndex}`);
                }
            })
            .catch(error => console.error(`Error fetching image for tile ${tileIndex}:`, error));
    });

    // Wait for all fetch requests to complete
    Promise.all(fetchPromises)
        .then(() => {
            console.log("All tiles loaded successfully");
        })
        .catch(error => {
            console.error("Error loading some tiles:", error);
        });
};

function applyColors() {
    for (let i = 1; i <= 14; i++) {
        const previewTile = document.getElementById(`preview-tile-${i}`);
        const currentTile = document.getElementById(`current-tile-${i}`);

        currentTile.style.backgroundColor = previewTile.style.backgroundColor;
    }
}

function sendTriggerRequest(tile, payload) {

    const keyToTileGroupMap = {
        '0': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],  // All tiles
        'a': [1, 2, 3, 4],    // Tiles A1 to A4
        'b': [6, 7, 8, 9],    // Tiles A6 to A9
        'c': [11, 12, 13, 14], // Tiles A11 to A14
        'd': [1, 2, 3, 4, 5, 6, 7], // Tiles A1 to A7
        'e': [8, 9, 10, 11, 12, 13, 14] // Tiles A8 to A14
    };

    fetch('/trigger-action/', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            tile: tile, // zone: 0, a, b, c, d, e
            payload: payload // activation: 1-24
        })
    })
    .then(response => response.json())

    // Call get request over here, for loop in keyToTileGroupMap[tile], recieve image and update the box
    // 
    .then(() => {
        // Iterate through tile indices and fetch images
        const tileIndices = keyToTileGroupMap[tile] || [];
        const fetchPromises = tileIndices.map(tileIndex => {
            fetch(`/device-output/${tileIndex}/`) // Adjust endpoint as necessary
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Failed to fetch image for tile ${tileIndex}`);
                    }
                    return response.json(); // Assuming the response is JSON containing a data URL
                })
                .then(data => {
                    const tileElement = document.getElementById(`current-tile-${tileIndex}`);
                    if (tileElement && data.src && data.src.startsWith("data:image/")) {
                        // Apply the image as the tile background
                        tileElement.style.backgroundImage = `url(${data.src})`;
                        tileElement.style.backgroundSize = "cover";
                        tileElement.style.backgroundPosition = "center";
                    } else {
                        console.error(`Invalid image data for tile ${tileIndex}`);
                    }
                })
                .catch(error => console.error(`Error fetching image for tile ${tileIndex}:`, error));
        });

        return Promise.all(fetchPromises);
    })
    .catch(error => console.error("Error with trigger action request:", error));

}

// CSRF token helper
function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return null;
}

function handleKeyPress(event) {

    if (event.key.length === 1 || event.key === 'Enter') { // Add single characters and Enter key
        keyBuffer += event.key;
    }

    // Map keypress to tile index (A1 to A14)
    const keyToTileGroupMap = {
        '0': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],  // All tiles
        'a': [1, 2, 3, 4],    // Tiles A1 to A4
        'b': [6, 7, 8, 9],    // Tiles A6 to A9
        'c': [11, 12, 13, 14], // Tiles A11 to A14
        'd': [1, 2, 3, 4, 5, 6, 7], // Tiles A1 to A7
        'e': [8, 9, 10, 11, 12, 13, 14] // Tiles A8 to A14
    };
    console.log(keyBuffer);
    if (['0', 'a', 'b', 'c', 'd', 'e'].includes(keyBuffer)) {
        firstParam = keyBuffer;
        localStorage.setItem("firstParam", firstParam);
        const tileIndices = keyToTileGroupMap[keyBuffer];
        selectTile(tileIndices);
        // Display first parameter on the UI (can be adapted for your UI framework)
        document.getElementById('first-param').textContent = `First Parameter: ${firstParam}`;
        console.log("firstParam: ", firstParam);
        keyBuffer = "";
    }

    // Handle second parameter
    const validSecondParams = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24'];
    
    if (validSecondParams.includes(keyBuffer)) {
        secondParam = keyBuffer;
        localStorage.setItem("secondParam", secondParam);
        document.getElementById('second-param').textContent = `Second Parameter: ${secondParam}`;
        console.log("secondParam: ", secondParam);
    }

    if (event.key === 'z') {
        secondParam = ''; // Clear the second parameter
        keyBuffer = "";
        document.getElementById('second-param').textContent = `Second Parameter: ${secondParam}`; // Update the UI
        console.log("secondParam has been cleared.");
    }

    // Apply the color changes when Enter is pressed
    if (event.key === 'Enter') {
        if (firstParam && secondParam) {
            console.log("first Prameter enterered: ", firstParam)
            console.log("second Paramter entered: ", secondParam)
            applyColors();
            sendTriggerRequest(firstParam, secondParam); // Send selected tiles to Django
        }
        keyBuffer = ""; // Clear buffer after Enter
    }
    
    // Limit buffer length to prevent excessive accumulation
    if (keyBuffer.length > 2) {
        keyBuffer = keyBuffer.slice(-2); // Keep only last 2 characters
    }
}

// Listen for key press events
document.addEventListener('keydown', handleKeyPress);

// Initialize the time when the page loads
updateTime();
