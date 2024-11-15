// Store the selected tiles for both current and proposed views
let keyBuffer = "";

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

// Select a tile and highlight it
function selectTile(tileIndices) {
    tileIndices.forEach(tileIndex => {
        const previewTile = document.getElementById(`preview-tile-${tileIndex}`);

        // Check if tile is already selected
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

function handleKeyPress(event) {

    if (event.key.length === 1 || event.key === 'Enter') { // Add single characters and Enter key
        keyBuffer += event.key;
    }

    // Map keypress to tile index (A1 to A14)
    const keyToTileGroupMap = {
        '0': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],  // All tiles
        '1A': [1, 2, 3, 4],    // Tiles A1 to A4
        '1B': [6, 7, 8, 9],    // Tiles A6 to A9
        '1C': [11, 12, 13, 14], // Tiles A11 to A14
        '1D': [1, 2, 3, 4, 5, 6, 7], // Tiles A1 to A7
        '1E': [8, 9, 10, 11, 12, 13, 14] // Tiles A8 to A14
    };

    if (keyToTileGroupMap[keyBuffer]) {
        const tileIndices = keyToTileGroupMap[keyBuffer];
        selectTile(tileIndices);
        
        // Clear the buffer after a match
        keyBuffer = "";
    }

    // Apply the color changes when Enter is pressed
    if (event.key === 'Enter') {
        applyColors();
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
