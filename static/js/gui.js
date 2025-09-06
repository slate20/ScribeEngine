// Global state
let currentProject = null;
let activeFiles = [];
let currentFile = null;

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Editor functionality
document.addEventListener('DOMContentLoaded', function () {
    // You can add your editor-related logic here as we build out the GUI.
    // For now, this event listener is intentionally left empty to prevent
    // any demo code from running.
});
