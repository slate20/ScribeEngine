// Global state
let currentView = 'split';
let gridEnabled = true;
let collisionEnabled = false;
let zoomLevel = 100;
let selectedSprite = null;
let isDragging = false;
let dragOffset = { x: 0, y: 0 };

// Canvas references
const canvas = document.getElementById('scene-canvas');
const ctx = canvas.getContext('2d');

// Mock sprite data
const sprites = [
    { id: 'player', name: 'Player', x: 100, y: 400, width: 32, height: 48, color: '#4ec9b0', label: '🧍' },
    { id: 'enemy', name: 'Enemy (Slime)', x: 300, y: 400, width: 32, height: 32, color: '#f48771', label: '👾' },
    { id: 'coin', name: 'Coin', x: 200, y: 350, width: 16, height: 16, color: '#ffd700', label: '💰' }
];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initCanvas();
    drawScene();
    switchView('split');
});

// Canvas initialization
function initCanvas() {
    canvas.addEventListener('mousedown', handleCanvasMouseDown);
    canvas.addEventListener('mousemove', handleCanvasMouseMove);
    canvas.addEventListener('mouseup', handleCanvasMouseUp);
    canvas.addEventListener('mouseleave', handleCanvasMouseUp);
}

// Drawing functions
function drawScene() {
    // Clear canvas
    ctx.fillStyle = '#2a2a2a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    if (gridEnabled) {
        drawGrid();
    }

    // Draw background indicator
    ctx.fillStyle = '#1a3a1a';
    ctx.fillRect(0, 0, canvas.width, 100);
    ctx.fillStyle = '#666';
    ctx.font = '12px Arial';
    ctx.fillText('Background: forest_bg.png', 10, 20);

    // Draw platform area
    ctx.fillStyle = '#4a3a2a';
    ctx.fillRect(0, 450, canvas.width, 150);
    ctx.fillStyle = '#666';
    ctx.fillText('Tilemap: level1.tmx', 10, 470);

    // Draw sprites
    sprites.forEach(sprite => {
        drawSprite(sprite);
    });
}

function drawGrid() {
    const gridSize = 16;
    ctx.strokeStyle = '#3a3a3a';
    ctx.lineWidth = 1;

    // Vertical lines
    for (let x = 0; x <= canvas.width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
    }

    // Horizontal lines
    for (let y = 0; y <= canvas.height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    }
}

function drawSprite(sprite) {
    const isSelected = selectedSprite && selectedSprite.id === sprite.id;

    // Draw sprite rectangle
    ctx.fillStyle = sprite.color;
    ctx.fillRect(sprite.x, sprite.y, sprite.width, sprite.height);

    // Draw label
    ctx.font = '20px Arial';
    ctx.fillText(sprite.label, sprite.x + sprite.width / 2 - 10, sprite.y + sprite.height / 2 + 8);

    // Draw selection outline
    if (isSelected) {
        ctx.strokeStyle = '#007acc';
        ctx.lineWidth = 2;
        ctx.strokeRect(sprite.x - 2, sprite.y - 2, sprite.width + 4, sprite.height + 4);
    }

    // Draw collision box
    if (collisionEnabled) {
        ctx.strokeStyle = '#ff00ff';
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.strokeRect(sprite.x, sprite.y, sprite.width, sprite.height);
        ctx.setLineDash([]);
    }

    // Draw name label
    ctx.fillStyle = '#d4d4d4';
    ctx.font = '10px Arial';
    ctx.fillText(sprite.name, sprite.x, sprite.y - 5);
}

// Mouse handling
function handleCanvasMouseDown(e) {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Check if clicking on a sprite
    for (let i = sprites.length - 1; i >= 0; i--) {
        const sprite = sprites[i];
        if (mouseX >= sprite.x && mouseX <= sprite.x + sprite.width &&
            mouseY >= sprite.y && mouseY <= sprite.y + sprite.height) {
            selectSprite(sprite);
            isDragging = true;
            dragOffset.x = mouseX - sprite.x;
            dragOffset.y = mouseY - sprite.y;
            return;
        }
    }

    // Deselect if clicking empty area
    selectSprite(null);
}

function handleCanvasMouseMove(e) {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Update mouse position display
    document.getElementById('mouse-pos').textContent = `Mouse: (${Math.round(mouseX)}, ${Math.round(mouseY)})`;

    // Handle dragging
    if (isDragging && selectedSprite) {
        let newX = mouseX - dragOffset.x;
        let newY = mouseY - dragOffset.y;

        // Snap to grid if enabled
        if (document.getElementById('snap-toggle').checked) {
            const gridSize = 16;
            newX = Math.round(newX / gridSize) * gridSize;
            newY = Math.round(newY / gridSize) * gridSize;
        }

        selectedSprite.x = Math.max(0, Math.min(canvas.width - selectedSprite.width, newX));
        selectedSprite.y = Math.max(0, Math.min(canvas.height - selectedSprite.height, newY));

        drawScene();
        updateInspector();
    }
}

function handleCanvasMouseUp(e) {
    if (isDragging) {
        isDragging = false;
        updateCodeFromVisual();
    }
}

// Sprite selection
function selectSprite(sprite) {
    selectedSprite = sprite;

    // Update hierarchy selection
    document.querySelectorAll('.hierarchy-item').forEach(item => {
        item.classList.remove('selected');
    });

    if (sprite) {
        const hierarchyItems = document.querySelectorAll('.hierarchy-item');
        hierarchyItems.forEach(item => {
            if (item.textContent.includes(sprite.name)) {
                item.classList.add('selected');
            }
        });
        document.getElementById('selected-sprite').textContent = `Selected: ${sprite.name}`;
    } else {
        document.getElementById('selected-sprite').textContent = 'Selected: None';
    }

    updateInspector();
    drawScene();
}

// Inspector updates
function updateInspector() {
    if (selectedSprite) {
        document.getElementById('pos-x').value = selectedSprite.x;
        document.getElementById('pos-y').value = selectedSprite.y;
    }
}

function updateSpritePosition() {
    if (selectedSprite) {
        selectedSprite.x = parseInt(document.getElementById('pos-x').value) || 0;
        selectedSprite.y = parseInt(document.getElementById('pos-y').value) || 0;
        drawScene();
        updateCodeFromVisual();
    }
}

// Code synchronization
function updateCodeFromVisual() {
    // In a real implementation, this would update the Python code
    // to reflect the visual changes
    console.log('Code would be updated with sprite positions:', sprites);
}

// View switching
function switchView(view) {
    currentView = view;

    // Update tab states
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');

    const visualEditor = document.getElementById('visual-editor');
    const codeEditor = document.getElementById('code-editor');

    switch(view) {
        case 'visual':
            visualEditor.style.display = 'flex';
            codeEditor.style.display = 'none';
            break;
        case 'code':
            visualEditor.style.display = 'none';
            codeEditor.style.display = 'flex';
            break;
        case 'split':
            visualEditor.style.display = 'flex';
            codeEditor.style.display = 'flex';
            break;
    }

    // Redraw canvas when switching to visual view
    if (view !== 'code') {
        drawScene();
    }
}

// Grid and collision toggles
function toggleGrid() {
    gridEnabled = document.getElementById('grid-toggle').checked;
    drawScene();
}

function toggleCollision() {
    collisionEnabled = document.getElementById('collision-toggle').checked;
    drawScene();
}

// Zoom controls
function zoomIn() {
    if (zoomLevel < 200) {
        zoomLevel += 10;
        updateZoom();
    }
}

function zoomOut() {
    if (zoomLevel > 50) {
        zoomLevel -= 10;
        updateZoom();
    }
}

function updateZoom() {
    document.getElementById('zoom-level').textContent = `${zoomLevel}%`;
    const scale = zoomLevel / 100;
    canvas.style.transform = `scale(${scale})`;
    canvas.style.transformOrigin = 'center center';
}

// Play/Stop scene
function playScene() {
    console.log('Playing scene...');
    document.querySelector('.status-left .status-item').innerHTML = '▶️ Running';

    // In real implementation, this would:
    // 1. Save current scene
    // 2. Send request to Flask backend
    // 3. Flask spawns subprocess: python run_scene.py level_1
    // 4. Pygame window opens

    alert('In the real IDE:\n\n1. Scene would be saved\n2. Flask backend spawns: python run_scene.py level_1\n3. Pygame window opens with live game\n4. Hot reload enabled for code changes');
}

function stopScene() {
    console.log('Stopping scene...');
    document.querySelector('.status-left .status-item').innerHTML = '✅ Ready';
}

// File selection
function selectFile(element, filename) {
    document.querySelectorAll('.tree-item').forEach(item => {
        item.classList.remove('active');
    });
    element.classList.add('active');

    document.querySelector('.file-name').textContent = `scenes/${filename}`;
    document.querySelector('.code-header span').textContent = `scenes/${filename}`;
}

// Tree section toggle
function toggleSection(header) {
    header.classList.toggle('collapsed');
}

// Auto-select player sprite on load
setTimeout(() => {
    selectSprite(sprites[0]);
}, 100);
