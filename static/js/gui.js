// Global state for the editor
let editor;
let unsavedFiles = new Set(); // To track files with unsaved changes
let currentProject = null;
let currentFile = null;
let gameStateIntervalId = null; // Global variable to store the interval ID
let ignoreNextChange = false; // Flag to ignore programmatic changes

/**
 * Initializes the CodeMirror editor instance.
 */
function initEditor() {
	const container = document.getElementById('codemirror-container');
	if (!container) {
		console.error("CodeMirror container could not be found in the DOM.");
		return;
	}

	// Prevent initializing more than once
	if (editor) {
		return;
	}

	editor = CodeMirror(container, {
		value: "// Select a file from the list to begin editing.",
		mode: 'jinja2',
		theme: 'material-darker',
		lineNumbers: true,
		readOnly: true, // Start as read-only until a file is opened
		extraKeys: {
			"Ctrl-S": function (cm) {
				saveFile();
			}
		}
	});

	editor.on('change', function() {
		if (ignoreNextChange) {
			ignoreNextChange = false; // Reset the flag
			return; // Ignore this change
		}
		if (currentFile && !editor.getOption("readOnly")) {
			unsavedFiles.add(currentFile);
			updateEditorUI();
		}
	});
}

/**
 * Opens a file in the editor by fetching its content from the server.
 * @param {string} projectName - The name of the current project.
 * @param {string} fileName - The name of the file to open.
 * @param {HTMLElement} element - The clicked file list item.
 */
function openFile(projectName, fileName, element) {
	if (!editor) {
		console.error("Editor is not initialized. Cannot open file.");
		return;
	}
	// Update UI to show which file is active
	document.querySelectorAll('.file-item').forEach(item => item.classList.remove('active'));
	element.classList.add('active');

	// Store current project and file
	currentProject = projectName;
	currentFile = fileName;

	// Update the editor header title
	const editorFileTitle = document.getElementById('editor-file-title');
	if (editorFileTitle) {
		editorFileTitle.textContent = fileName;
	}

	fetch(`/api/get-file-content/${projectName}/${fileName}`)
		.then(response => response.json())
		.then(data => {
			if (data.status === 'success') {
					ignoreNextChange = true; // Set flag to ignore the change event from setValue
					editor.setValue(data.content);
					editor.setOption("readOnly", false); // Make editor writable
					updateEditorUI(); // Call updateEditorUI after file is loaded

				// Set the correct syntax highlighting mode based on file extension
				let mode = 'scribe'; // Default for .tgame
				if (fileName.endsWith('.py')) {
					mode = 'python';
				} else if (fileName.endsWith('.json')) {
					mode = { name: 'javascript', json: true };
				} else if (fileName.endsWith('.css')) {
					mode = 'css';
				}
				editor.setOption("mode", mode);

			} else {
				showNotification(data.message, 'error');
			}
		})
		.catch(err => {
			console.error('Error fetching file:', err);
			showNotification('Could not load file.', 'error');
		});
}

/**
 * Saves the current content of the editor to the server.
 */
function saveFile() {
	if (!currentProject || !currentFile || !editor || editor.getOption("readOnly")) {
		showNotification('No file is open to save.', 'warning');
		return;
	}

	const content = editor.getValue();

	fetch(`/api/save-file/${currentProject}/${currentFile}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			content: content
		})
	})
		.then(response => response.json())
		.then(data => {
			if (data.status === 'success') {
				showNotification(data.message, 'success');
				unsavedFiles.delete(currentFile); // Remove from unsavedFiles
				updateEditorUI(); // Update UI after save
				// Refresh the preview iframe after a successful save
				refreshPreview();
			} else {
				showNotification(data.message, 'error');
			}
		})
		.catch(err => {
			console.error('Error saving file:', err);
			showNotification('Could not save file.', 'error');
		});
}

/**
 * Reloads the content of the preview iframe.
 */
function refreshPreview() {
	const iframe = document.getElementById('preview-iframe');
	if (iframe) {
		// Appending ?t=${new Date().getTime()} is a common trick to bypass browser caching
		iframe.src = `/`;
		showNotification('Preview refreshed!', 'info');
	}
}

/**
 * Displays a temporary notification on the screen.
 * @param {string} message - The message to display.
 * @param {string} type - The type of notification ('success', 'error', 'warning', 'info').
 */
function showNotification(message, type = 'info') {
	const notification = document.createElement('div');
	const colors = {
		success: 'var(--success-color)',
		error: 'var(--danger-color)',
		warning: 'var(--warning-color)',
		info: 'var(--accent-color)'
	};

	notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 12px 20px;
        background: ${colors[type] || colors.info};
        color: white;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        z-index: 1001;
        opacity: 0;
        transform: translateY(-10px);
        transition: all 0.3s;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
	notification.textContent = message;
	document.body.appendChild(notification);

	setTimeout(() => {
		notification.style.opacity = '1';
		notification.style.transform = 'translateY(0)';
	}, 10);

	setTimeout(() => {
		notification.style.opacity = '0';
		notification.style.transform = 'translateY(-10px)';
		setTimeout(() => {
			if (notification.parentNode) {
				notification.parentNode.removeChild(notification);
			}
		}, 300);
	}, 4000);
}

/**
 * Initializes the draggable divider between the editor and preview panels.
 */
function initResizer() {
	const handle = document.getElementById('drag-handle');
	const leftPanel = document.getElementById('editor-area');
	const rightPanel = document.getElementById('previewPanel');
	const container = document.querySelector('.main-content');

	if (!handle || !leftPanel || !rightPanel || !container) return;

	// Set initial panel sizes (e.g., 65% for editor, 35% for preview)
	const sidebarWidth = document.querySelector('.sidebar').offsetWidth;
	const availableWidth = container.offsetWidth - sidebarWidth - handle.offsetWidth;
	leftPanel.style.width = `${availableWidth * 0.65}px`;
	rightPanel.style.width = `${availableWidth * 0.35}px`;

	let isDragging = false;
	let startX, startLeftWidth, startRightWidth;

	handle.addEventListener('mousedown', function (e) {
		isDragging = true;
		startX = e.clientX;
		startLeftWidth = leftPanel.offsetWidth;
		startRightWidth = rightPanel.offsetWidth;
		
		document.body.style.cursor = 'col-resize';
		document.body.style.userSelect = 'none';
		document.body.style.pointerEvents = 'none';
	});

	document.addEventListener('mousemove', function (e) {
		if (!isDragging) return;
		
		const deltaX = e.clientX - startX;
		const newLeftWidth = startLeftWidth + deltaX;
		const newRightWidth = startRightWidth - deltaX;

		// Apply constraints
		if (newLeftWidth > 300 && newRightWidth > 300) {
			leftPanel.style.width = `${newLeftWidth}px`;
			rightPanel.style.width = `${newRightWidth}px`;
		}
	});

	document.addEventListener('mouseup', function (e) {
		isDragging = false;
		document.body.style.cursor = '';
		document.body.style.userSelect = '';
		document.body.style.pointerEvents = '';
	});
}

/**
 * Initializes the draggable resizer for the debug terminal.
 */
function initDebugTerminalResizer() {
    const handle = document.getElementById('debug-terminal-handle');
    const terminal = document.getElementById('debug-terminal');

    if (!handle || !terminal) return;

    let isDragging = false;
    let startY, startHeight;

    handle.addEventListener('mousedown', function (e) {
        isDragging = true;
        startY = e.clientY;
        startHeight = terminal.offsetHeight;

        document.body.style.cursor = 'ns-resize';
        document.body.style.userSelect = 'none';
        document.body.style.pointerEvents = 'none';
    });

    document.addEventListener('mousemove', function (e) {
        if (!isDragging) return;

        const deltaY = e.clientY - startY;
        const newHeight = startHeight - deltaY; // Invert deltaY for dragging from top

        // Apply constraints (min-height and max-height)
        if (newHeight > 30 && newHeight < window.innerHeight * 0.8) { // Example constraints
            terminal.style.height = `${newHeight}px`;
        }
    });

    document.addEventListener('mouseup', function (e) {
        isDragging = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        document.body.style.pointerEvents = '';
    });
}

// New function to update editor UI based on unsaved changes
function updateEditorUI() {
    const saveBtn = document.getElementById('save-file-btn');
    const editorFileTitle = document.getElementById('editor-file-title');

    // Update Save File button
    if (saveBtn) {
        if (currentFile && unsavedFiles.has(currentFile)) {
            saveBtn.classList.add('unsaved-changes');
        } else {
            saveBtn.classList.remove('unsaved-changes');
        }
    }

    // Update Editor Title
    if (editorFileTitle && currentFile) {
        let titleText = currentFile;
        if (unsavedFiles.has(currentFile)) {
            titleText += ' *';
        }
        editorFileTitle.textContent = titleText;
    }

    // Update File List Items
    document.querySelectorAll('.file-item').forEach(item => {
        const filePath = item.dataset.filepath;
        const fileNameSpan = item.querySelector('.file-name'); // Assuming file-name span holds the text

        if (filePath && fileNameSpan) {
            let originalFileName = fileNameSpan.textContent.replace(' *', ''); // Remove existing asterisk if any

            if (unsavedFiles.has(filePath)) {
                item.classList.add('unsaved-file-item');
                if (!fileNameSpan.textContent.endsWith(' *')) { // Add asterisk only if not already present
                    fileNameSpan.textContent = originalFileName + ' *';
                }
            } else {
                item.classList.remove('unsaved-file-item');
                fileNameSpan.textContent = originalFileName; // Ensure no asterisk
            }
        }
    });
}

// --- Event Listeners ---

// This listener waits for HTMX to finish swapping content onto the page.
// It's the key to initializing the editor at the right time.
document.body.addEventListener('htmx:afterSwap', function (event) {
	// Check if the editor container is now present in the DOM
	const editorContainer = document.getElementById('codemirror-container');

	if (editorContainer) {
		// If it exists, initialize the editor
		initEditor();
		initResizer();
		initDebugTerminalResizer(); // Initialize the debug terminal resizer

		// We also attach listeners for buttons that only exist on the editor page
		const saveBtn = document.getElementById('save-file-btn');
		if (saveBtn) {
			saveBtn.addEventListener('click', saveFile);
		}

		const refreshBtn = document.getElementById('refresh-preview-btn');
		if (refreshBtn) {
			refreshBtn.addEventListener('click', refreshPreview);
		}

		const toggleBtn = document.getElementById('toggle-preview-btn');
		if (toggleBtn) {
			toggleBtn.addEventListener('click', togglePreview);
		}

		const themeSelector = document.getElementById('theme-selector');
		if (themeSelector) {
			themeSelector.addEventListener('change', function() {
				const theme = this.value;
				// Set CodeMirror theme
				editor.setOption("theme", theme);
				// Set body class for UI theme
				if (theme === 'default') { // 'default' is the CodeMirror theme name for light theme
					document.body.classList.add('theme-light');
				} else {
					document.body.classList.remove('theme-light');
				}
			});
		}

		const toggleDebugBtn = document.getElementById('toggle-debug-terminal-btn');
		if (toggleDebugBtn) {
			toggleDebugBtn.addEventListener('click', toggleDebugTerminal);
		}

		// Initially hide the debug terminal
		const debugTerminal = document.getElementById('debug-terminal');
		if (debugTerminal) {
			debugTerminal.classList.add('hidden');
		}

		// Start polling for game state
		if (gameStateIntervalId) {
			clearInterval(gameStateIntervalId);
		}
		gameStateIntervalId = setInterval(updateGameStateDisplay, 2000); // Update every 2 seconds

        // Ensure UI state is correct after HTMX swap
        updateEditorUI();
	}
});

function toggleDebugTerminal() {
    const debugTerminal = document.getElementById('debug-terminal');
    if (debugTerminal) {
        debugTerminal.classList.toggle('hidden');
    }
}

function updateGameStateDisplay() {
    const display = document.getElementById('game-state-content'); // Target the new content div
    if (!display) return;

    fetch('/api/game-state')
        .then(response => response.json())
        .then(state => {
            display.innerHTML = ''; // Clear previous state
            // Display the raw JSON for now, can be formatted later
            const pre = document.createElement('pre');
            pre.textContent = JSON.stringify(state, null, 2);
            display.appendChild(pre);
        })
        .catch(err => {
            console.error('Error fetching game state:', err);
            display.innerHTML = '<div class="state-item error">Could not load game state.</div>';
        });
}

function togglePreview() {
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.classList.toggle('preview-hidden');
        // Re-initialize resizer to recalculate widths if it's shown again
        if (!mainContent.classList.contains('preview-hidden')) {
            initResizer();
        }
    }
}

function switchTab(clickedTab) {
    // Remove active class from all tabs
    document.querySelectorAll('.sidebar-tab').forEach(tab => tab.classList.remove('active'));
    // Add active class to the clicked tab
    clickedTab.classList.add('active');
}