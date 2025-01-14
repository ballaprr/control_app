// Store the selected tiles for both current and proposed views
let keyBuffer = "";
let firstParam = localStorage.getItem("firstParam") || "";
let secondParam = localStorage.getItem("secondParam") || null;
let fgSequence = false;

let selectedTiles = {
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
    const allTiles = document.querySelectorAll('[id^="preview-tile-"]');
    const secondParam = localStorage.getItem("secondParam");
    const legendData = JSON.parse(localStorage.getItem('legendData')) || [];
    // Unhighlight all tiles
    allTiles.forEach(tile => {
        tile.style.backgroundColor = ""; // Reset background color
        tile.style.backgroundImage = '';
    });

    // Clear the currently selected tiles set
    selectedTiles.preview.clear();

    const filteredLegendData = legendData.filter(item => item.trigger === secondParam);
    console.log(filteredLegendData)
    // Display images for selected tiles
    /*
    tileIndices.forEach(tileIndex => {
        const previewTile = document.getElementById(`preview-tile-${tileIndex}`);
        if (previewTile) {
            previewTile.style.backgroundColor = "#ffeb3b"; // Highlight with yellow
            selectedTiles.preview.add(tileIndex); // Add to the selected set
        } else {
            console.warn(`Tile with ID preview-tile-${tileIndex} not found.`);
        }
    });
    */
   console.log("tileIndices: ", tileIndices);
   console.log("filteredLegendData: ", filteredLegendData);
    tileIndices.forEach((tileIndex, idx) => {
        // Use index + 1 to map to tile indices if needed
        // const tileIndex = savedTiles[index] || (index + 1); // Fallback to index + 1 if savedTiles doesn't have the index
        const previewTile = document.getElementById(`preview-tile-${tileIndex}`);

        if (previewTile) {
            // Use the current index to find the corresponding thumbnail in filteredLegendData
            const legendItem = filteredLegendData[idx % filteredLegendData.length]; // Cycle through legend data if more tiles than data
            console.log(legendItem)

            
            if (legendItem && legendItem.thumb) {
                previewTile.style.backgroundImage = `url(${legendItem.thumb})`;
                previewTile.style.backgroundSize = 'cover';
                previewTile.style.backgroundPosition = 'center';
            } else {
                previewTile.style.backgroundColor = '#ffeb3b'; // Fallback color
                previewTile.style.backgroundImage = '';
                console.log(`No thumbnail available for trigger: ${legendItem?.trigger}`);
            }

            // Optionally, store the tile index as selected
            selectedTiles.preview.add(tileIndex);
        } else {
            console.log(`Tile element with ID preview-tile-${tileIndex} not found.`);
        }
    });

    saveSelectedTiles();
}

// set selected tiles for according activation image
function loadSelectedTiles() {
    const savedTiles = JSON.parse(localStorage.getItem('selectedTiles')) || [];
    const legendData = JSON.parse(localStorage.getItem('legendData')) || [];
    const secondParam = localStorage.getItem("secondParam");
    console.log("savedTiles: ", savedTiles);

    const filteredLegendData = legendData.filter(item => item.trigger === secondParam);
    /*
    savedTiles.forEach(tileIndex => {
        const previewTile = document.getElementById(`preview-tile-${tileIndex}`);
        if (previewTile) {
            previewTile.style.backgroundColor = "#ffeb3b"; // Restore color
            selectedTiles.preview.add(tileIndex); // Restore the set of selected tiles
        }
    });
    */
   console.log("filteredLegendData: ", filteredLegendData);
    savedTiles.forEach((tileIndex, idx) => {
        // Use index + 1 to map to tile indices if needed
        // const tileIndex = savedTiles[index] || (index + 1); // Fallback to index + 1 if savedTiles doesn't have the index
        const previewTile = document.getElementById(`preview-tile-${tileIndex}`);

        if (previewTile) {
            // Use the current index to find the corresponding thumbnail in filteredLegendData
            const legendItem = filteredLegendData[idx % filteredLegendData.length]; // Cycle through legend data if more tiles than data
            console.log(legendItem)
            if (legendItem && legendItem.thumb) {
                previewTile.style.backgroundImage = `url(${legendItem.thumb})`;
                previewTile.style.backgroundSize = 'cover';
                previewTile.style.backgroundPosition = 'center';
            } else {
                previewTile.style.backgroundColor = '#ffeb3b'; // Fallback color
                console.log(`No thumbnail available for trigger: ${legendItem?.trigger}`);
            }

            // Optionally, store the tile index as selected
            selectedTiles.preview.add(tileIndex);
        } else {
            console.log(`Tile element with ID preview-tile-${tileIndex} not found.`);
        }
    });
}

// Call this function when the page loads
// save legend data to local storage
window.onload = function() {
    loadSelectedTiles(); // Load selected tiles on page load
    updateTime(); // Initialize the time
    loadLegendTableFromStorage(); // Load legend data from local storage
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

function formatDataAndDisplay(data) {
    const units = {
        "boot_uptime": "seconds",
        "cpu idle": "%",
        "disk available": "MB",
        "disk used": "MB",
        "fps": "frames/second",
        "info beamer uptime": "seconds",
        "network data received": "bytes",
        "network data sent": "bytes",
        "PI CPU temperature": "°C",
        "video hz": "Hz",
        "video resolution": "",
        "gpu": "KB",
        "gpu_used": "KB",
        "gpu arm": "KB",
        "network ip address": "",
        "network mac address": "",
        "hwids eth0": "",
        "hwids wlan0": "",
        "revision": "",
        "info beamer version": "",
    };

    const container = document.getElementById("device-response");
    container.innerHTML = ""; // Clear any existing content

    // Create a table element
    const table = document.createElement("table");
    table.style.width = "100%";
    table.style.borderCollapse = "collapse";
    table.classList.add('device-table');

    // Create table header
    const headerRow = document.createElement("tr");
    const keyHeader = document.createElement("th");
    keyHeader.textContent = "Key";
    const valueHeader = document.createElement("th");
    valueHeader.textContent = "Value";
    headerRow.appendChild(keyHeader);
    headerRow.appendChild(valueHeader);
    table.appendChild(headerRow);

    // Add data rows
    for (const [key, value] of Object.entries(data)) {
        const unit = units[key] || ""; // Get the unit for the key or default to empty
        const formattedValue = `${value} ${unit}`.trim();

        const row = document.createElement("tr");

        const keyCell = document.createElement("td");
        keyCell.textContent = key;
        keyCell.style.border = "1px solid #ccc";
        keyCell.style.padding = "8px";

        const valueCell = document.createElement("td");
        valueCell.textContent = formattedValue;
        valueCell.style.border = "1px solid #ccc";
        valueCell.style.padding = "8px";

        row.appendChild(keyCell);
        row.appendChild(valueCell);
        table.appendChild(row);
    }

    // Append the table to the container
    container.appendChild(table);
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
    if (['0', 'a', 'b', 'c', 'd', 'e'].includes(keyBuffer)) {
        firstParam = keyBuffer;
        localStorage.setItem("firstParam", firstParam);
        const tileIndices = keyToTileGroupMap[keyBuffer];
        selectTile(tileIndices);
        // Display first parameter on the UI (can be adapted for your UI framework)
        document.getElementById('first-param').textContent = `Zone: ${firstParam}`;
        console.log("firstParam: ", firstParam);
        keyBuffer = "";
    }

    // Handle second parameter
    const validSecondParams = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24'];
    
    // set preview tiles based off secondParam
    if (validSecondParams.includes(keyBuffer)) {
        secondParam = keyBuffer;
        localStorage.setItem("secondParam", secondParam);
        document.getElementById('second-param').textContent = `Activation: ${secondParam}`;
        console.log("secondParam: ", secondParam);

        const titleIndices = [...selectedTiles.preview]; // Convert the Set to an array
        selectTile(titleIndices); // Update the preview tiles
    }

    if (event.key === 'z') {
        secondParam = ''; // Clear the second parameter
        keyBuffer = "";
        localStorage.setItem("secondParam", secondParam);
        document.getElementById('second-param').textContent = `Activation: ${secondParam}`; // Update the UI
        console.log("secondParam has been cleared.");
        const titleIndices = [...selectedTiles.preview]; // Convert the Set to an array
        selectTile(titleIndices);
    }

    if (event.key === 'm') {
        console.log("Black screen has been triggered.");
        fetch('/blackscreen/', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
        })
        .then(response => response.json())

        .then(() => {
            // Iterate through tile indices and fetch images
            const tileIndices = keyToTileGroupMap['0'] || [];
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

    if (event.key == 'i') {
        const tileNumber = prompt("Enter tile number (e.g., 1, 2, ..., 14):");
        if (tileNumber && !isNaN(tileNumber)) {
            const tileIndex = parseInt(tileNumber, 10);
            if (tileIndex >= 1 && tileIndex <= 14) {
                console.log(`Tile number ${tileIndex} selected.`);
            
                // Call the get_deviceid API
                fetch(`/get-deviceid/${tileIndex}/`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(), // Include CSRF token if necessary
                    },
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Error: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Device ID Response:', data);
                    // document.getElementById('device-response').textContent = JSON.stringify(data, null, 2);
                    formatDataAndDisplay(data);
                })
                .catch(error => {
                    console.error('Error fetching device ID:', error);
                });
            } else {
                alert("Invalid tile number. Please enter a number between 1 and 14.");
                keyBuffer = ""; // Reset buffer on invalid tile
                return; // Exit early
            }
        } else {
            alert("Invalid input. Please enter a valid number.");
            keyBuffer = ""; // Reset buffer on invalid input
            return; // Exit early
        }
        keyBuffer = ""; 
    }

    if (event.key === 'f') {
        fgSequence = true;
        console.log("f has been triggered")
        keyBuffer = "";
        return;
    }

    if (fgSequence && event.key === 'g') {
        console.log("Sequence 'f' followed by 'g' detected.");
        fgSequence = false;
        const tileNumber = prompt("Enter tile number (e.g., 1, 2, ..., 14):");
        fetch('/reboot-device/', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                tile: tileNumber,
            })
        })
        .then(response => response.json())
    }

    if (event.key === 's') {
        console.log("switch setup");
        fetch('/switch-setup/', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                device_id: device,
                setup_id: 257387,
            })
        })
    }
    // Apply the color changes when Enter is pressed
    if (event.key === 'Enter') {
        if (firstParam && secondParam) {
            console.log("first Prameter enterered: ", firstParam)
            console.log("second Paramter entered: ", secondParam)
            sendTriggerRequest(firstParam, secondParam); // Send selected tiles to Django
        }
        keyBuffer = ""; // Clear buffer after Enter
    }
    
    // Limit buffer length to prevent excessive accumulation
    if (keyBuffer.length > 2) {
        keyBuffer = keyBuffer.slice(-2); // Keep only last 2 characters
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const refreshButton = document.getElementById('refresh-legend');
    refreshButton.addEventListener('click', function () {
        fetchLegendData();
    });

    // Listen for key press events
    document.addEventListener('keydown', handleKeyPress);
});

function fetchLegendData() {
    const setupDropdown = document.getElementById('setup-dropdown');
    const selectedSetupId = setupDropdown.value;
    console.log('Selected setup ID:', selectedSetupId);
    fetch(`/fetch-legend-data/${selectedSetupId}`)
        .then(response => response.json())
        .then(data => updateLegendTable(data))
        .catch(error => console.error('Error:', error));
}

function loadLegendTableFromStorage() {
    const savedData = localStorage.getItem('legendData');
    if (savedData) {
        const data = JSON.parse(savedData);
        updateLegendTable(data);
    } else {
        console.log('No legend data found in localStorage.');
    }
}


// save legend data asynchronously
function updateLegendTable(data) {
    const tableBody = document.getElementById('legend-table-body');
    localStorage.setItem('legendData', JSON.stringify(data));
    // Clear the existing table content
    loadSelectedTiles();
    tableBody.innerHTML = '';

    // Create new rows
    const triggersRow = document.createElement('tr');
    const thumbnailsRow = document.createElement('tr');

    const triggersToReplace = ['59', '60', '61', '62'];

    data.forEach(item => {
        // Create trigger cell
        const triggerCell = document.createElement('th');
        // Replace trigger value if it matches the specified triggers
        if (triggersToReplace.includes(String(item.trigger))) {
            triggerCell.textContent = '20';
        } else {
            triggerCell.textContent = item.trigger;
        }
        triggersRow.appendChild(triggerCell);

        // Create thumbnail cell
        const thumbnailCell = document.createElement('td');
        if (item.thumb) {
            const img = document.createElement('img');
            img.src = item.thumb;
            img.alt = 'Thumbnail';
            img.style.width = '100px';
            img.style.height = 'auto';
            thumbnailCell.appendChild(img);
        } else {
            thumbnailCell.textContent = 'No thumbnail available';
        }
        thumbnailsRow.appendChild(thumbnailCell);
    });

    // Append new rows to the table body
    tableBody.appendChild(triggersRow);
    tableBody.appendChild(thumbnailsRow);
}


// Initialize the time when the page loads

updateTime();