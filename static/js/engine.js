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

    // Save/Load button handlers are now in the modal template to ensure proper loading order
});