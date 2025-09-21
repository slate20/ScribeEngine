// Global state for the editor
let editor;
let unsavedFiles = new Set(); // To track files with unsaved changes
let currentProject = null;
let currentFile = null;
let gameStateIntervalId = null; // Global variable to store the interval ID
let ignoreNextChange = false; // Flag to ignore programmatic changes

// Tab management system
class TabManager {
    constructor() {
        this.tabs = new Map(); // filename -> {content, isDirty, element, originalContent}
        this.activeTab = null;
        this.maxTabs = 15; // Prevent too many tabs
        this.tabContainer = null;
    }

    initialize() {
        this.tabContainer = document.getElementById('editor-tabs');
        if (!this.tabContainer) {
            console.error('Tab container not found');
            return false;
        }
        return true;
    }

    hasTab(filename) {
        return this.tabs.has(filename);
    }

    getTab(filename) {
        return this.tabs.get(filename);
    }

    getActiveTab() {
        return this.activeTab ? this.tabs.get(this.activeTab) : null;
    }

    getAllTabs() {
        return Array.from(this.tabs.keys());
    }

    getTabCount() {
        return this.tabs.size;
    }

    canAddTab() {
        return this.tabs.size < this.maxTabs;
    }

    addTab(filename, content = '') {
        if (!this.canAddTab()) {
            showNotification(`Maximum ${this.maxTabs} tabs allowed`, 'warning');
            return false;
        }

        if (this.hasTab(filename)) {
            this.switchToTab(filename);
            return true;
        }

        const tab = {
            content: content,
            originalContent: content,
            isDirty: false,
            element: null
        };

        this.tabs.set(filename, tab);
        this.createTabElement(filename);
        this.updateTabsVisibility();
        this.switchToTab(filename);

        return true;
    }

    removeTab(filename, force = false) {
        const tab = this.getTab(filename);
        if (!tab) return true;

        // Check for unsaved changes
        if (tab.isDirty && !force) {
            const shouldSave = confirm(`File "${filename}" has unsaved changes. Close anyway?`);
            if (!shouldSave) return false;
        }

        // Remove from unsaved files tracking
        unsavedFiles.delete(filename);

        // Remove tab element
        if (tab.element) {
            tab.element.remove();
        }

        const wasActive = this.activeTab === filename;
        this.tabs.delete(filename);

        // Switch to another tab if this was active
        if (wasActive) {
            const remainingTabs = this.getAllTabs();
            if (remainingTabs.length > 0) {
                // Switch to the last tab in the list
                this.switchToTab(remainingTabs[remainingTabs.length - 1]);
            } else {
                // No tabs left, clear editor
                this.activeTab = null;
                this.clearEditor();
            }
        }

        this.updateTabsVisibility();
        return true;
    }

    switchToTab(filename) {
        const tab = this.getTab(filename);
        if (!tab) return false;

        // Update active tab styling
        this.updateActiveTabStyling(filename);

        // Update editor content
        ignoreNextChange = true;
        editor.setValue(tab.content);
        editor.setOption("readOnly", false);

        // Update global state
        this.activeTab = filename;
        currentFile = filename;

        // Update UI
        this.updateEditorTitle();
        this.updateSaveButtonState();
        this.updateFileListActiveState();

        // Set syntax highlighting
        this.updateSyntaxHighlighting(filename);

        return true;
    }

    updateTabContent(filename, content) {
        const tab = this.getTab(filename);
        if (!tab) return;

        tab.content = content;
        tab.isDirty = content !== tab.originalContent;

        // Update unsaved files tracking
        if (tab.isDirty) {
            unsavedFiles.add(filename);
        } else {
            unsavedFiles.delete(filename);
        }

        this.updateTabElement(filename);
        this.updateSaveButtonState();
    }

    markTabSaved(filename) {
        const tab = this.getTab(filename);
        if (!tab) return;

        tab.originalContent = tab.content;
        tab.isDirty = false;
        unsavedFiles.delete(filename);

        this.updateTabElement(filename);
        this.updateSaveButtonState();
    }

    createTabElement(filename) {
        const tab = this.getTab(filename);
        if (!tab) return;

        const tabElement = document.createElement('div');
        tabElement.className = 'editor-tab';
        tabElement.setAttribute('data-filename', filename);

        const displayName = filename.length > 20 ? '...' + filename.slice(-17) : filename;

        tabElement.innerHTML = `
            <span class="tab-name">${displayName}</span>
            <button class="tab-close" title="Close tab">
                <i data-lucide="x"></i>
            </button>
        `;

        // Add event listeners
        tabElement.addEventListener('click', (e) => {
            if (!e.target.closest('.tab-close')) {
                this.switchToTab(filename);
            }
        });

        const closeBtn = tabElement.querySelector('.tab-close');
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.removeTab(filename);
        });

        // Add right-click context menu
        tabElement.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.showTabContextMenu(e, filename);
        });

        this.tabContainer.appendChild(tabElement);
        tab.element = tabElement;

        // Initialize Lucide icons for the new tab
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    updateTabElement(filename) {
        const tab = this.getTab(filename);
        if (!tab || !tab.element) return;

        const tabElement = tab.element;
        const nameSpan = tabElement.querySelector('.tab-name');

        let displayName = filename.length > 20 ? '...' + filename.slice(-17) : filename;
        if (tab.isDirty) {
            displayName += ' *';
        }

        nameSpan.textContent = displayName;

        // Update tab styling
        if (tab.isDirty) {
            tabElement.classList.add('unsaved');
        } else {
            tabElement.classList.remove('unsaved');
        }
    }

    updateActiveTabStyling(activeFilename) {
        // Remove active class from all tabs
        const allTabs = this.tabContainer.querySelectorAll('.editor-tab');
        allTabs.forEach(tab => tab.classList.remove('active'));

        // Add active class to current tab
        const activeTab = this.tabContainer.querySelector(`[data-filename="${activeFilename}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }
    }

    updateTabsVisibility() {
        if (!this.tabContainer) return;

        if (this.getTabCount() > 0) {
            this.tabContainer.style.display = 'flex';
        } else {
            this.tabContainer.style.display = 'none';
        }
    }

    clearEditor() {
        ignoreNextChange = true;
        editor.setValue("// Select a file from the list to begin editing.");
        editor.setOption("readOnly", true);
        currentFile = null;
        this.updateEditorTitle();
        this.updateSaveButtonState();
    }

    updateEditorTitle() {
        const editorFileTitle = document.getElementById('editor-file-title');
        if (!editorFileTitle) return;

        if (this.activeTab) {
            const tab = this.getTab(this.activeTab);
            let titleText = this.activeTab;
            if (tab && tab.isDirty) {
                titleText += ' *';
            }
            editorFileTitle.textContent = titleText;
        } else {
            editorFileTitle.textContent = 'No file open';
        }
    }

    updateSaveButtonState() {
        const saveBtn = document.getElementById('save-file-btn');
        if (!saveBtn) return;

        const activeTab = this.getActiveTab();
        if (activeTab && activeTab.isDirty) {
            saveBtn.classList.add('unsaved-changes');
        } else {
            saveBtn.classList.remove('unsaved-changes');
        }
    }

    updateFileListActiveState() {
        // Remove active class from all file items
        document.querySelectorAll('.file-item').forEach(item => item.classList.remove('active'));

        // Add active class to current file
        if (this.activeTab) {
            const activeItem = document.querySelector(`[data-filepath="${this.activeTab}"]`);
            if (activeItem) {
                activeItem.classList.add('active');
            }
        }
    }

    updateSyntaxHighlighting(filename) {
        if (!editor) return;

        let mode = 'scribe'; // Default for .tgame
        if (filename.endsWith('.py')) {
            mode = 'python';
        } else if (filename.endsWith('.json')) {
            mode = { name: 'javascript', json: true };
        } else if (filename.endsWith('.css')) {
            mode = 'css';
        }
        editor.setOption("mode", mode);
    }

    closeAllTabs() {
        const allTabs = this.getAllTabs();
        for (const filename of allTabs) {
            if (!this.removeTab(filename)) {
                // If user cancels closing a dirty tab, stop
                break;
            }
        }
    }

    closeOtherTabs(keepFilename) {
        const allTabs = this.getAllTabs();
        for (const filename of allTabs) {
            if (filename !== keepFilename) {
                if (!this.removeTab(filename)) {
                    // If user cancels closing a dirty tab, stop
                    break;
                }
            }
        }
    }

    showTabContextMenu(event, filename) {
        // Remove any existing context menu
        this.hideTabContextMenu();

        const contextMenu = document.createElement('div');
        contextMenu.className = 'tab-context-menu';
        contextMenu.style.position = 'fixed';
        contextMenu.style.left = event.clientX + 'px';
        contextMenu.style.top = event.clientY + 'px';
        contextMenu.style.zIndex = '1000';
        contextMenu.style.background = 'var(--secondary-bg)';
        contextMenu.style.border = '1px solid var(--border-color)';
        contextMenu.style.borderRadius = '6px';
        contextMenu.style.padding = '4px 0';
        contextMenu.style.minWidth = '150px';
        contextMenu.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.3)';

        const menuItems = [
            {
                text: 'Close Tab',
                action: () => this.removeTab(filename)
            },
            {
                text: 'Close Other Tabs',
                action: () => this.closeOtherTabs(filename),
                disabled: this.getTabCount() <= 1
            },
            {
                text: 'Close All Tabs',
                action: () => this.closeAllTabs(),
                disabled: this.getTabCount() === 0
            }
        ];

        menuItems.forEach(item => {
            const menuItem = document.createElement('div');
            menuItem.className = 'tab-context-menu-item';
            menuItem.textContent = item.text;
            menuItem.style.padding = '8px 16px';
            menuItem.style.cursor = item.disabled ? 'not-allowed' : 'pointer';
            menuItem.style.color = item.disabled ? 'var(--text-muted)' : 'var(--text-primary)';

            if (!item.disabled) {
                menuItem.addEventListener('click', () => {
                    item.action();
                    this.hideTabContextMenu();
                });

                menuItem.addEventListener('mouseenter', () => {
                    menuItem.style.background = 'var(--tertiary-bg)';
                });

                menuItem.addEventListener('mouseleave', () => {
                    menuItem.style.background = 'transparent';
                });
            }

            contextMenu.appendChild(menuItem);
        });

        document.body.appendChild(contextMenu);

        // Hide context menu when clicking elsewhere
        const hideOnClick = (e) => {
            if (!contextMenu.contains(e.target)) {
                this.hideTabContextMenu();
                document.removeEventListener('click', hideOnClick);
            }
        };

        setTimeout(() => {
            document.addEventListener('click', hideOnClick);
        }, 0);
    }

    hideTabContextMenu() {
        const existingMenu = document.querySelector('.tab-context-menu');
        if (existingMenu) {
            existingMenu.remove();
        }
    }
}

// Global tab manager instance
let tabManager = new TabManager();

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

	// Initialize tab manager
	if (!tabManager.initialize()) {
		console.error("Failed to initialize tab manager");
		return;
	}

	editor = CodeMirror(container, {
		value: "// Select a file from the list to begin editing.",
		mode: 'null',
		theme: 'material-darker',
		lineNumbers: true,
		autoCloseBrackets: true,
		readOnly: true, // Start as read-only until a file is opened
		lineWrapping: true, // Enable word wrapping
		extraKeys: {
			"Ctrl-S": function (cm) {
				saveFile();
			},
			"' '": function(cm) {
				const pos = cm.getCursor();
				const textBeforeBlock = cm.getRange({line: pos.line, ch: pos.ch - 3}, pos);
				const textBeforeInline = cm.getRange({line: pos.line, ch: pos.ch - 2}, pos);

				// First, check for the more specific "block" case: '{$ -'
				if (textBeforeBlock === '{$-') {
					// The user typed '{$ -' then space. Replace it all with a block.
					// We replace from 4 chars back (to include '{$ -') up to the cursor (to include the space)
					const textAfter = cm.getRange(pos, {line: pos.line, ch: pos.ch + 1});
					const from = {line: pos.line, ch: pos.ch - 3};
					const to = (textAfter === '}') ? {line: pos.line, ch: pos.ch + 1} : pos;
					cm.replaceRange('{$-\n\n-$}', from, to);

					// Move cursor to the new empty line
					cm.setCursor({line: pos.line + 1, ch: 0});
					// cm.execCommand("indentAuto");
					return;
				
				// Next, check for the "inline" case: '{$'
				} else if (textBeforeInline === '{$') {
					// The user typed '{$' then space. Replace it all with an inline block.
					// We replace from 3 chars back (to include '{$') up to the cursor (to include the space)
					const textAfter = cm.getRange(pos, {line: pos.line, ch: pos.ch + 1});
					const from = {line: pos.line, ch: pos.ch - 2};
					const to = (textAfter === '}') ? {line: pos.line, ch: pos.ch + 1} : pos;
					cm.replaceRange('{$  $}', from, to);
					
					// Move cursor into the middle
					cm.setCursor({line: pos.line, ch: pos.ch + 1});
					return;

				} else if (textBeforeInline === '{%') {
                    // The user typed '{%' then space. Replace it all with an inline block.
                    // We replace from 3 chars back (to include '{%') up to the cursor (to include the space)
                    const textAfter = cm.getRange(pos, {line: pos.line, ch: pos.ch + 1});
                    const from = {line: pos.line, ch: pos.ch - 2};
                    const to = (textAfter === '}') ? {line: pos.line, ch: pos.ch + 1} : pos;
                    cm.replaceRange('{%  %}', from, to);
                    
                    // Move cursor into the middle
                    cm.setCursor({line: pos.line, ch: pos.ch + 1});
                    return;
				}
				
				// If no case is matched, let CodeMirror insert a normal space
				return CodeMirror.Pass;
			},
			"Enter": function(cm) {
                const pos = cm.getCursor();
                const textBeforeBlock = cm.getRange({line: pos.line, ch: pos.ch - 3}, pos);
                if (textBeforeBlock === '{$-') {
                    // The user typed '{$ -' then enter. Replace it with a block.
                    // We replace from 4 chars back (to include '{$ -') up to the cursor (to include the enter)
					const textAfter = cm.getRange(pos, {line: pos.line, ch: pos.ch + 1});
                    const from = {line: pos.line, ch: pos.ch - 3};
                    const to = (textAfter === '}') ? {line: pos.line, ch: pos.ch + 1} : pos;
                    cm.replaceRange('{$-\n\n-$}', from, to);

                    // Move cursor to the new empty line
                    cm.setCursor({line: pos.line + 1, ch: 0});
                    // cm.execCommand("indentAuto");
                    return;
                }

                // If case did not match, let CodeMirror insert a normal enter
                return CodeMirror.Pass;
			},
			"Ctrl-W": function(cm) {
				// Close current tab
				if (currentFile) {
					tabManager.removeTab(currentFile);
				}
			},
			"Ctrl-Tab": function(cm) {
				// Switch to next tab
				const tabs = tabManager.getAllTabs();
				if (tabs.length > 1) {
					const currentIndex = tabs.indexOf(currentFile);
					const nextIndex = (currentIndex + 1) % tabs.length;
					tabManager.switchToTab(tabs[nextIndex]);
				}
			},
			"Ctrl-Shift-Tab": function(cm) {
				// Switch to previous tab
				const tabs = tabManager.getAllTabs();
				if (tabs.length > 1) {
					const currentIndex = tabs.indexOf(currentFile);
					const prevIndex = currentIndex === 0 ? tabs.length - 1 : currentIndex - 1;
					tabManager.switchToTab(tabs[prevIndex]);
				}
			},
			"Ctrl-Shift-T": function(cm) {
				// Show notification about recently closed tabs (placeholder for future feature)
				showNotification('Recently closed tabs feature coming soon!', 'info');
			}
		}
	});

	editor.on('change', function() {
		if (ignoreNextChange) {
			ignoreNextChange = false; // Reset the flag
			return; // Ignore this change
		}
		if (currentFile && !editor.getOption("readOnly")) {
			// Update tab content and dirty state
			tabManager.updateTabContent(currentFile, editor.getValue());
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

	// Store current project
	currentProject = projectName;

	// Check if file is already open in a tab
	if (tabManager.hasTab(fileName)) {
		// Switch to existing tab
		tabManager.switchToTab(fileName);
		return;
	}

	// Load file content and create new tab
	fetch(`/api/get-file-content/${projectName}/${fileName}`)
		.then(response => response.json())
		.then(data => {
			if (data.status === 'success') {
				// Add new tab with file content
				tabManager.addTab(fileName, data.content);
				updateEditorUI(); // Call updateEditorUI after file is loaded
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
async function saveFile() {
	if (!currentProject || !currentFile || !editor || editor.getOption("readOnly")) {
		showNotification('No file is open to save.', 'warning');
		return;
	}

	const content = editor.getValue();

	// Capture game state before saving file
	try {
		const gameStateResponse = await fetch('/api/game-state');
		const currentGameState = await gameStateResponse.json();

		// Send game state to a temporary storage endpoint on the backend
		await fetch('/api/set-temp-game-state', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(currentGameState)
		});
	} catch (error) {
		console.error('Error capturing or sending game state:', error);
		showNotification('Could not capture game state.', 'error');
		// Decide if you want to proceed with file save even if state capture fails
		// For now, we'll proceed, but a more robust solution might stop here.
	}

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
				// Mark tab as saved and update UI
				tabManager.markTabSaved(currentFile);
				updateEditorUI(); // Update UI after save
				// Refresh the preview iframe after a successful save
				if (data.passage_html) {
					const iframeDoc = document.getElementById('preview-iframe').contentWindow.document;
					const gameContentDiv = iframeDoc.getElementById('game-content');
					gameContentDiv.innerHTML = data.passage_html;
					// Re-process HTMX on the newly loaded content within the iframe
					if (iframeDoc.defaultView.htmx) { // Check if htmx is available in the iframe's context
						iframeDoc.defaultView.htmx.process(gameContentDiv);
					}
				} else {
					refreshPreview();
				}
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
 * Reloads the content of the preview iframe, preserving the current passage.
 */
async function refreshPreview() {
	const iframe = document.getElementById('preview-iframe');
	if (!iframe) {
		showNotification('Preview iframe not found.', 'error');
		return;
	}

	try {
		// Fetch current game state to get the current passage
		const gameStateResponse = await fetch('/api/game-state');
		const gameState = await gameStateResponse.json();
		const currentPassage = gameState.current_passage || 'start';

		// Reload iframe with full context
		iframe.src = `/`;
		
		// Wait for iframe to load, then navigate to current passage
		iframe.onload = function() {
			try {
				const iframeDoc = iframe.contentWindow.document;
				const gameContentDiv = iframeDoc.getElementById('game-content');
				
				if (gameContentDiv && iframe.contentWindow.htmx) {
					// Use HTMX to load the current passage into the game-content div
					iframe.contentWindow.htmx.ajax('GET', `/passage/${currentPassage}`, {
						target: '#game-content',
						swap: 'innerHTML'
					});
				} else {
					console.warn('HTMX or game-content div not found in iframe');
				}
			} catch (error) {
				console.error('Error navigating to current passage in iframe:', error);
			}
		};

		showNotification('Preview refreshed!', 'info');

	} catch (error) {
		console.error('Error fetching game state for refresh:', error);
		// Fallback to simple reload
		iframe.src = `/`;
		showNotification('Preview refreshed (fallback to start)!', 'warning');
	}
}

/**
 * Displays a temporary notification on the screen.
 * @param {string} message - The message to display.
 * @param {string} type - The type of notification ('success', 'error', 'warning', 'info').
 */
function showNotification(message, type = 'info') {
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        document.body.appendChild(container);
    }

	const notification = document.createElement('div');
    notification.className = 'notification';
	const colors = {
		success: 'var(--success-color)',
		error: 'var(--danger-color)',
		warning: 'var(--warning-color)',
		info: 'var(--accent-color)'
	};

    notification.style.background = colors[type] || colors.info;
	notification.textContent = message;
	container.appendChild(notification);

	setTimeout(() => {
		notification.style.opacity = '1';
		notification.style.transform = 'translateX(0)';
	}, 10);

	setTimeout(() => {
		notification.style.opacity = '0';
		notification.style.transform = 'translateX(20px)';
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

	// Set initial panel sizes only if they haven't been set already (to prevent modal-triggered resets)
	const hasCustomWidths = leftPanel.style.width && rightPanel.style.width;
	if (!hasCustomWidths) {
		const sidebarWidth = document.querySelector('.sidebar').offsetWidth;
		const availableWidth = container.offsetWidth - sidebarWidth - handle.offsetWidth;
		leftPanel.style.width = `${availableWidth * 0.50}px`;
		rightPanel.style.width = `${availableWidth * 0.50}px`;
	}

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
	// Skip initialization if this is a modal-related swap to prevent preview panel resizing
	if (event.target && event.target.id === 'modal-container') {
		return;
	}

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


		// Theme toggle functionality
		function toggleTheme() {
			const currentTheme = editor.getOption("theme");
			const isLight = currentTheme === 'default';
			const newTheme = isLight ? 'material-darker' : 'default';
			const themeIcon = document.getElementById('theme-icon');
			
			// Set CodeMirror theme
			editor.setOption("theme", newTheme);
			
			// Set body class for UI theme
			if (newTheme === 'default') {
				document.body.classList.add('theme-light');
				themeIcon.setAttribute('data-lucide', 'sun');
			} else {
				document.body.classList.remove('theme-light');
				themeIcon.setAttribute('data-lucide', 'moon');
			}
			
			// Refresh lucide icons
			if (typeof lucide !== 'undefined') {
				lucide.createIcons();
			}
		}

		const themeToggleBtn = document.getElementById('theme-toggle-btn');
		if (themeToggleBtn) {
			themeToggleBtn.addEventListener('click', toggleTheme);
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

		const fontSizeSelector = document.getElementById('font-size-selector');
		if (fontSizeSelector) {
			fontSizeSelector.addEventListener('change', function() {
				document.documentElement.style.setProperty('--editor-font-size', this.value);
			});
			// Set initial font size based on the selected value
			document.documentElement.style.setProperty('--editor-font-size', fontSizeSelector.value);
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
		gameStateIntervalId = setInterval(updateGameStateDisplay, 500); // Update every 500ms

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

// File Explorer Collapse/Expand Functionality
function toggleSection(sectionId) {
    const header = document.querySelector(`[data-section="${sectionId}"]`);
    const section = document.getElementById(`${sectionId}-section`);

    if (!header || !section) return;

    const isCollapsed = section.classList.contains('collapsed');
    const icon = header.querySelector('.collapse-icon');

    if (isCollapsed) {
        // Expand
        section.classList.remove('collapsed');
        header.classList.remove('collapsed');
        header.setAttribute('aria-expanded', 'true');
        if (icon) icon.setAttribute('data-lucide', 'chevron-down');
    } else {
        // Collapse
        section.classList.add('collapsed');
        header.classList.add('collapsed');
        header.setAttribute('aria-expanded', 'false');
        if (icon) icon.setAttribute('data-lucide', 'chevron-right');
    }

    // Re-initialize Lucide icons for the changed icon
    if (window.lucide) {
        lucide.createIcons();
    }

    // Save state to localStorage
    saveSectionState(sectionId, !isCollapsed);
}

function toggleGroup(groupId) {
    const header = document.querySelector(`[data-group="${groupId}"]`);
    const groupFiles = document.getElementById(`${groupId}-files`);

    if (!header || !groupFiles) return;

    const isCollapsed = groupFiles.classList.contains('collapsed');
    const icon = header.querySelector('.collapse-icon');

    if (isCollapsed) {
        // Expand
        groupFiles.classList.remove('collapsed');
        header.classList.remove('collapsed');
        header.setAttribute('aria-expanded', 'true');
        if (icon) icon.setAttribute('data-lucide', 'chevron-down');
    } else {
        // Collapse
        groupFiles.classList.add('collapsed');
        header.classList.add('collapsed');
        header.setAttribute('aria-expanded', 'false');
        if (icon) icon.setAttribute('data-lucide', 'chevron-right');
    }

    // Re-initialize Lucide icons for the changed icon
    if (window.lucide) {
        lucide.createIcons();
    }

    // Save state to localStorage
    saveGroupState(groupId, !isCollapsed);
}

// LocalStorage state management
function getCollapseStateKey() {
    return `fileExplorer_${currentProject || 'default'}_collapseState`;
}

function saveSectionState(sectionId, isCollapsed) {
    const stateKey = getCollapseStateKey();
    let state = JSON.parse(localStorage.getItem(stateKey) || '{}');

    if (!state.sections) state.sections = {};
    state.sections[sectionId] = isCollapsed;

    localStorage.setItem(stateKey, JSON.stringify(state));
}

function saveGroupState(groupId, isCollapsed) {
    const stateKey = getCollapseStateKey();
    let state = JSON.parse(localStorage.getItem(stateKey) || '{}');

    if (!state.groups) state.groups = {};
    state.groups[groupId] = isCollapsed;

    localStorage.setItem(stateKey, JSON.stringify(state));
}

function loadCollapseState() {
    const stateKey = getCollapseStateKey();
    const state = JSON.parse(localStorage.getItem(stateKey) || '{}');

    // Restore section states
    if (state.sections) {
        Object.entries(state.sections).forEach(([sectionId, isCollapsed]) => {
            if (isCollapsed) {
                const header = document.querySelector(`[data-section="${sectionId}"]`);
                const section = document.getElementById(`${sectionId}-section`);
                const icon = header?.querySelector('.collapse-icon');

                if (header && section) {
                    section.classList.add('collapsed');
                    header.classList.add('collapsed');
                    header.setAttribute('aria-expanded', 'false');
                    if (icon) icon.setAttribute('data-lucide', 'chevron-right');
                }
            }
        });
    }

    // Restore group states
    if (state.groups) {
        Object.entries(state.groups).forEach(([groupId, isCollapsed]) => {
            if (isCollapsed) {
                const header = document.querySelector(`[data-group="${groupId}"]`);
                const groupFiles = document.getElementById(`${groupId}-files`);
                const icon = header?.querySelector('.collapse-icon');

                if (header && groupFiles) {
                    groupFiles.classList.add('collapsed');
                    header.classList.add('collapsed');
                    header.setAttribute('aria-expanded', 'false');
                    if (icon) icon.setAttribute('data-lucide', 'chevron-right');
                }
            }
        });
    }

    // Re-initialize Lucide icons after state restoration
    if (window.lucide) {
        lucide.createIcons();
    }
}

// Keyboard support for collapsible headers
document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' || event.key === ' ') {
        const target = event.target;

        if (target.classList.contains('collapsible-header')) {
            event.preventDefault();

            const sectionId = target.getAttribute('data-section');
            const groupId = target.getAttribute('data-group');

            if (sectionId) {
                toggleSection(sectionId);
            } else if (groupId) {
                toggleGroup(groupId);
            }
        }
    }
});

// Load collapse state when file list loads
document.addEventListener('htmx:afterSwap', function(event) {
    if (event.target && event.target.id === 'sidebar-content') {
        // File list has been refreshed, restore collapse state
        setTimeout(loadCollapseState, 50); // Small delay to ensure DOM is ready
    }
});

// Event delegation for project actions dropdown
document.body.addEventListener('click', function(event) {
    const projectActionsBtn = document.getElementById('project-actions-btn');
    const projectActionsDropdown = document.getElementById('project-actions-dropdown');

    if (!projectActionsBtn || !projectActionsDropdown) return; // Elements not present

    // If the clicked element is the button itself, toggle the dropdown
    if (projectActionsBtn.contains(event.target)) {
        event.stopPropagation(); // Prevent the click from bubbling up to the window listener
        projectActionsDropdown.classList.toggle('show');
    } else if (!projectActionsDropdown.contains(event.target)) {
        // If the clicked element is not the button and not inside the dropdown, close the dropdown
        projectActionsDropdown.classList.remove('show');
    }
});

// --- pywebview API bridge ---
async function browseForProjectRoot() {
    try {
        const path = await window.pywebview.api.open_folder_dialog();
        if (path) {
            const pathInput = document.getElementById('project-root-path');
            if (pathInput) {
                pathInput.value = path;
            }
        }
    } catch (e) {
        console.error("Error calling pywebview API: ", e);
    }
}

function resetGameState() {
    // Close the dropdown menu
    const projectActionsDropdown = document.getElementById('project-actions-dropdown');
    if (projectActionsDropdown) {
        projectActionsDropdown.classList.remove('show');
    }
    
    fetch('/api/reset-game-state', { method: 'POST' })
        .then(response => {
            showNotification('Game state has been reset.', 'success');
            // Simplified approach: just reload preview iframe to '/'
            const iframe = document.getElementById('preview-iframe');
            if (iframe) {
                iframe.src = '/';
            }
            // Force an immediate update of the debug display
            updateGameStateDisplay();
        })
        .catch(err => {
            console.error('Error resetting game state:', err);
            showNotification('An error occurred while resetting the game state.', 'error');
        });
}

// Build Progress Modal Management
let buildPollingInterval = null;
let buildStartTime = null;
let currentBuildPath = null;

/**
 * Shows the build progress modal
 * @param {string} projectName - Name of the project being built
 */
function showBuildModal(projectName) {
    const modal = document.getElementById('build-progress-modal');
    const projectNameEl = document.getElementById('build-project-name');
    const statusEl = document.getElementById('build-status');
    const elapsedEl = document.getElementById('build-elapsed');
    const spinner = modal.querySelector('.spinner');
    
    // Reset modal state
    projectNameEl.textContent = projectName;
    statusEl.textContent = 'Initializing build...';
    statusEl.className = 'build-status';
    elapsedEl.textContent = '0s';
    spinner.className = 'spinner';
    
    // Reset footer buttons
    document.getElementById('build-cancel-btn').style.display = 'inline-block';
    document.getElementById('build-open-folder-btn').style.display = 'none';
    document.getElementById('build-close-btn').style.display = 'none';
    
    // Show the modal with animation
    modal.style.display = 'flex';
    setTimeout(() => modal.classList.add('show'), 10);
    
    // Record start time for elapsed calculation
    buildStartTime = Date.now();
    currentBuildPath = null;
    
    // Start polling for build status
    startBuildPolling(projectName);
}

/**
 * Updates the build status in the modal
 * @param {string} status - Current build status
 * @param {string} message - Progress message
 * @param {number} elapsedSeconds - Elapsed time in seconds
 */
function updateBuildStatus(status, message, elapsedSeconds) {
    const statusEl = document.getElementById('build-status');
    const elapsedEl = document.getElementById('build-elapsed');
    const spinner = document.querySelector('#build-progress-modal .spinner');
    
    if (statusEl) {
        statusEl.textContent = message;
        
        // Update status styling based on build state
        statusEl.className = 'build-status';
        if (status === 'completed') {
            statusEl.classList.add('success');
            spinner.classList.add('success');
        } else if (status === 'failed') {
            statusEl.classList.add('error');
            spinner.classList.add('error');
        }
    }
    
    if (elapsedEl && elapsedSeconds !== undefined) {
        elapsedEl.textContent = formatElapsedTime(elapsedSeconds);
    }
}

/**
 * Hides the build progress modal
 * @param {boolean} success - Whether the build was successful
 * @param {string} message - Final message to show
 */
function hideBuildModal(success, message) {
    const modal = document.getElementById('build-progress-modal');
    
    // Stop polling
    if (buildPollingInterval) {
        clearInterval(buildPollingInterval);
        buildPollingInterval = null;
    }
    
    // Hide the modal with animation
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
    
    // Show final notification
    if (message) {
        showNotification(message, success ? 'success' : 'error');
    }
}

/**
 * Starts polling the build status API
 * @param {string} projectName - Name of the project being built
 */
function startBuildPolling(projectName) {
    buildPollingInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/build-status/${projectName}`);
            
            if (response.ok) {
                const buildInfo = await response.json();
                const elapsedMs = Date.now() - buildStartTime;
                const elapsedSeconds = Math.floor(elapsedMs / 1000);
                
                updateBuildStatus(buildInfo.status, buildInfo.progress, elapsedSeconds);
                
                // Stop polling if build is complete or failed
                if (buildInfo.status === 'completed') {
                    // Store build path for folder opening
                    currentBuildPath = buildInfo.executable_path;
                    
                    // Add completion animation
                    const progressContainer = document.querySelector('.build-progress-container');
                    progressContainer.classList.add('completed');
                    
                    // Update footer buttons for completion
                    setTimeout(() => {
                        document.getElementById('build-cancel-btn').style.display = 'none';
                        document.getElementById('build-open-folder-btn').style.display = 'inline-block';
                        document.getElementById('build-close-btn').style.display = 'inline-block';
                        lucide.createIcons();
                    }, 1000);
                    
                    // Stop polling
                    if (buildPollingInterval) {
                        clearInterval(buildPollingInterval);
                        buildPollingInterval = null;
                    }
                } else if (buildInfo.status === 'failed') {
                    setTimeout(() => {
                        // Update footer for failure
                        document.getElementById('build-cancel-btn').textContent = 'Close';
                        document.getElementById('build-cancel-btn').onclick = () => hideBuildModal(false, buildInfo.message || 'Build failed');
                    }, 1000);
                    
                    // Stop polling
                    if (buildPollingInterval) {
                        clearInterval(buildPollingInterval);
                        buildPollingInterval = null;
                    }
                }
            } else if (response.status === 404) {
                // Build not found - it may have completed and been cleaned up
                hideBuildModal(true, 'Build may have completed. Check the project dist/ folder.');
            }
        } catch (error) {
            console.error('Error polling build status:', error);
            // Continue polling - network errors are temporary
        }
    }, 2000); // Poll every 2 seconds
}

/**
 * Formats elapsed time in a human-readable format
 * @param {number} seconds - Elapsed time in seconds
 * @returns {string} Formatted time string
 */
function formatElapsedTime(seconds) {
    if (seconds < 60) {
        return `${seconds}s`;
    } else {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds}s`;
    }
}

/**
 * Opens the build output folder using the system's file manager
 */
function openBuildFolder() {
    if (currentBuildPath) {
        showNotification(`Build folder: ${currentBuildPath}`, 'success');
        // In a desktop app, we could use:
        // window.pywebview.api.open_folder(currentBuildPath)
        // For now, just show the path
    } else {
        showNotification('Build path not available', 'error');
    }
}

/**
 * Starts the build process and shows the progress modal
 * @param {string} projectName - Name of the project to build
 */
async function startBuild(projectName) {
    const buildBtn = document.getElementById('build-btn');
    
    try {
        // Disable build button during request
        buildBtn.disabled = true;
        buildBtn.innerHTML = '<i data-lucide="loader-2"></i> Starting...';
        lucide.createIcons();
        
        // Start the build
        const response = await fetch(`/api/build-game/${projectName}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            // Show build modal and start monitoring
            showBuildModal(projectName);
        } else {
            // Show error notification
            showNotification(result.message || 'Failed to start build', 'error');
        }
    } catch (error) {
        console.error('Error starting build:', error);
        showNotification('Network error: Could not start build', 'error');
    } finally {
        // Re-enable build button
        setTimeout(() => {
            buildBtn.disabled = false;
            buildBtn.innerHTML = '<i data-lucide="package"></i> Build';
            lucide.createIcons();
        }, 2000);
    }
}

/**
 * Copies asset path to clipboard using textarea method (pywebview compatible)
 * @param {string} assetPath - The asset file path relative to assets folder
 */
function copyAssetPath(assetPath) {
    const fullPath = `game/${assetPath}`;

    // Create a temporary textarea element for copying
    const textarea = document.createElement('textarea');
    textarea.value = fullPath;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);

    try {
        textarea.select();
        textarea.setSelectionRange(0, textarea.value.length);
        const success = document.execCommand('copy');

        if (success) {
            showNotification(`Copied: ${fullPath}`, 'success');
        } else {
            showNotification('Failed to copy to clipboard', 'error');
        }
    } catch (error) {
        console.error('Copy failed:', error);
        showNotification('Failed to copy to clipboard', 'error');
    } finally {
        document.body.removeChild(textarea);
    }
}

// Color Picker Functions
function openColorPickerModal() {
    const modal = document.getElementById('color-picker-modal');
    const colorInput = document.getElementById('color-input');

    if (!modal) {
        console.error('Color picker modal not found');
        return;
    }

    modal.style.display = 'flex';
    modal.classList.add('show');

    // Initialize color picker with default color
    updateColorDisplay(colorInput.value);

    // Remove any existing event listeners to prevent duplicates
    const newColorInput = colorInput.cloneNode(true);
    colorInput.parentNode.replaceChild(newColorInput, colorInput);

    // Add event listener for color changes
    newColorInput.addEventListener('input', function() {
        updateColorDisplay(this.value);
    });
}

function closeColorPickerModal() {
    const modal = document.getElementById('color-picker-modal');
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

function updateColorDisplay(hexColor) {
    const hexValue = document.getElementById('hex-value');
    const rgbValue = document.getElementById('rgb-value');
    const hslValue = document.getElementById('hsl-value');
    const colorSwatch = document.getElementById('color-swatch');

    // Update hex value
    hexValue.textContent = hexColor.toUpperCase();

    // Convert to RGB
    const rgb = hexToRgb(hexColor);
    rgbValue.textContent = `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;

    // Convert to HSL
    const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b);
    hslValue.textContent = `hsl(${hsl.h}, ${hsl.s}%, ${hsl.l}%)`;

    // Update color swatch
    colorSwatch.style.backgroundColor = hexColor;
}

function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

function rgbToHsl(r, g, b) {
    r /= 255;
    g /= 255;
    b /= 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
        h = s = 0; // Achromatic
    } else {
        const d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

        switch (max) {
            case r: h = (g - b) / d + (g < b ? 6 : 0); break;
            case g: h = (b - r) / d + 2; break;
            case b: h = (r - g) / d + 4; break;
        }
        h /= 6;
    }

    return {
        h: Math.round(h * 360),
        s: Math.round(s * 100),
        l: Math.round(l * 100)
    };
}

function copyColorValue(format) {
    let value;
    let button;

    switch (format) {
        case 'hex':
            value = document.getElementById('hex-value').textContent;
            button = document.querySelector('.color-format-row:nth-child(1) .copy-btn');
            break;
        case 'rgb':
            value = document.getElementById('rgb-value').textContent;
            button = document.querySelector('.color-format-row:nth-child(2) .copy-btn');
            break;
        case 'hsl':
            value = document.getElementById('hsl-value').textContent;
            button = document.querySelector('.color-format-row:nth-child(3) .copy-btn');
            break;
    }

    if (value && button) {
        // Create a temporary textarea element for copying
        const textarea = document.createElement('textarea');
        textarea.value = value;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);

        try {
            textarea.select();
            textarea.setSelectionRange(0, textarea.value.length);
            const success = document.execCommand('copy');

            if (success) {
                // Show copy feedback
                button.classList.add('copied');
                const originalIcon = button.innerHTML;
                button.innerHTML = '<i data-lucide="check"></i>';
                lucide.createIcons();

                setTimeout(() => {
                    button.classList.remove('copied');
                    button.innerHTML = originalIcon;
                    lucide.createIcons();
                }, 1500);

                showNotification(`Copied: ${value}`, 'success');
            } else {
                showNotification('Failed to copy to clipboard', 'error');
            }
        } catch (error) {
            console.error('Copy failed:', error);
            showNotification('Failed to copy to clipboard', 'error');
        } finally {
            document.body.removeChild(textarea);
        }
    }
}

// Initialize color picker button event listener when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Use event delegation since the button might be added dynamically
    document.addEventListener('click', function(e) {
        // Check if the clicked element is the color picker button or a child of it
        const colorPickerBtn = e.target.closest('#color-picker-btn');
        if (colorPickerBtn) {
            e.preventDefault();
            openColorPickerModal();
        }
    });

    // Close modal when clicking outside
    document.addEventListener('click', function(e) {
        const modal = document.getElementById('color-picker-modal');
        if (modal && e.target === modal) {
            closeColorPickerModal();
        }
    });
});
