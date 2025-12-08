/**
 * ScribeEngine IDE - Main JavaScript
 */

// Global state
const IDE = {
    editor: null,
    currentFile: null,
    openFiles: new Map(), // filepath -> {content, modified, language}
    fileTree: null,
    monaco: null,
    editorReady: false,
    pendingFileSwitch: null
};

// Initialize IDE when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('IDE: DOM loaded, initializing...');

    // Initialize event listeners first (they don't depend on Monaco)
    initEventListeners();

    // Load data immediately
    loadFileTree();
    loadRoutes();
    loadDatabaseTables();
    updateProjectName();

    // Initialize Monaco Editor (this may take time to load from CDN)
    initMonacoEditor();

    console.log('IDE: Initialization complete');
});

/**
 * Initialize Monaco Editor
 */
function initMonacoEditor() {
    console.log('IDE: Loading Monaco Editor...');

    // Check if require is available
    if (typeof require === 'undefined') {
        console.error('IDE: RequireJS not loaded! Monaco Editor cannot initialize.');
        console.error('IDE: Falling back to simple text editor');
        setStatus('Error: RequireJS not loaded, using fallback editor', 'error');
        useFallbackEditor();
        return;
    }

    console.log('IDE: RequireJS is available, configuring paths...');

    // Try to detect which CDN loaded successfully
    const cdnPaths = [
        'https://unpkg.com/monaco-editor@0.45.0/min/vs',
        'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs',
        'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs'
    ];

    require.config({
        paths: {
            vs: cdnPaths[0]  // Use the first one (unpkg)
        }
    });

    console.log('IDE: Requiring Monaco Editor modules...');

    require(['vs/editor/editor.main'], function () {
        console.log('IDE: Monaco Editor modules loaded successfully');
        IDE.monaco = monaco;

        try {
            // Register custom .stpl language
            console.log('IDE: Registering custom language...');
            registerScribeLanguage();
            console.log('IDE: Custom language registered');

            // Create editor instance
            console.log('IDE: Creating editor instance...');
            IDE.editor = monaco.editor.create(document.getElementById('monaco-editor'), {
                theme: 'vs-dark',
                automaticLayout: true,
                minimap: { enabled: true },
                fontSize: 14,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                tabSize: 4,
                insertSpaces: true,
            });
            console.log('IDE: Editor instance created');

            // Track cursor position
            IDE.editor.onDidChangeCursorPosition((e) => {
                updateCursorPosition(e.position);
            });

            // Track content changes
            IDE.editor.onDidChangeModelContent(() => {
                markFileAsModified();
            });

            // Mark as ready
            IDE.editorReady = true;
            console.log('IDE: Monaco Editor initialized and ready');
            setStatus('Editor ready');

            // If there's a pending file switch, do it now
            if (IDE.pendingFileSwitch) {
                console.log('IDE: Processing pending file switch:', IDE.pendingFileSwitch);
                switchToFile(IDE.pendingFileSwitch);
                IDE.pendingFileSwitch = null;
            }
        } catch (error) {
            console.error('IDE: Error during Monaco initialization:', error);
            setStatus('Editor initialization error', 'error');

            // Fall back to simple editor
            useFallbackEditor();
        }
    }, function(err) {
        console.error('IDE: Failed to load Monaco Editor modules:', err);
        console.error('IDE: Error details:', err.requireModules, err.requireType);
        setStatus('Error loading editor', 'error');

        // Fall back to simple editor
        useFallbackEditor();
    });
}

/**
 * Register ScribeEngine template language for Monaco
 */
function registerScribeLanguage() {
    try {
        monaco.languages.register({ id: 'scribe-template' });
        console.log('IDE: Language ID registered');

        // Use a simple, working language definition
        monaco.languages.setMonarchTokensProvider('scribe-template', {
            tokenizer: {
                root: [
                    // Decorators
                    [/@\w+/, 'keyword'],

                    // Python blocks
                    [/\{\$/, 'delimiter'],
                    [/\$\}/, 'delimiter'],

                    // Jinja2
                    [/\{%/, 'delimiter'],
                    [/%\}/, 'delimiter'],
                    [/\{\{/, 'delimiter'],
                    [/\}\}/, 'delimiter'],

                    // Keywords
                    [/\b(if|else|elif|for|while|def|class|return)\b/, 'keyword'],

                    // Strings
                    [/"([^"\\]|\\.)*$/, 'string.invalid'],
                    [/'([^'\\]|\\.)*$/, 'string.invalid'],
                    [/"/, 'string', '@string_double'],
                    [/'/, 'string', '@string_single'],

                    // Comments
                    [/#.*$/, 'comment'],
                    [/<!--/, 'comment', '@html_comment'],
                ],

                string_double: [
                    [/[^\\"]+/, 'string'],
                    [/"/, 'string', '@pop']
                ],

                string_single: [
                    [/[^\\']+/, 'string'],
                    [/'/, 'string', '@pop']
                ],

                html_comment: [
                    [/-->/, 'comment', '@pop'],
                    [/./, 'comment']
                ]
            }
        });
        console.log('IDE: Monarch tokenizer registered');
    } catch (error) {
        console.error('IDE: Error registering language:', error);
        throw error;
    }

    // Auto-completion for .stpl files
    monaco.languages.registerCompletionItemProvider('scribe-template', {
        provideCompletionItems: (model, position) => {
            const suggestions = [
                {
                    label: '@route',
                    kind: monaco.languages.CompletionItemKind.Snippet,
                    insertText: "@route('${1:/path}')\n{$\n\t$0\n$}\n",
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Define a route'
                },
                {
                    label: 'db.find',
                    kind: monaco.languages.CompletionItemKind.Method,
                    insertText: "db.find('${1:table}', ${2:id})",
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Find a record by ID'
                },
                {
                    label: 'db.where',
                    kind: monaco.languages.CompletionItemKind.Method,
                    insertText: "db.where('${1:table}', ${2:column}=${3:value})",
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Find records matching criteria'
                },
                {
                    label: 'db.table',
                    kind: monaco.languages.CompletionItemKind.Method,
                    insertText: "db.table('${1:table}')$0",
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Start a query builder chain'
                },
                {
                    label: 'session',
                    kind: monaco.languages.CompletionItemKind.Variable,
                    insertText: "session['${1:key}']",
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Access session data'
                },
                {
                    label: 'request.form',
                    kind: monaco.languages.CompletionItemKind.Variable,
                    insertText: "request.form.get('${1:name}')",
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Get form data'
                },
            ];

            return { suggestions };
        },
    });
}

/**
 * Initialize event listeners
 */
function initEventListeners() {
    // Save button
    document.getElementById('save-btn').addEventListener('click', saveCurrentFile);

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl+S or Cmd+S to save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            saveCurrentFile();
        }
    });

    // Panel tabs
    document.querySelectorAll('.panel-tab').forEach(tab => {
        tab.addEventListener('click', () => switchPanel(tab.dataset.panel));
    });

    // New file/folder buttons
    document.getElementById('new-file-btn').addEventListener('click', () => showModal('new-file-modal'));
    document.getElementById('new-folder-btn').addEventListener('click', () => showModal('new-folder-modal'));
    document.getElementById('refresh-files-btn').addEventListener('click', loadFileTree);

    // Modal handlers
    document.getElementById('new-file-create-btn').addEventListener('click', createNewFile);
    document.getElementById('new-file-cancel-btn').addEventListener('click', () => hideModal('new-file-modal'));
    document.getElementById('new-folder-create-btn').addEventListener('click', createNewFolder);
    document.getElementById('new-folder-cancel-btn').addEventListener('click', () => hideModal('new-folder-modal'));

    // Preview controls
    document.getElementById('refresh-preview-btn').addEventListener('click', refreshPreview);
    document.getElementById('preview-go-btn').addEventListener('click', loadPreview);
    document.getElementById('preview-url').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loadPreview();
    });

    // Database controls
    document.getElementById('refresh-tables-btn').addEventListener('click', loadDatabaseTables);
    document.getElementById('table-select').addEventListener('change', (e) => {
        if (e.target.value) loadTableData(e.target.value);
    });

    // Resizers
    initResizers();
}

/**
 * Initialize panel resizers
 */
function initResizers() {
    // Sidebar resizer
    const sidebarResizer = document.getElementById('sidebar-resizer');
    const sidebar = document.getElementById('sidebar');

    if (sidebarResizer && sidebar) {
        makeResizable(sidebarResizer, sidebar, 'width', 150, 500);
    }

    // Right panel resizer
    const rightPanelResizer = document.getElementById('right-panel-resizer');
    const rightPanel = document.getElementById('right-panel');

    if (rightPanelResizer && rightPanel) {
        makeResizable(rightPanelResizer, rightPanel, 'width', 300, 800, true);
    }
}

/**
 * Make an element resizable
 */
function makeResizable(resizer, element, property, minSize, maxSize, reverse = false) {
    let startPos = 0;
    let startSize = 0;

    resizer.addEventListener('mousedown', (e) => {
        e.preventDefault();
        startPos = property === 'width' ? e.clientX : e.clientY;
        startSize = parseInt(getComputedStyle(element)[property], 10);

        document.addEventListener('mousemove', resize);
        document.addEventListener('mouseup', stopResize);

        // Add a class to disable text selection during resize
        document.body.style.cursor = property === 'width' ? 'col-resize' : 'row-resize';
        document.body.style.userSelect = 'none';
    });

    function resize(e) {
        const currentPos = property === 'width' ? e.clientX : e.clientY;
        const diff = reverse ? (startPos - currentPos) : (currentPos - startPos);
        let newSize = startSize + diff;

        // Clamp to min/max
        newSize = Math.max(minSize, Math.min(maxSize, newSize));

        element.style[property] = `${newSize}px`;
    }

    function stopResize() {
        document.removeEventListener('mousemove', resize);
        document.removeEventListener('mouseup', stopResize);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
    }
}

/**
 * Load file tree from server
 */
async function loadFileTree() {
    console.log('IDE: Loading file tree...');
    try {
        const response = await fetch('/__scribe_gui/api/files');
        console.log('IDE: File tree response status:', response.status);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('IDE: File tree data:', data);

        IDE.fileTree = data.files;
        renderFileTree();
        setStatus('Files loaded');
    } catch (error) {
        setStatus('Error loading files', 'error');
        console.error('IDE: Error loading file tree:', error);
    }
}

/**
 * Render file tree in sidebar
 */
function renderFileTree() {
    console.log('IDE: Rendering file tree...');
    const container = document.getElementById('file-tree');

    if (!container) {
        console.error('IDE: file-tree container not found!');
        return;
    }

    if (!IDE.fileTree || IDE.fileTree.length === 0) {
        console.warn('IDE: No files to render');
        container.innerHTML = '<div class="loading">No files found</div>';
        return;
    }

    function renderNode(node, level = 0) {
        if (node.type === 'directory') {
            const folderDiv = document.createElement('div');
            folderDiv.className = 'folder-item';
            folderDiv.style.paddingLeft = `${level * 1 + 1}rem`;
            folderDiv.textContent = `📁 ${node.name}`;

            const childrenDiv = document.createElement('div');
            childrenDiv.className = 'folder-children';

            if (node.children) {
                node.children.forEach(child => {
                    const childElement = renderNode(child, level + 1);
                    childrenDiv.appendChild(childElement);
                });
            }

            const wrapper = document.createElement('div');
            wrapper.appendChild(folderDiv);
            wrapper.appendChild(childrenDiv);

            return wrapper;
        } else {
            const fileDiv = document.createElement('div');
            fileDiv.className = 'file-item';
            fileDiv.style.paddingLeft = `${level * 1 + 1}rem`;
            fileDiv.textContent = `📄 ${node.name}`;
            fileDiv.dataset.path = node.path;

            fileDiv.addEventListener('click', () => openFile(node.path));

            return fileDiv;
        }
    }

    container.innerHTML = '';

    try {
        IDE.fileTree.forEach(node => {
            const element = renderNode(node);
            container.appendChild(element);
        });
        console.log(`IDE: Rendered ${IDE.fileTree.length} top-level items`);
    } catch (error) {
        console.error('IDE: Error rendering file tree:', error);
        container.innerHTML = '<div class="loading error">Error rendering files</div>';
    }
}

/**
 * Open a file in the editor
 */
async function openFile(filepath) {
    try {
        // Check if already open
        if (IDE.openFiles.has(filepath)) {
            switchToFile(filepath);
            return;
        }

        const response = await fetch(`/__scribe_gui/api/file/${filepath}`);
        const data = await response.json();

        if (data.error) {
            setStatus(`Error: ${data.error}`, 'error');
            return;
        }

        // Store file info
        IDE.openFiles.set(filepath, {
            content: data.content,
            originalContent: data.content,
            modified: false,
            language: data.language
        });

        // Add tab
        addTab(filepath);

        // Switch to this file
        switchToFile(filepath);

        setStatus(`Opened ${filepath}`);
    } catch (error) {
        setStatus(`Error opening file: ${error.message}`, 'error');
        console.error(error);
    }
}

/**
 * Switch to an already-open file
 */
function switchToFile(filepath, retryCount = 0) {
    console.log(`IDE: Switching to file: ${filepath} (retry: ${retryCount})`);
    IDE.currentFile = filepath;
    const fileInfo = IDE.openFiles.get(filepath);

    if (!fileInfo) {
        console.error(`IDE: File info not found for ${filepath}`);
        return;
    }

    // Check if editor is ready
    if (!IDE.editorReady || !IDE.editor) {
        if (retryCount >= 50) { // Max 5 seconds of retrying
            console.error('IDE: Monaco Editor failed to initialize after 5 seconds');
            setStatus('Editor initialization failed', 'error');
            // Store for later if Monaco eventually loads
            IDE.pendingFileSwitch = filepath;
            return;
        }

        console.warn(`IDE: Monaco Editor not ready yet, waiting... (attempt ${retryCount + 1}/50)`);
        // Store pending switch
        IDE.pendingFileSwitch = filepath;
        // Retry after a short delay
        setTimeout(() => switchToFile(filepath, retryCount + 1), 100);
        return;
    }

    // Clear pending switch since we're processing it now
    IDE.pendingFileSwitch = null;

    // Update editor content and language
    try {
        const model = IDE.editor.getModel();
        if (model) {
            IDE.editor.setValue(fileInfo.content);
            monaco.editor.setModelLanguage(model, fileInfo.language);
        } else {
            const newModel = monaco.editor.createModel(fileInfo.content, fileInfo.language);
            IDE.editor.setModel(newModel);
        }

        // Update UI
        document.getElementById('editor-placeholder').style.display = 'none';
        document.getElementById('monaco-editor').style.display = 'block';

        console.log(`IDE: Editor updated with ${fileInfo.content.length} chars, language: ${fileInfo.language}`);
    } catch (error) {
        console.error('IDE: Error updating editor:', error);
    }

    // Update tabs
    document.querySelectorAll('.editor-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.path === filepath);
    });

    // Update file tree
    document.querySelectorAll('.file-item').forEach(item => {
        item.classList.toggle('active', item.dataset.path === filepath);
    });

    // Update status bar
    document.getElementById('file-language').textContent = fileInfo.language;

    // Enable save button if modified
    document.getElementById('save-btn').disabled = !fileInfo.modified;
}

/**
 * Add a tab for an open file
 */
function addTab(filepath) {
    const tabsContainer = document.getElementById('tabs-container');
    const filename = filepath.split('/').pop();

    const tab = document.createElement('div');
    tab.className = 'editor-tab';
    tab.dataset.path = filepath;

    tab.innerHTML = `
        <span class="tab-name">${filename}</span>
        <button class="close-btn" data-path="${filepath}">×</button>
    `;

    tab.querySelector('.tab-name').addEventListener('click', () => switchToFile(filepath));
    tab.querySelector('.close-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        closeFile(filepath);
    });

    tabsContainer.appendChild(tab);
}

/**
 * Close a file tab
 */
function closeFile(filepath) {
    const fileInfo = IDE.openFiles.get(filepath);

    if (fileInfo && fileInfo.modified) {
        if (!confirm(`${filepath} has unsaved changes. Close anyway?`)) {
            return;
        }
    }

    IDE.openFiles.delete(filepath);

    // Remove tab
    const tab = document.querySelector(`.editor-tab[data-path="${filepath}"]`);
    if (tab) tab.remove();

    // If this was the current file, switch to another or show placeholder
    if (IDE.currentFile === filepath) {
        const remaining = Array.from(IDE.openFiles.keys());
        if (remaining.length > 0) {
            switchToFile(remaining[0]);
        } else {
            IDE.currentFile = null;
            document.getElementById('editor-placeholder').style.display = 'flex';
            document.getElementById('monaco-editor').style.display = 'none';
        }
    }
}

/**
 * Get CSRF token from meta tag
 */
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

/**
 * Save the current file
 */
async function saveCurrentFile() {
    if (!IDE.currentFile) return;

    const fileInfo = IDE.openFiles.get(IDE.currentFile);
    const content = IDE.editor.getValue();

    console.log(`IDE: Saving ${IDE.currentFile}, ${content.length} bytes`);

    try {
        const response = await fetch(`/__scribe_gui/api/file/${IDE.currentFile}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ content })
        });

        console.log(`IDE: Save response status: ${response.status}`);

        if (!response.ok) {
            const text = await response.text();
            console.error('IDE: Save failed, response:', text);
            setStatus(`Error saving: HTTP ${response.status}`, 'error');
            return;
        }

        const data = await response.json();
        console.log('IDE: Save response data:', data);

        if (data.success) {
            fileInfo.content = content;
            fileInfo.originalContent = content;
            fileInfo.modified = false;

            document.getElementById('save-btn').disabled = true;
            setStatus(`Saved ${IDE.currentFile}`);
        } else {
            setStatus(`Error saving: ${data.error}`, 'error');
        }
    } catch (error) {
        setStatus(`Error saving: ${error.message}`, 'error');
        console.error('IDE: Save error:', error);
    }
}

/**
 * Mark current file as modified
 */
function markFileAsModified() {
    if (!IDE.currentFile) return;

    const fileInfo = IDE.openFiles.get(IDE.currentFile);
    const currentContent = IDE.editor.getValue();

    fileInfo.modified = (currentContent !== fileInfo.originalContent);
    document.getElementById('save-btn').disabled = !fileInfo.modified;

    // Update tab to show modified indicator
    const tab = document.querySelector(`.editor-tab[data-path="${IDE.currentFile}"]`);
    if (tab) {
        const tabName = tab.querySelector('.tab-name');
        if (fileInfo.modified && !tabName.textContent.startsWith('● ')) {
            tabName.textContent = '● ' + tabName.textContent;
        } else if (!fileInfo.modified && tabName.textContent.startsWith('● ')) {
            tabName.textContent = tabName.textContent.substring(2);
        }
    }
}

/**
 * Create new file
 */
async function createNewFile() {
    const filename = document.getElementById('new-file-name').value.trim();

    if (!filename) {
        alert('Please enter a filename');
        return;
    }

    try {
        const response = await fetch('/__scribe_gui/api/file/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ path: filename, type: 'file' })
        });

        const data = await response.json();

        if (data.success) {
            hideModal('new-file-modal');
            document.getElementById('new-file-name').value = '';
            loadFileTree();
            openFile(filename);
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

/**
 * Create new folder
 */
async function createNewFolder() {
    const foldername = document.getElementById('new-folder-name').value.trim();

    if (!foldername) {
        alert('Please enter a folder name');
        return;
    }

    try {
        const response = await fetch('/__scribe_gui/api/file/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ path: foldername, type: 'directory' })
        });

        const data = await response.json();

        if (data.success) {
            hideModal('new-folder-modal');
            document.getElementById('new-folder-name').value = '';
            loadFileTree();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

/**
 * Switch right panel tabs
 */
function switchPanel(panelName) {
    document.querySelectorAll('.panel-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.panel === panelName);
    });

    document.querySelectorAll('.panel-content').forEach(content => {
        content.classList.toggle('active', content.id === `${panelName}-panel`);
    });

    // Load data for the panel if needed
    if (panelName === 'database') {
        loadDatabaseTables();
    } else if (panelName === 'routes') {
        loadRoutes();
    }
}

/**
 * Load preview of current route
 */
function loadPreview() {
    const url = document.getElementById('preview-url').value.trim();

    if (!url) {
        setStatus('Enter a route path to preview', 'error');
        return;
    }

    const iframe = document.getElementById('preview-frame');
    iframe.src = url;

    setStatus(`Loading preview: ${url}`);
}

/**
 * Refresh preview
 */
function refreshPreview() {
    const iframe = document.getElementById('preview-frame');

    if (iframe.src) {
        iframe.src = iframe.src; // Reload
        setStatus('Preview refreshed');
    }
}

/**
 * Load database tables
 */
async function loadDatabaseTables() {
    try {
        const response = await fetch('/__scribe_gui/api/database/tables');
        const data = await response.json();

        const select = document.getElementById('table-select');
        select.innerHTML = '<option value="">Select a table...</option>';

        data.tables.forEach(table => {
            const option = document.createElement('option');
            option.value = table;
            option.textContent = table;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading tables:', error);
    }
}

/**
 * Load table data
 */
async function loadTableData(tableName) {
    try {
        const response = await fetch(`/__scribe_gui/api/database/table/${tableName}`);
        const data = await response.json();

        const content = document.getElementById('database-content');

        if (data.columns.length === 0) {
            content.innerHTML = '<p class="placeholder-text">Table is empty</p>';
            return;
        }

        // Create table
        let html = '<table class="db-table"><thead><tr>';
        data.columns.forEach(col => {
            html += `<th>${col}</th>`;
        });
        html += '</tr></thead><tbody>';

        data.data.forEach(row => {
            html += '<tr>';
            data.columns.forEach(col => {
                html += `<td>${row[col] !== null ? row[col] : '<em>NULL</em>'}</td>`;
            });
            html += '</tr>';
        });

        html += '</tbody></table>';
        content.innerHTML = html;
    } catch (error) {
        console.error('Error loading table data:', error);
    }
}

/**
 * Load routes
 */
async function loadRoutes() {
    try {
        const response = await fetch('/__scribe_gui/api/routes');
        const data = await response.json();

        const routesList = document.getElementById('routes-list');

        if (data.routes.length === 0) {
            routesList.innerHTML = '<p class="placeholder-text">No routes found in .stpl files</p>';
            return;
        }

        let html = '<div class="routes-container">';
        data.routes.forEach(route => {
            const methods = route.methods.join(', ');
            const decorators = route.decorators.length > 0
                ? `<div class="route-decorators">@${route.decorators.join(' @')}</div>`
                : '';

            html += `
                <div class="route-item">
                    <div class="route-header">
                        <span class="route-methods">${methods}</span>
                        <span class="route-path">${route.path}</span>
                    </div>
                    ${decorators}
                    <div class="route-file">${route.file}</div>
                </div>
            `;
        });
        html += '</div>';

        routesList.innerHTML = html;
    } catch (error) {
        console.error('Error loading routes:', error);
        document.getElementById('routes-list').innerHTML =
            '<p class="placeholder-text error">Error loading routes</p>';
    }
}

/**
 * Update project name in header
 */
function updateProjectName() {
    const projectName = window.location.pathname.split('/').filter(Boolean)[0] || 'ScribeEngine Project';
    document.getElementById('project-name').textContent = projectName;
}

/**
 * Update cursor position in status bar
 */
function updateCursorPosition(position) {
    document.getElementById('cursor-position').textContent = `Ln ${position.lineNumber}, Col ${position.column}`;
}

/**
 * Set status message
 */
function setStatus(message, type = 'info') {
    const statusEl = document.getElementById('status-message');
    statusEl.textContent = message;

    // Could add color coding based on type
    if (type === 'error') {
        statusEl.style.color = '#f48771';
    } else {
        statusEl.style.color = 'white';
    }
}

/**
 * Show modal
 */
function showModal(modalId) {
    document.getElementById(modalId).style.display = 'flex';
}

/**
 * Hide modal
 */
function hideModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

/**
 * Use a simple textarea fallback if Monaco fails to load
 */
function useFallbackEditor() {
    console.log('IDE: Setting up fallback text editor');

    // Hide placeholder, show editor container
    document.getElementById('editor-placeholder').style.display = 'none';
    const editorContainer = document.getElementById('monaco-editor');
    editorContainer.style.display = 'block';

    // Create a simple textarea
    editorContainer.innerHTML = '<textarea id="fallback-editor" style="width: 100%; height: 100%; background: #1e1e1e; color: #ccc; border: none; padding: 10px; font-family: monospace; font-size: 14px; resize: none; outline: none;"></textarea>';

    const textarea = document.getElementById('fallback-editor');

    // Create a mock editor object that mimics Monaco's API
    IDE.editor = {
        setValue: (value) => {
            console.log(`IDE: Fallback setValue called with ${value.length} chars`);
            textarea.value = value;
            // Force display
            editorContainer.style.display = 'block';
        },
        getValue: () => {
            return textarea.value;
        },
        getModel: () => null,
        setModel: () => {},
        onDidChangeCursorPosition: () => {},
        onDidChangeModelContent: (callback) => {
            textarea.addEventListener('input', callback);
        }
    };

    IDE.editorReady = true;
    console.log('IDE: Fallback editor ready');

    // Process pending file switch
    if (IDE.pendingFileSwitch) {
        console.log('IDE: Processing pending file in fallback mode:', IDE.pendingFileSwitch);
        switchToFile(IDE.pendingFileSwitch);
        IDE.pendingFileSwitch = null;
    }
}
