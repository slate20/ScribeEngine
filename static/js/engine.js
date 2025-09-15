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

    // Passage search functionality
    const passageSearchBtn = document.getElementById('passage-search-btn');
    const passageSearchModal = document.getElementById('passage-search-modal');
    const passageSearchInput = document.getElementById('passage-search-input');
    const passageSearchResults = document.getElementById('passage-search-results');

    let allPassages = [];

    if (passageSearchBtn) {
        passageSearchBtn.addEventListener('click', function () {
            openPassageSearchModal();
        });
    }

    function openPassageSearchModal() {
        // Fetch passages if we haven't already
        if (allPassages.length === 0) {
            fetch('/debug/passages')
                .then(response => response.json())
                .then(passages => {
                    allPassages = passages.sort();
                    showPassageSearchModal();
                })
                .catch(error => {
                    console.error('Error fetching passages:', error);
                });
        } else {
            showPassageSearchModal();
        }
    }

    function showPassageSearchModal() {
        passageSearchModal.classList.add('show');
        passageSearchInput.value = '';
        passageSearchInput.focus();
        displayPassages(allPassages);
    }

    if (passageSearchInput) {
        passageSearchInput.addEventListener('input', function () {
            const query = this.value.toLowerCase();
            const filteredPassages = allPassages.filter(passage =>
                passage.toLowerCase().includes(query)
            );
            displayPassages(filteredPassages);
        });

        passageSearchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                closePassageSearchModal();
            } else if (e.key === 'Enter') {
                const firstResult = passageSearchResults.querySelector('.passage-result');
                if (firstResult) {
                    firstResult.click();
                }
            }
        });
    }

    function displayPassages(passages) {
        if (passages.length === 0) {
            passageSearchResults.innerHTML = '<div class="no-results">No matching passages found</div>';
            return;
        }

        const html = passages.slice(0, 20).map(passage =>
            `<div class="passage-result" data-passage="${passage}">
                <span class="passage-name">${passage}</span>
            </div>`
        ).join('');

        if (passages.length > 20) {
            passageSearchResults.innerHTML = html + '<div class="result-limit">Showing first 20 results...</div>';
        } else {
            passageSearchResults.innerHTML = html;
        }

        // Add click handlers to results
        passageSearchResults.querySelectorAll('.passage-result').forEach(result => {
            result.addEventListener('click', function () {
                const passageName = this.dataset.passage;
                navigateToPassage(passageName);
            });
        });
    }

    function navigateToPassage(passageName) {
        closePassageSearchModal();
        // Use HTMX to navigate to the passage
        htmx.ajax('GET', `/passage/${encodeURIComponent(passageName)}`, '#game-content');
    }

    window.closePassageSearchModal = function() {
        passageSearchModal.classList.remove('show');
    }

    // Close modal when clicking outside
    passageSearchModal.addEventListener('click', function (e) {
        if (e.target === passageSearchModal) {
            closePassageSearchModal();
        }
    });

    document.body.addEventListener('htmx:afterRequest', function (event) {
        if (debugPanel && debugPanel.style.display !== 'none') {
            fetch('/debug/state')
                .then(response => response.json())
                .then(data => {
                    debugContent.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                });
        }
    });

    // Back button functionality
    const navBackBtn = document.getElementById('nav-back-btn');

    function updateBackButton() {
        if (!navBackBtn) return;

        fetch('/debug/state')
            .then(response => response.json())
            .then(data => {
                const lastPassage = data.last_passage;
                if (lastPassage) {
                    navBackBtn.disabled = false;
                    navBackBtn.title = `Return to ${lastPassage}`;
                    navBackBtn.onclick = function() {
                        htmx.ajax('GET', `/passage/${encodeURIComponent(lastPassage)}`, '#game-content');
                    };
                } else {
                    navBackBtn.disabled = true;
                    navBackBtn.title = 'No previous passage';
                    navBackBtn.onclick = null;
                }
            })
            .catch(error => {
                console.error('Error fetching game state for back button:', error);
                navBackBtn.disabled = true;
            });
    }

    // Update back button on page load
    if (navBackBtn) {
        updateBackButton();
    }

    // Update back button after each HTMX request
    document.body.addEventListener('htmx:afterRequest', function (event) {
        updateBackButton();
    });

    // Save/Load button handlers are now in the modal template to ensure proper loading order
});