/**
 * Scribe Engine Browser Storage System
 * Handles localStorage-based save/load operations for web-hosted games
 */

class ScribeBrowserStorage {
    constructor(projectName = 'default') {
        this.projectPrefix = `scribe_${projectName}_`;
        this.maxSlots = 6;
        this.setupStorageCallback();
    }

    setupStorageCallback() {
        // Global callback for storage operations
        window.scribeStorageCallback = (result) => {
            // Handle different operation types
            switch (result.type) {
                case 'save':
                    this.handleSaveResult(result);
                    break;
                case 'load':
                    this.handleLoadResult(result);
                    break;
                case 'list_saves':
                    this.handleListSavesResult(result);
                    break;
                case 'metadata':
                    this.handleMetadataResult(result);
                    break;
                case 'delete':
                    this.handleDeleteResult(result);
                    break;
                case 'export':
                    this.handleExportResult(result);
                    break;
                case 'import':
                    this.handleImportResult(result);
                    break;
                case 'validate':
                    this.handleValidateResult(result);
                    break;
            }
        };
    }

    handleSaveResult(result) {
        if (result.success) {
            this.showNotification('Game saved successfully', 'success');
            // Refresh save UI if modal is open
            this.refreshSaveModal();
        } else {
            this.showNotification(result.message || 'Failed to save game', 'error');
        }
    }

    handleLoadResult(result) {
        if (result.success && result.data) {
            // Send loaded data to server for processing
            fetch('/browser-storage/load-complete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    slot: result.slot,
                    save_data: result.data
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.showNotification('Game loaded successfully', 'success');
                    // Refresh the game display
                    if (data.passage_html) {
                        document.getElementById('game-content').innerHTML = data.passage_html;
                    }
                    // Close load modal
                    this.closeModal();
                } else {
                    this.showNotification(data.message || 'Failed to load game', 'error');
                }
            })
            .catch(error => {
                console.error('Load completion failed:', error);
                this.showNotification('Failed to complete game load', 'error');
            });
        } else {
            this.showNotification(result.message || 'Failed to load game', 'error');
        }
    }

    handleListSavesResult(result) {
        if (result.success) {
            this.currentSaveList = result.data;
            this.updateSaveListUI(result.data);
        } else {
            this.currentSaveList = {};
            this.updateSaveListUI({});
        }
    }

    handleMetadataResult(result) {
        // Handle individual metadata requests
        if (this.metadataCallbacks && this.metadataCallbacks[result.slot]) {
            this.metadataCallbacks[result.slot](result.success ? result.data : null);
            delete this.metadataCallbacks[result.slot];
        }

        // Update load details panel if this is for a selected slot
        if (result.success && result.data) {
            this.updateLoadDetailsPanel(result.slot, result.data);
        }
    }

    updateLoadDetailsPanel(slot, saveInfo) {
        // Find the load details container
        const detailsContainer = document.getElementById('load-details');
        if (!detailsContainer) {
            return;
        }

        // Format timestamps
        const formatTimestamp = (timestamp) => {
            if (!timestamp) return 'Unknown';
            return new Date(timestamp).toLocaleString();
        };

        const formatPlaytime = (seconds) => {
            if (!seconds || seconds === 0) return '0m';
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            if (hours > 0) {
                return `${hours}h ${minutes}m`;
            }
            return `${minutes}m`;
        };

        // Build the details HTML
        const detailsHTML = `
            <div class="load-details">
                <div class="save-preview">
                    <h4>${saveInfo.description || 'Untitled Save'}</h4>
                    <div class="save-metadata">
                        <p><strong>Location:</strong> ${saveInfo.passage_name || 'Unknown'}</p>
                        <p><strong>Saved:</strong> ${formatTimestamp(saveInfo.timestamp)}</p>
                        <p><strong>Play Time:</strong> ${formatPlaytime(saveInfo.playtime)}</p>
                        ${saveInfo.created_timestamp !== saveInfo.timestamp ?
                            `<p><strong>Created:</strong> ${formatTimestamp(saveInfo.created_timestamp)}</p>` : ''}
                    </div>
                </div>
                <div class="load-actions">
                    <button type="button" class="btn btn-outline btn-sm"
                            onclick="deleteBrowserSave(${slot})">
                        Delete Save
                    </button>
                    <button type="button" class="btn btn-outline btn-sm"
                            onclick="exportBrowserSave(${slot})">
                        Export Save
                    </button>
                </div>
            </div>
            <form id="load-form" style="display: none;">
                <input type="hidden" name="slot" value="${slot}">
            </form>
        `;

        detailsContainer.innerHTML = detailsHTML;

        // Enable the load button
        const loadBtn = document.getElementById('confirm-load-btn');
        if (loadBtn) {
            loadBtn.disabled = false;
        }
    }

    handleDeleteResult(result) {
        if (result.success) {
            this.showNotification('Save deleted successfully', 'success');
            // Refresh save UI
            this.refreshSaveModal();
            this.refreshLoadModal();
        } else {
            this.showNotification(result.message || 'Failed to delete save', 'error');
        }
    }

    handleExportResult(result) {
        if (result.success) {
            this.showNotification('Save exported successfully', 'success');
        } else {
            this.showNotification(result.message || 'Failed to export save', 'error');
        }
    }

    handleImportResult(result) {
        if (result.success) {
            this.showNotification('Save imported successfully', 'success');
            // Refresh save UI
            this.refreshSaveModal();
            this.refreshLoadModal();
        } else {
            this.showNotification(result.message || 'Failed to import save', 'error');
        }
    }

    handleValidateResult(result) {
        // Handle validation results as needed
    }

    // Utility methods for UI interaction
    showNotification(message, type = 'info') {
        // Try to use existing notification system
        if (window.showNotification) {
            window.showNotification(message, type);
        } else {
            // Fallback notification
            alert(message);
        }
    }

    closeModal() {
        // Close any open modals
        const modal = document.getElementById('modal-container');
        if (modal) {
            modal.innerHTML = '';
        }
    }

    refreshSaveModal() {
        // Refresh save modal if it's open
        const saveModal = document.querySelector('.save-modal');
        if (saveModal) {
            // Trigger refresh of save list
            this.requestSaveList();
        }
    }

    refreshLoadModal() {
        // Refresh load modal if it's open
        const loadModal = document.querySelector('.load-modal');
        if (loadModal) {
            // Trigger refresh of save list
            this.requestSaveList();
        }
    }

    updateSaveListUI(saves) {
        // Update save slot UI elements - find by slot number in the grid
        const saveSlots = document.querySelectorAll('.save-slot');

        saveSlots.forEach((slotElement, index) => {
            const slot = index + 1; // Slots are 1-indexed
            const saveData = saves[slot];

            if (saveData) {
                slotElement.classList.add('populated');
                slotElement.classList.remove('empty');

                // Update metadata display with correct selectors
                const descElement = slotElement.querySelector('.slot-description');
                const passageElement = slotElement.querySelector('.slot-passage');
                const timeElement = slotElement.querySelector('.slot-date');

                // Try alternative selectors if the main ones don't work
                const slotContent = slotElement.querySelector('.slot-content');

                if (descElement) {
                    descElement.textContent = saveData.description || 'Untitled Save';
                } else if (slotContent) {
                    // Rebuild the content structure if elements don't exist
                    slotContent.innerHTML = `
                        <div class="slot-description">${saveData.description || 'Untitled Save'}</div>
                        <div class="slot-meta">
                            <div class="slot-passage">${saveData.passage_name || 'Unknown'}</div>
                            <div class="slot-date">${new Date(saveData.timestamp).toLocaleString()}</div>
                        </div>
                    `;
                }

                if (passageElement) {
                    passageElement.textContent = saveData.passage_name || 'Unknown';
                }
                if (timeElement) {
                    const date = new Date(saveData.timestamp);
                    timeElement.textContent = date.toLocaleString();
                }

                // Enable click handler for load modal
                if (document.getElementById('load-modal')) {
                    slotElement.setAttribute('hx-post', '/modal/load/select');
                    slotElement.setAttribute('hx-vals', JSON.stringify({slot: slot}));
                    slotElement.setAttribute('hx-target', '#load-details');
                    slotElement.setAttribute('onclick', 'selectSlot(this)');
                    slotElement.style.cursor = 'pointer';
                }
            } else {
                slotElement.classList.add('empty');
                slotElement.classList.remove('populated');

                // Clear metadata display
                const slotContent = slotElement.querySelector('.slot-content');
                if (slotContent) {
                    slotContent.innerHTML = '<div class="empty-slot">Empty</div>';
                }

                // Remove click handlers for empty slots
                slotElement.removeAttribute('hx-post');
                slotElement.removeAttribute('hx-vals');
                slotElement.removeAttribute('hx-target');
                slotElement.removeAttribute('onclick');
                slotElement.style.cursor = 'default';
            }
        });
    }

    requestSaveList() {
        // Request save list from server (which will trigger JS execution)
        fetch('/saves/metadata')
            .then(response => response.json())
            .then(data => {
                if (data.type === 'javascript') {
                    // Execute the JavaScript code
                    eval(data.code);
                }
            })
            .catch(error => {
                // Silently handle save list request errors
            });
    }

    // File import handling
    setupFileImport() {
        // Create hidden file input for imports
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.json';
        fileInput.style.display = 'none';
        document.body.appendChild(fileInput);

        fileInput.addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const saveData = JSON.parse(e.target.result);
                        // Send to server for import processing
                        const slot = this.pendingImportSlot || 1;

                        fetch(`/saves/${slot}/import`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(saveData)
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.type === 'javascript') {
                                eval(data.code);
                            }
                        })
                        .catch(error => {
                            this.showNotification('Failed to import save', 'error');
                        });
                    } catch (error) {
                        this.showNotification('Invalid save file format', 'error');
                    }
                };
                reader.readAsText(file);
            }
        });

        this.fileInput = fileInput;
    }

    importSave(slot) {
        this.pendingImportSlot = slot;
        if (!this.fileInput) {
            this.setupFileImport();
        }
        this.fileInput.click();
    }

    // Storage size monitoring
    getStorageInfo() {
        try {
            let totalSize = 0;
            let scribeSize = 0;

            for (let key in localStorage) {
                if (localStorage.hasOwnProperty(key)) {
                    const size = localStorage[key].length;
                    totalSize += size;

                    if (key.startsWith('scribe_')) {
                        scribeSize += size;
                    }
                }
            }

            // Estimate storage limit (usually 5-10MB)
            const estimatedLimit = 5 * 1024 * 1024; // 5MB in characters (rough estimate)

            return {
                totalSize,
                scribeSize,
                estimatedLimit,
                percentUsed: (totalSize / estimatedLimit) * 100
            };
        } catch (error) {
            return null;
        }
    }

    checkStorageSpace() {
        const info = this.getStorageInfo();
        if (info && info.percentUsed > 80) {
            this.showNotification(
                `Browser storage is ${Math.round(info.percentUsed)}% full. Consider exporting saves as backup.`,
                'warning'
            );
        }
    }
}

// Initialize browser storage if in browser mode
let scribeBrowserStorage = null;

function initializeBrowserStorage(projectName) {
    scribeBrowserStorage = new ScribeBrowserStorage(projectName);
    scribeBrowserStorage.checkStorageSpace();
}

// Global functions for browser storage operations
function deleteBrowserSave(slot) {
    if (confirm('Are you sure you want to delete this save?')) {
        // Make HTMX request to delete route which will return JavaScript
        fetch(`/saves/${slot}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.type === 'javascript') {
                eval(data.code);
            }
        })
        .catch(error => {
            // Silently handle delete errors
        });
    }
}

function exportBrowserSave(slot) {
    // Make HTMX request to export route which will return JavaScript for download
    fetch(`/saves/${slot}/export`)
    .then(response => response.json())
    .then(data => {
        if (data.type === 'javascript') {
            eval(data.code);
        }
    })
    .catch(error => {
        // Silently handle export errors
    });
}

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScribeBrowserStorage;
}