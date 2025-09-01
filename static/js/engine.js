document.addEventListener('DOMContentLoaded', function() {
    const saveBtn = document.getElementById('save-btn');
    const loadBtn = document.getElementById('load-btn');
    const debugBtn = document.getElementById('debug-btn');

    if (saveBtn) {
        saveBtn.addEventListener('click', () => saveGame());
    }

    if (loadBtn) {
        loadBtn.addEventListener('click', () => loadGame());
    }

    if (debugBtn) {
        debugBtn.addEventListener('click', () => toggleDebug());
    }

    // Auto-refresh debug info on passage navigation
    const gameContent = document.getElementById('game-content');
    if (gameContent) {
        gameContent.addEventListener('htmx:afterSwap', function() {
            const debugPanel = document.getElementById('debug-panel');
            if (debugPanel && debugPanel.style.display !== 'none') {
                updateDebugInfo();
            }
        });
    }
});

function saveGame(slot = 1) {
    fetch('/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ slot: slot }),
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            alert('Game saved!');
        } else {
            alert('Error saving game: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error saving game:', error);
        alert('An error occurred while saving the game.');
    });
}

function loadGame(slot = 1) {
    fetch('/load', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ slot: slot }),
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            alert('Game loaded!');
            // HTMX will not automatically process the new content, so we need to do it manually
            const gameContent = document.getElementById('game-content');
            if (gameContent) {
                gameContent.innerHTML = data.passage_html;
                htmx.process(gameContent);
            }
        } else {
            alert('Error loading game: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error loading game:', error);
        alert('An error occurred while loading the game.');
    });
}

function toggleDebug() {
    const panel = document.getElementById('debug-panel');
    if (panel) {
        if (panel.style.display === 'none') {
            panel.style.display = 'block';
            updateDebugInfo();
        } else {
            panel.style.display = 'none';
        }
    }
}

function updateDebugInfo() {
    const debugContent = document.getElementById('debug-content');
    if (debugContent) {
        fetch('/debug/state')
            .then(response => response.json())
            .then(data => {
                debugContent.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            })
            .catch(error => {
                console.error('Error fetching debug info:', error);
                debugContent.innerHTML = 'Error loading debug information.';
            });
    }
}