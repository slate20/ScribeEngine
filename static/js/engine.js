document.addEventListener('DOMContentLoaded', function () {
    const debugBtn = document.getElementById('debug-btn');
    const debugPanel = document.getElementById('debug-panel');
    const debugContent = document.getElementById('debug-content');

    if (debugBtn && debugPanel) {
        debugBtn.addEventListener('click', function () {
            const isHidden = debugPanel.style.display === 'none';
            debugPanel.style.display = isHidden ? 'block' : 'none';
            if (isHidden) {
                fetch('/debug/state')
                    .then(response => response.json())
                    .then(data => {
                        debugContent.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    });
            }
        });
    }

    document.body.addEventListener('htmx:afterRequest', function (event) {
        if (debugPanel && debugPanel.style.display !== 'none') {
            fetch('/debug/state')
                .then(response => response.json())
                .then(data => {
                    debugContent.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                });
        }
    });

    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', function () {
            fetch('/save', { method: 'POST', body: JSON.stringify({ slot: 1 }), headers: { 'Content-Type': 'application/json' } })
                .then(response => response.json())
                .then(data => {
                    console.log('Game saved:', data);
                    alert('Game saved!');
                });
        });
    }

    const loadBtn = document.getElementById('load-btn');
    if (loadBtn) {
        loadBtn.addEventListener('click', function () {
            fetch('/load', { method: 'POST', body: JSON.stringify({ slot: 1 }), headers: { 'Content-Type': 'application/json' } })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        console.log('Game loaded:', data);
                        if (data.passage_html) {
                            document.getElementById('game-content').innerHTML = data.passage_html;
                        }
                        alert('Game loaded!');
                        htmx.process(document.getElementById('game-content'));
                    } else {
                        alert('Error loading game: ' + data.message);
                    }
                });
        });
    }
});