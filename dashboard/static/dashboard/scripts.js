// Store the selected tiles for both current and proposed views
let keyBuffer = "";
let firstParam = "";
let secondParam = null;

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
}

// Apply the color changes from the proposed view to the current view
function applyColors() {
    for (let i = 1; i <= 14; i++) {
        const previewTile = document.getElementById(`preview-tile-${i}`);
        const currentTile = document.getElementById(`current-tile-${i}`);

        // Apply the color from the proposed tile to the current tile
        currentTile.style.backgroundColor = previewTile.style.backgroundColor;
    }
}

function sendTriggerRequest(tile, payload) {

    fetch('/trigger-action/', {  // This URL should match the Django view URL
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()  // If CSRF protection is enabled
        },
        body: JSON.stringify({
            tile: tile,
            payload: payload
        })
    })
    .then(response => response.json())
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
        const tileIndices = keyToTileGroupMap[keyBuffer];
        selectTile(tileIndices);
        // Display first parameter on the UI (can be adapted for your UI framework)
        document.getElementById('first-param').textContent = `First Parameter: ${firstParam}`;
        console.log("firstParam: ", firstParam);
        keyBuffer = "";
    }

    const validSecondParams = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24'];
    // const secondParamInt = parseInt(keyBuffer, 10);

    if (validSecondParams.includes(keyBuffer)) {
        secondParam = keyBuffer;
        // Display second parameter on the UI (can be adapted for your UI framework)
        document.getElementById('second-param').textContent = `Second Parameter: ${secondParam}`;
        console.log("secondParam: ", secondParam);
        keyBuffer = "";
    }

    // Apply the color changes when Enter is pressed
    if (event.key === 'Enter') {
        applyColors();
        sendTriggerRequest(firstParam, secondParam); // Send selected tiles to Django
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
