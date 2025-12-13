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
    pendingFileSwitch: null,
    panels: {
        sidebarWidth: 250,
        previewWidth: null,
        previewVisible: true
    },
    categorizedTree: null,
    categoryState: {
        collapsedCategories: new Set(),
        collapsedFolders: new Set()
    }
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

    // Initialize preview with root path
    const previewUrlInput = document.getElementById('preview-url');
    if (previewUrlInput && !previewUrlInput.value) {
        previewUrlInput.value = '/';
        loadPreview();
    }

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

        // Enhanced multi-language tokenizer for .stpl files
        // Supports Python blocks {$ $}, Jinja2 {{ }} {% %}, and HTML
        monaco.languages.setMonarchTokensProvider('scribe-template', {
            defaultToken: '',
            tokenPostfix: '.stpl',

            // Keywords for different contexts
            pythonKeywords: [
                'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue',
                'def', 'del', 'elif', 'else', 'except', 'False', 'finally', 'for',
                'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'None',
                'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True', 'try',
                'while', 'with', 'yield'
            ],

            pythonBuiltins: [
                'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
                'chr', 'dict', 'dir', 'divmod', 'enumerate', 'filter', 'float', 'format',
                'frozenset', 'getattr', 'hasattr', 'hash', 'hex', 'int', 'isinstance',
                'len', 'list', 'map', 'max', 'min', 'next', 'object', 'oct', 'open',
                'ord', 'pow', 'print', 'range', 'repr', 'reversed', 'round', 'set',
                'setattr', 'slice', 'sorted', 'str', 'sum', 'tuple', 'type', 'zip'
            ],

            jinjaKeywords: [
                'block', 'endblock', 'extends', 'include', 'import', 'from', 'as',
                'macro', 'endmacro', 'call', 'endcall', 'filter', 'endfilter',
                'set', 'endset', 'if', 'elif', 'else', 'endif', 'for', 'endfor',
                'in', 'not', 'and', 'or', 'is', 'defined', 'undefined'
            ],

            jinjaFilters: [
                'abs', 'attr', 'batch', 'capitalize', 'center', 'default', 'escape',
                'filesizeformat', 'first', 'float', 'format', 'groupby', 'indent',
                'int', 'join', 'last', 'length', 'list', 'lower', 'map', 'max',
                'min', 'pprint', 'random', 'reject', 'replace', 'reverse', 'round',
                'safe', 'select', 'slice', 'sort', 'string', 'sum', 'title', 'trim',
                'truncate', 'unique', 'upper', 'urlencode', 'urlize', 'wordcount', 'wordwrap'
            ],

            operators: [
                '=', '>', '<', '!', '~', '?', ':', '==', '<=', '>=', '!=',
                '&&', '||', '++', '--', '+', '-', '*', '/', '&', '|', '^', '%',
                '<<', '>>', '>>>', '+=', '-=', '*=', '/=', '&=', '|=', '^=',
                '%=', '<<=', '>>=', '>>>='
            ],

            symbols: /[=><!~?:&|+\-*\/\^%]+/,
            escapes: /\\(?:[abfnrtv\\"']|x[0-9A-Fa-f]{1,4}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8})/,
            digits: /\d+(_+\d+)*/,

            tokenizer: {
                // ========== ROOT STATE (HTML Mode) ==========
                root: [
                    // Route decorators (always at start of line or after whitespace)
                    [/^(\s*)(@\w+)/, ['white', 'annotation']],
                    [/(\s+)(@\w+)/, ['white', 'annotation']],

                    // Python code blocks {$ ... $} - Distinctive orange highlight
                    [/\{\$/, { token: 'type.identifier', next: '@pythonBlock', nextEmbedded: 'python' }],

                    // Jinja2 expressions {{ ... }} - Cyan/teal highlight
                    [/\{\{/, { token: 'number.hex', next: '@jinjaExpression' }],

                    // Jinja2 statements {% ... %} - Purple/magenta highlight
                    [/\{%/, { token: 'tag', next: '@jinjaStatement' }],

                    // HTML comments
                    [/<!--/, { token: 'comment.html', next: '@htmlComment' }],

                    // HTML doctype
                    [/<!DOCTYPE/, 'metatag.html', '@doctype'],

                    // HTML tags
                    [/<(\w+)/, { token: 'tag.html', next: '@htmlTag' }],
                    [/<\/(\w+)\s*>/, 'tag.html'],

                    // Whitespace
                    [/[ \t\r\n]+/, 'white'],
                ],

                // ========== HTML COMMENT STATE ==========
                htmlComment: [
                    [/-->/, { token: 'comment.html', next: '@pop' }],
                    [/./, 'comment.html']
                ],

                // ========== HTML DOCTYPE STATE ==========
                doctype: [
                    [/[^>]+/, 'metatag.content.html'],
                    [/>/, { token: 'metatag.html', next: '@pop' }]
                ],

                // ========== HTML TAG STATE ==========
                htmlTag: [
                    [/[ \t\r\n]+/, 'white'],
                    [/(\w+)(\s*=\s*)/, ['attribute.name.html', 'delimiter.html']],
                    [/"([^"]*)"/, 'attribute.value.html'],
                    [/'([^']*)'/, 'attribute.value.html'],
                    [/>/, { token: 'tag.html', next: '@pop' }],
                    [/(\w+)/, 'attribute.name.html']
                ],

                // ========== PYTHON BLOCK STATE {$ ... $} ==========
                pythonBlock: [
                    // Exit Python block - Matching orange highlight
                    [/\$\}/, { token: 'type.identifier', next: '@pop', nextEmbedded: '@pop' }],

                    // Python comments
                    [/#.*$/, 'comment'],

                    // Python keywords
                    [/\b(def|class|return|if|elif|else|for|while|try|except|finally|with|as|import|from|pass|break|continue|raise|yield|await|async|lambda|global|nonlocal|assert)\b/, 'keyword'],

                    // Boolean and None
                    [/\b(True|False|None)\b/, 'constant.language'],

                    // Built-in functions
                    [/\b(print|len|range|enumerate|zip|map|filter|str|int|float|bool|list|dict|set|tuple|type|isinstance|hasattr|getattr|setattr)\b/, 'support.function'],

                    // Special objects available in ScribeEngine
                    [/\b(db|session|request|g|redirect|abort|jsonify|url_for|csrf|flash)\b/, 'variable.language'],

                    // Decorators
                    [/@\w+/, 'annotation'],

                    // Numbers
                    [/\b\d+[lL]?\b/, 'number'],
                    [/\b0[xX][0-9a-fA-F]+[lL]?\b/, 'number.hex'],
                    [/\b0[oO][0-7]+[lL]?\b/, 'number.octal'],
                    [/\b0[bB][01]+[lL]?\b/, 'number.binary'],
                    [/\b\d+\.?\d*([eE][\-+]?\d+)?\b/, 'number.float'],

                    // Strings (including f-strings)
                    [/f"/, { token: 'string', next: '@fstringDouble' }],
                    [/f'/, { token: 'string', next: '@fstringSingle' }],
                    [/"""/, { token: 'string', next: '@stringTripleDouble' }],
                    [/'''/, { token: 'string', next: '@stringTripleSingle' }],
                    [/"/, { token: 'string', next: '@stringDouble' }],
                    [/'/, { token: 'string', next: '@stringSingle' }],

                    // Operators
                    [/[{}()\[\]]/, '@brackets'],
                    [/@symbols/, 'operator'],

                    // Identifiers
                    [/[a-zA-Z_]\w*/, 'identifier'],

                    // Whitespace
                    [/[ \t\r\n]+/, 'white'],
                ],

                // ========== JINJA2 EXPRESSION STATE {{ ... }} ==========
                jinjaExpression: [
                    // Exit expression - Matching cyan/teal highlight
                    [/\}\}/, { token: 'number.hex', next: '@pop' }],

                    // Jinja2 filters (pipe syntax)
                    [/\|(\w+)/, 'support.function.jinja'],

                    // Jinja2 keywords
                    [/\b(is|not|defined|undefined|none|true|false)\b/, 'keyword.jinja'],

                    // Python-like keywords in expressions
                    [/\b(and|or|not|in)\b/, 'keyword.jinja'],

                    // Numbers
                    [/\b\d+\.?\d*\b/, 'number'],

                    // Strings
                    [/"([^"\\]|\\.)*"/, 'string'],
                    [/'([^'\\]|\\.)*'/, 'string'],

                    // Special variables
                    [/\b(session|request|g)\b/, 'variable.language'],

                    // Operators and symbols
                    [/[{}()\[\].]/, '@brackets'],
                    [/@symbols/, 'operator'],

                    // Identifiers (variables)
                    [/[a-zA-Z_]\w*/, 'variable'],

                    [/[ \t\r\n]+/, 'white'],
                ],

                // ========== JINJA2 STATEMENT STATE {% ... %} ==========
                jinjaStatement: [
                    // Exit statement - Matching purple/magenta highlight
                    [/%\}/, { token: 'tag', next: '@pop' }],

                    // Jinja2 block keywords
                    [/\b(block|endblock|extends|include|import|macro|endmacro|call|endcall|filter|endfilter|set|endset)\b/, 'keyword.control.jinja'],

                    // Jinja2 control flow
                    [/\b(if|elif|else|endif|for|endfor|in|not|and|or|is|defined|undefined)\b/, 'keyword.jinja'],

                    // Boolean and None
                    [/\b(true|false|none)\b/, 'constant.language'],

                    // Numbers
                    [/\b\d+\.?\d*\b/, 'number'],

                    // Strings
                    [/"([^"\\]|\\.)*"/, 'string'],
                    [/'([^'\\]|\\.)*'/, 'string'],

                    // Operators
                    [/[{}()\[\].]/, '@brackets'],
                    [/@symbols/, 'operator'],

                    // Identifiers
                    [/[a-zA-Z_]\w*/, 'identifier'],

                    [/[ \t\r\n]+/, 'white'],
                ],

                // ========== STRING STATES FOR PYTHON ==========
                stringDouble: [
                    [/[^\\"]+/, 'string'],
                    [/@escapes/, 'string.escape'],
                    [/\\./, 'string.escape.invalid'],
                    [/"/, { token: 'string', next: '@pop' }]
                ],

                stringSingle: [
                    [/[^\\']+/, 'string'],
                    [/@escapes/, 'string.escape'],
                    [/\\./, 'string.escape.invalid'],
                    [/'/, { token: 'string', next: '@pop' }]
                ],

                stringTripleDouble: [
                    [/[^"]+/, 'string'],
                    [/"""/, { token: 'string', next: '@pop' }],
                    [/"/, 'string']
                ],

                stringTripleSingle: [
                    [/[^']+/, 'string'],
                    [/'''/, { token: 'string', next: '@pop' }],
                    [/'/, 'string']
                ],

                // F-strings (simplified - full support would require nested expressions)
                fstringDouble: [
                    [/[^\\"{}]+/, 'string'],
                    [/@escapes/, 'string.escape'],
                    [/\{/, 'string.interpolation.delimiter', '@fstringInterp'],
                    [/"/, { token: 'string', next: '@pop' }]
                ],

                fstringSingle: [
                    [/[^\\'{}]+/, 'string'],
                    [/@escapes/, 'string.escape'],
                    [/\{/, 'string.interpolation.delimiter', '@fstringInterp'],
                    [/'/, { token: 'string', next: '@pop' }]
                ],

                fstringInterp: [
                    [/[^}]+/, 'string.interpolation'],
                    [/\}/, { token: 'string.interpolation.delimiter', next: '@pop' }]
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
 * Load panel state from localStorage
 */
function loadPanelState() {
    try {
        const saved = localStorage.getItem('scribe-ide-panels');
        if (saved) {
            const state = JSON.parse(saved);
            IDE.panels = { ...IDE.panels, ...state };
        }
    } catch (error) {
        console.error('IDE: Error loading panel state:', error);
    }
}

/**
 * Save panel state to localStorage
 */
function savePanelState() {
    try {
        localStorage.setItem('scribe-ide-panels', JSON.stringify(IDE.panels));
    } catch (error) {
        console.error('IDE: Error saving panel state:', error);
    }
}

/**
 * Load file tree state from localStorage
 */
function loadFileTreeState() {
    try {
        const saved = localStorage.getItem('scribe-ide-file-tree');
        if (saved) {
            const state = JSON.parse(saved);
            IDE.categoryState.collapsedCategories = new Set(state.collapsedCategories || []);
            IDE.categoryState.collapsedFolders = new Set(state.collapsedFolders || []);
        }
    } catch (error) {
        console.error('IDE: Error loading file tree state:', error);
    }
}

/**
 * Save file tree state to localStorage
 */
function saveFileTreeState() {
    try {
        const state = {
            collapsedCategories: Array.from(IDE.categoryState.collapsedCategories),
            collapsedFolders: Array.from(IDE.categoryState.collapsedFolders)
        };
        localStorage.setItem('scribe-ide-file-tree', JSON.stringify(state));
    } catch (error) {
        console.error('IDE: Error saving file tree state:', error);
    }
}

/**
 * Debounce function for performance
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
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

    // Refresh files button
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
    loadPanelState();

    const sidebarResizer = document.getElementById('sidebar-resizer');
    const sidebar = document.getElementById('sidebar');

    if (sidebarResizer && sidebar) {
        sidebar.style.width = `${IDE.panels.sidebarWidth}px`;
        makeResizable(sidebarResizer, sidebar, 'width', 150, 500, false, (newWidth) => {
            IDE.panels.sidebarWidth = newWidth;
            savePanelState();
        });
    }

    const rightPanelResizer = document.getElementById('right-panel-resizer');
    const rightPanel = document.getElementById('right-panel');

    if (rightPanelResizer && rightPanel) {
        // Calculate 50/50 split if no saved width
        if (!IDE.panels.previewWidth) {
            const ideMain = document.getElementById('ide-main');
            const availableWidth = ideMain.offsetWidth - IDE.panels.sidebarWidth - 8;
            IDE.panels.previewWidth = Math.floor(availableWidth / 2);
        }

        rightPanel.style.width = `${IDE.panels.previewWidth}px`;
        if (!IDE.panels.previewVisible) {
            rightPanel.classList.add('hidden');
        }

        const calculateMaxWidth = () => {
            const ideMain = document.getElementById('ide-main');
            const availableWidth = ideMain.offsetWidth - IDE.panels.sidebarWidth - 8;
            return availableWidth - 400;
        };

        makeResizable(rightPanelResizer, rightPanel, 'width', 300, calculateMaxWidth(), true, (newWidth) => {
            IDE.panels.previewWidth = newWidth;
            savePanelState();
        });
    }

    const toggleBtn = document.getElementById('toggle-preview-btn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', togglePreviewPanel);
        updateToggleButtonIcon();
    }

    // Window resize handler
    window.addEventListener('resize', debounce(handleWindowResize, 200));
}

/**
 * Make an element resizable
 */
function makeResizable(resizer, element, property, minSize, maxSize, reverse = false, onResize = null) {
    let startPos = 0;
    let startSize = 0;

    resizer.addEventListener('mousedown', (e) => {
        e.preventDefault();
        startPos = property === 'width' ? e.clientX : e.clientY;
        startSize = parseInt(getComputedStyle(element)[property], 10);

        document.addEventListener('mousemove', resize);
        document.addEventListener('mouseup', stopResize);

        document.body.style.cursor = property === 'width' ? 'col-resize' : 'row-resize';
        document.body.style.userSelect = 'none';
    });

    function resize(e) {
        const currentPos = property === 'width' ? e.clientX : e.clientY;
        const diff = reverse ? (startPos - currentPos) : (currentPos - startPos);
        let newSize = startSize + diff;

        const actualMaxSize = typeof maxSize === 'function' ? maxSize() : maxSize;
        newSize = Math.max(minSize, Math.min(actualMaxSize, newSize));

        element.style[property] = `${newSize}px`;

        if (onResize) {
            onResize(newSize);
        }
    }

    function stopResize() {
        document.removeEventListener('mousemove', resize);
        document.removeEventListener('mouseup', stopResize);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
    }
}

/**
 * Toggle preview panel visibility
 */
function togglePreviewPanel() {
    const rightPanel = document.getElementById('right-panel');
    const isHidden = rightPanel.classList.contains('hidden');

    if (isHidden) {
        rightPanel.classList.remove('hidden');
        rightPanel.style.width = `${IDE.panels.previewWidth}px`;
        IDE.panels.previewVisible = true;
    } else {
        rightPanel.classList.add('hidden');
        IDE.panels.previewVisible = false;
    }

    updateToggleButtonIcon();
    savePanelState();
}

/**
 * Update toggle button icon based on panel state
 */
function updateToggleButtonIcon() {
    const toggleBtn = document.getElementById('toggle-preview-btn');
    const rightPanel = document.getElementById('right-panel');

    if (toggleBtn) {
        const iconSpan = toggleBtn.querySelector('.icon');
        const isHidden = rightPanel.classList.contains('hidden');
        if (iconSpan) {
            iconSpan.textContent = isHidden ? '▶' : '◀';
        }
        toggleBtn.title = isHidden ? 'Show Preview Panel' : 'Hide Preview Panel';
    }
}

/**
 * Handle window resize to keep panels within bounds
 */
function handleWindowResize() {
    const rightPanel = document.getElementById('right-panel');
    if (!rightPanel || rightPanel.classList.contains('hidden')) return;

    const ideMain = document.getElementById('ide-main');
    const availableWidth = ideMain.offsetWidth - IDE.panels.sidebarWidth - 8;
    const maxWidth = availableWidth - 400;

    if (IDE.panels.previewWidth > maxWidth) {
        IDE.panels.previewWidth = maxWidth;
        rightPanel.style.width = `${maxWidth}px`;
        savePanelState();
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
 * Categorize files into Templates, Logic, Data, Style
 */
function categorizeFiles(fileTree) {
    const categories = {
        templates: { label: 'Templates (Pages)', icon: '📄', files: [], collapsed: false },
        logic: { label: 'Logic', icon: '🔧', folders: {}, collapsed: false },
        data: { label: 'Data', icon: '🗄️', folders: {}, collapsed: false },
        style: { label: 'Style', icon: '🎨', folders: {}, collapsed: false }
    };

    const configFiles = [];

    function processNode(node, parentPath = '') {
        const fullPath = parentPath ? `${parentPath}/${node.name}` : node.name;

        // Config files
        if (node.type === 'file' && node.name === 'scribe.json') {
            configFiles.push({ ...node, path: fullPath });
            return;
        }

        // Templates (.stpl files anywhere)
        if (node.type === 'file' && node.extension === '.stpl') {
            categories.templates.files.push({ ...node, path: fullPath });
            return;
        }

        // Logic (lib/ directory - .py files)
        if (fullPath.startsWith('lib/') || fullPath === 'lib') {
            if (node.type === 'file' && node.extension === '.py') {
                addToCategoryFolder(categories.logic, node, fullPath, 'lib');
            } else if (node.type === 'directory' && node.children) {
                node.children.forEach(child => processNode(child, fullPath));
            }
            return;
        }

        // Data (migrations/ directory - .sql files)
        if (fullPath.startsWith('migrations/') || fullPath === 'migrations') {
            if (node.type === 'file' && node.extension === '.sql') {
                addToCategoryFolder(categories.data, node, fullPath, 'migrations');
            } else if (node.type === 'directory' && node.children) {
                node.children.forEach(child => processNode(child, fullPath));
            }
            return;
        }

        // Style (static/css/ directory - .css files)
        if (fullPath.startsWith('static/css/') || fullPath === 'static/css' || fullPath === 'static') {
            if (node.type === 'file' && node.extension === '.css') {
                addToCategoryFolder(categories.style, node, fullPath, 'static');
            } else if (node.type === 'directory' && node.children) {
                node.children.forEach(child => processNode(child, fullPath));
            }
            return;
        }

        // Process children for other directories
        if (node.type === 'directory' && node.children) {
            node.children.forEach(child => processNode(child, fullPath));
        }
    }

    function addToCategoryFolder(category, node, fullPath, rootPath) {
        const relativePath = fullPath.replace(new RegExp(`^${rootPath}/?`), '');

        if (node.type === 'file') {
            if (!relativePath) return;

            const parts = relativePath.split('/');
            let current = category.folders;

            // Build folder structure
            for (let i = 0; i < parts.length - 1; i++) {
                const part = parts[i];
                if (!current[part]) {
                    current[part] = {
                        name: part,
                        files: [],
                        subfolders: {},
                        collapsed: false
                    };
                }
                current = current[part].subfolders;
            }

            // Add file to parent folder or root
            if (parts.length === 1) {
                // File directly in root (e.g., lib/helpers.py)
                if (!category.rootFiles) category.rootFiles = [];
                category.rootFiles.push({ ...node, path: fullPath });
            } else {
                // File in subfolder
                const parentKey = parts[parts.length - 2];
                if (!current[parentKey]) {
                    current[parentKey] = {
                        name: parentKey,
                        files: [],
                        subfolders: {},
                        collapsed: false
                    };
                }
                current[parentKey].files.push({ ...node, path: fullPath });
            }
        }
    }

    fileTree.forEach(node => processNode(node));

    // Apply collapsed state from localStorage
    Object.keys(categories).forEach(key => {
        categories[key].collapsed = IDE.categoryState.collapsedCategories.has(key);
    });

    return { categories, configFiles };
}

/**
 * Render file tree in sidebar (categorized)
 */
function renderFileTree() {
    console.log('IDE: Rendering categorized file tree...');
    const container = document.getElementById('file-tree');

    if (!container || !IDE.fileTree || IDE.fileTree.length === 0) {
        container.innerHTML = '<div class="loading">No files found</div>';
        return;
    }

    loadFileTreeState();
    IDE.categorizedTree = categorizeFiles(IDE.fileTree);
    const { categories, configFiles } = IDE.categorizedTree;

    container.innerHTML = '';

    // Render each category
    Object.entries(categories).forEach(([key, category]) => {
        const hasContent = (category.files && category.files.length > 0) ||
                          (category.rootFiles && category.rootFiles.length > 0) ||
                          (category.folders && Object.keys(category.folders).length > 0);

        if (!hasContent) return;

        const section = renderCategory(key, category);
        container.appendChild(section);
    });

    // Render config files
    if (configFiles.length > 0) {
        const configSection = document.createElement('div');
        configSection.className = 'config-files';
        configFiles.forEach(file => {
            const fileDiv = createFileElement(file);
            configSection.appendChild(fileDiv);
        });
        container.appendChild(configSection);
    }
}

/**
 * Render a category section
 */
function renderCategory(categoryKey, category) {
    const section = document.createElement('div');
    section.className = 'category-section';

    const fileCount = (category.files ? category.files.length : 0) +
                     (category.rootFiles ? category.rootFiles.length : 0);
    const folderCount = category.folders ? Object.keys(category.folders).length : 0;

    const header = document.createElement('div');
    header.className = `category-header ${category.collapsed ? 'collapsed' : ''}`;

    // Create header content (clickable area)
    const headerContent = document.createElement('div');
    headerContent.className = 'category-header-content';
    headerContent.innerHTML = `
        <span class="category-icon">${category.icon}</span>
        <span class="category-label">${category.label}</span>
        <span class="category-count">${fileCount + folderCount}</span>
        <span class="collapse-icon">▼</span>
    `;

    // Create action buttons
    const actions = document.createElement('div');
    actions.className = 'category-actions';

    const newFileBtn = document.createElement('button');
    newFileBtn.className = 'category-action-btn';
    newFileBtn.innerHTML = '📄';
    newFileBtn.title = 'New File';
    newFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        showNewFileModal(categoryKey);
    });

    const newFolderBtn = document.createElement('button');
    newFolderBtn.className = 'category-action-btn';
    newFolderBtn.innerHTML = '📁';
    newFolderBtn.title = 'New Folder';
    newFolderBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        showNewFolderModal(categoryKey);
    });

    actions.appendChild(newFileBtn);
    actions.appendChild(newFolderBtn);

    header.appendChild(headerContent);
    header.appendChild(actions);

    const content = document.createElement('div');
    content.className = `category-content ${category.collapsed ? 'collapsed' : ''}`;

    // Render root files (files directly in category root, e.g., lib/helpers.py)
    if (category.rootFiles) {
        category.rootFiles.forEach(file => {
            content.appendChild(createFileElement(file));
        });
    }

    // Render folders
    if (category.folders) {
        Object.values(category.folders).forEach(folder => {
            content.appendChild(renderFolder(folder));
        });
    }

    // Render files
    if (category.files) {
        category.files.forEach(file => {
            content.appendChild(createFileElement(file));
        });
    }

    headerContent.addEventListener('click', () => toggleCategory(categoryKey, header, content));

    section.appendChild(header);
    section.appendChild(content);
    return section;
}

/**
 * Render a folder within a category
 */
function renderFolder(folder, level = 0) {
    const wrapper = document.createElement('div');
    wrapper.className = 'category-folder';

    const folderDiv = document.createElement('div');
    folderDiv.className = `folder-item ${folder.collapsed ? 'collapsed' : ''}`;
    folderDiv.style.paddingLeft = `${level * 1 + 1}rem`;
    folderDiv.innerHTML = `<span class="folder-icon">📁</span> ${folder.name}`;

    const childrenDiv = document.createElement('div');
    childrenDiv.className = `folder-children ${folder.collapsed ? 'collapsed' : ''}`;

    if (folder.subfolders) {
        Object.values(folder.subfolders).forEach(subfolder => {
            childrenDiv.appendChild(renderFolder(subfolder, level + 1));
        });
    }

    if (folder.files) {
        folder.files.forEach(file => {
            childrenDiv.appendChild(createFileElement(file, level + 1));
        });
    }

    folderDiv.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleFolder(folder.name, folderDiv, childrenDiv);
    });

    wrapper.appendChild(folderDiv);
    wrapper.appendChild(childrenDiv);
    return wrapper;
}

/**
 * Create a file element
 */
function createFileElement(file, level = 0) {
    const fileDiv = document.createElement('div');
    fileDiv.className = 'file-item';
    fileDiv.style.paddingLeft = `${level * 1 + 1}rem`;
    fileDiv.textContent = `📄 ${file.name}`;
    fileDiv.dataset.path = file.path;
    fileDiv.addEventListener('click', () => openFile(file.path));
    return fileDiv;
}

/**
 * Toggle category collapsed state
 */
function toggleCategory(categoryKey, headerElement, contentElement) {
    const isCollapsed = headerElement.classList.contains('collapsed');

    if (isCollapsed) {
        headerElement.classList.remove('collapsed');
        contentElement.classList.remove('collapsed');
        IDE.categoryState.collapsedCategories.delete(categoryKey);
    } else {
        headerElement.classList.add('collapsed');
        contentElement.classList.add('collapsed');
        IDE.categoryState.collapsedCategories.add(categoryKey);
    }

    saveFileTreeState();
}

/**
 * Toggle folder collapsed state
 */
function toggleFolder(folderPath, folderElement, childrenElement) {
    const isCollapsed = folderElement.classList.contains('collapsed');

    if (isCollapsed) {
        folderElement.classList.remove('collapsed');
        childrenElement.classList.remove('collapsed');
        IDE.categoryState.collapsedFolders.delete(folderPath);
    } else {
        folderElement.classList.add('collapsed');
        childrenElement.classList.add('collapsed');
        IDE.categoryState.collapsedFolders.add(folderPath);
    }

    saveFileTreeState();
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
 * Category context for file creation
 */
let currentFileContext = null;

/**
 * Show new file modal with category context
 */
function showNewFileModal(categoryKey) {
    const contexts = {
        templates: { extension: '.stpl', basePath: '', label: 'Template' },
        logic: { extension: '.py', basePath: 'lib/', label: 'Python Module' },
        data: { extension: '.sql', basePath: 'migrations/', label: 'Migration' },
        style: { extension: '.css', basePath: 'static/css/', label: 'Stylesheet' }
    };

    currentFileContext = contexts[categoryKey];
    const modal = document.getElementById('new-file-modal');
    const input = document.getElementById('new-file-name');
    const title = modal.querySelector('h2');

    title.textContent = `New ${currentFileContext.label}`;
    input.placeholder = `${currentFileContext.basePath}filename${currentFileContext.extension}`;
    input.value = '';

    showModal('new-file-modal');
    setTimeout(() => input.focus(), 100);
}

/**
 * Show new folder modal with category context
 */
function showNewFolderModal(categoryKey) {
    const contexts = {
        templates: { basePath: '', label: 'Template Folder' },
        logic: { basePath: 'lib/', label: 'Logic Folder' },
        data: { basePath: 'migrations/', label: 'Data Folder' },
        style: { basePath: 'static/css/', label: 'Style Folder' }
    };

    currentFileContext = contexts[categoryKey];
    const modal = document.getElementById('new-folder-modal');
    const input = document.getElementById('new-folder-name');
    const title = modal.querySelector('h2');

    title.textContent = `New ${currentFileContext.label}`;
    input.placeholder = `${currentFileContext.basePath}foldername`;
    input.value = '';

    showModal('new-folder-modal');
    setTimeout(() => input.focus(), 100);
}

/**
 * Create new file
 */
async function createNewFile() {
    let filename = document.getElementById('new-file-name').value.trim();

    if (!filename) {
        alert('Please enter a filename');
        return;
    }

    // Apply context-aware defaults
    if (currentFileContext) {
        // If user didn't provide basePath, prepend it
        if (!filename.startsWith(currentFileContext.basePath)) {
            filename = currentFileContext.basePath + filename;
        }
        // If user didn't provide extension, append it
        if (!filename.endsWith(currentFileContext.extension)) {
            filename += currentFileContext.extension;
        }
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
            currentFileContext = null;
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
    let foldername = document.getElementById('new-folder-name').value.trim();

    if (!foldername) {
        alert('Please enter a folder name');
        return;
    }

    // Apply context-aware defaults
    if (currentFileContext) {
        // If user didn't provide basePath, prepend it
        if (!foldername.startsWith(currentFileContext.basePath)) {
            foldername = currentFileContext.basePath + foldername;
        }
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
            currentFileContext = null;
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
        // First, get available database connections
        const connectionsResponse = await fetch('/__scribe_gui/api/database/connections');
        const connectionsData = await connectionsResponse.json();

        if (!connectionsData.connections || connectionsData.connections.length === 0) {
            console.error('No database connections available');
            return;
        }

        // Use 'default' connection if available, otherwise use first connection
        const connectionName = connectionsData.connections.includes('default')
            ? 'default'
            : connectionsData.connections[0];

        // Store current connection for use in loadTableData
        window.currentDbConnection = connectionName;

        // Now load tables for this connection
        const response = await fetch(`/__scribe_gui/api/database/${connectionName}/tables`);
        const data = await response.json();

        const select = document.getElementById('table-select');
        select.innerHTML = '<option value="">Select a table...</option>';

        if (data.tables) {
            data.tables.forEach(table => {
                const option = document.createElement('option');
                option.value = table;
                option.textContent = table;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading tables:', error);
    }
}

/**
 * Load table data
 */
async function loadTableData(tableName) {
    try {
        // Use the stored connection name (default to 'default' if not set)
        const connectionName = window.currentDbConnection || 'default';
        const response = await fetch(`/__scribe_gui/api/database/${connectionName}/table/${tableName}`);
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
