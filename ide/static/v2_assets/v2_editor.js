/**
 * Scribe Engine V2 Editor
 * Main JavaScript for the visual scene editor
 */

// Project data from HTML
const projectData = document.getElementById('project-data');
const PROJECT_NAME = projectData.dataset.projectName;
const PROJECT_PATH = projectData.dataset.projectPath;

// Editor state
let currentScene = null;
let currentMode = 'visual'; // 'visual' or 'code'
let previewRunning = false;

// Initialize editor when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('[V2 Editor] Initializing...');
    console.log('[V2 Editor] Project:', PROJECT_NAME);

    initializeToolbar();
    initializeCanvas();
    loadSceneList();

    setStatus('V2 Editor ready');
});

// ============================================================================
// Toolbar
// ============================================================================

function initializeToolbar() {
    // Mode toggle buttons
    document.getElementById('btn-visual-mode').addEventListener('click', () => {
        switchMode('visual');
    });

    document.getElementById('btn-code-mode').addEventListener('click', () => {
        switchMode('code');
    });

    // Preview button
    document.getElementById('btn-preview').addEventListener('click', () => {
        togglePreview();
    });

    // Save button
    document.getElementById('btn-save').addEventListener('click', () => {
        saveCurrentScene();
    });
}

function switchMode(mode) {
    currentMode = mode;

    // Update button states
    document.getElementById('btn-visual-mode').classList.toggle('active', mode === 'visual');
    document.getElementById('btn-code-mode').classList.toggle('active', mode === 'code');

    // Update editor visibility
    document.getElementById('visual-editor').classList.toggle('active', mode === 'visual');
    document.getElementById('code-editor').classList.toggle('active', mode === 'code');

    console.log('[V2 Editor] Switched to', mode, 'mode');
}

// ============================================================================
// Canvas Setup
// ============================================================================

let canvas, ctx;
let gridEnabled = true;
let snapEnabled = true;
let zoomLevel = 1.0;

function initializeCanvas() {
    canvas = document.getElementById('scene-canvas');
    ctx = canvas.getContext('2d');

    // Resize canvas to fill container
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Canvas tools
    document.getElementById('btn-grid').addEventListener('click', () => {
        gridEnabled = !gridEnabled;
        document.getElementById('btn-grid').classList.toggle('active', gridEnabled);
        renderCanvas();
    });

    document.getElementById('btn-snap').addEventListener('click', () => {
        snapEnabled = !snapEnabled;
        document.getElementById('btn-snap').classList.toggle('active', snapEnabled);
    });

    document.getElementById('btn-zoom-in').addEventListener('click', () => {
        zoomLevel = Math.min(zoomLevel + 0.1, 3.0);
        updateZoom();
    });

    document.getElementById('btn-zoom-out').addEventListener('click', () => {
        zoomLevel = Math.max(zoomLevel - 0.1, 0.3);
        updateZoom();
    });

    // Mouse tracking
    canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) / zoomLevel);
        const y = Math.floor((e.clientY - rect.top) / zoomLevel);
        document.getElementById('mouse-pos').textContent = `X: ${x}, Y: ${y}`;
    });

    // Initial render
    renderCanvas();
}

function resizeCanvas() {
    const parent = canvas.parentElement;
    canvas.width = parent.clientWidth;
    canvas.height = parent.clientHeight - 80; // Account for toolbars
    renderCanvas();
}

function updateZoom() {
    document.getElementById('zoom-level').textContent = Math.round(zoomLevel * 100) + '%';
    renderCanvas();
}

function renderCanvas() {
    // Clear canvas
    ctx.fillStyle = '#1e1e1e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.save();
    ctx.scale(zoomLevel, zoomLevel);

    // Draw grid if enabled
    if (gridEnabled) {
        drawGrid();
    }

    // Draw sprites (placeholder for now)
    drawPlaceholderSprites();

    ctx.restore();
}

function drawGrid() {
    const gridSize = 32;
    ctx.strokeStyle = '#2a2a2a';
    ctx.lineWidth = 1;

    // Vertical lines
    for (let x = 0; x < canvas.width / zoomLevel; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height / zoomLevel);
        ctx.stroke();
    }

    // Horizontal lines
    for (let y = 0; y < canvas.height / zoomLevel; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width / zoomLevel, y);
        ctx.stroke();
    }
}

function drawPlaceholderSprites() {
    // Placeholder: Draw some example sprites
    ctx.fillStyle = '#0e639c';
    ctx.fillRect(100, 100, 32, 48);

    ctx.fillStyle = '#666';
    ctx.fillRect(50, 200, 150, 20);

    ctx.fillStyle = 'rgba(255, 255, 0, 0.5)';
    ctx.font = '14px sans-serif';
    ctx.fillText('Scene Canvas - Coming Soon', 50, 50);
}

// ============================================================================
// Scene List
// ============================================================================

function loadSceneList() {
    const sceneListEl = document.getElementById('scene-list');

    // Fetch scenes from API
    fetch(`/api/v2/project/${encodeURIComponent(PROJECT_NAME)}/metadata`)
        .then(response => response.json())
        .then(data => {
            const scenes = data.config?.scenes?.scenes || [];

            if (scenes.length === 0) {
                sceneListEl.innerHTML = '<div class="empty-state">No scenes found</div>';
                return;
            }

            sceneListEl.innerHTML = '';
            scenes.forEach(scene => {
                const item = document.createElement('div');
                item.className = 'tree-item';
                item.textContent = scene.name;
                item.dataset.sceneName = scene.name;
                item.addEventListener('click', () => loadScene(scene.name));
                sceneListEl.appendChild(item);
            });

            console.log('[V2 Editor] Loaded', scenes.length, 'scenes');
        })
        .catch(error => {
            console.error('[V2 Editor] Error loading scenes:', error);
            sceneListEl.innerHTML = '<div class="empty-state">Error loading scenes</div>';
        });
}

function loadScene(sceneName) {
    console.log('[V2 Editor] Loading scene:', sceneName);
    currentScene = sceneName;

    // Update UI
    document.getElementById('current-scene-title').textContent = sceneName;

    // Highlight selected scene
    document.querySelectorAll('#scene-list .tree-item').forEach(item => {
        item.classList.toggle('selected', item.dataset.sceneName === sceneName);
    });

    // TODO: Load scene data and render sprites
    setStatus(`Scene loaded: ${sceneName}`);
}

// ============================================================================
// Preview Management
// ============================================================================

function togglePreview() {
    if (previewRunning) {
        stopPreview();
    } else {
        startPreview();
    }
}

function startPreview() {
    console.log('[V2 Editor] Starting preview...');
    setStatus('Starting preview...');

    // TODO: Actually start preview subprocess via API
    // For now, just simulate it
    setTimeout(() => {
        previewRunning = true;
        updatePreviewStatus();
        setStatus('Preview running');
    }, 500);
}

function stopPreview() {
    console.log('[V2 Editor] Stopping preview...');
    setStatus('Stopping preview...');

    // TODO: Actually stop preview subprocess via API
    setTimeout(() => {
        previewRunning = false;
        updatePreviewStatus();
        setStatus('Preview stopped');
    }, 300);
}

function updatePreviewStatus() {
    const statusEl = document.getElementById('preview-status');
    const btnPreview = document.getElementById('btn-preview');

    if (previewRunning) {
        statusEl.textContent = 'Preview: Running';
        statusEl.className = 'preview-indicator running';
        btnPreview.textContent = '⏹ Stop Preview';
    } else {
        statusEl.textContent = 'Preview: Stopped';
        statusEl.className = 'preview-indicator stopped';
        btnPreview.textContent = '▶ Preview';
    }
}

// ============================================================================
// Save/Load
// ============================================================================

function saveCurrentScene() {
    if (!currentScene) {
        alert('No scene loaded');
        return;
    }

    console.log('[V2 Editor] Saving scene:', currentScene);
    setStatus('Saving scene...');

    // TODO: Implement actual save logic
    setTimeout(() => {
        setStatus('Scene saved successfully');
    }, 300);
}

// ============================================================================
// Utilities
// ============================================================================

function setStatus(message) {
    document.getElementById('status-message').textContent = message;
    console.log('[V2 Editor]', message);
}
