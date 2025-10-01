While the Scribe Engine IDE provides a powerful, all-in-one solution, some developers may prefer to use their own external code editors (like VS Code, Neovim, or Sublime Text) and command-line tools. The CLI (Command-Line Interface) workflow is designed for this purpose.

## When to Use the CLI Workflow

This workflow is ideal for developers who:

- Prefer their own configured code editor.
    
- Want to integrate Scribe Engine into a larger toolchain (e.g., using Git for version control).
    
- Are working in a team environment with specific development standards.
    
- Need to automate parts of the development or build process via scripts.
    

## The CLI Launcher

The core of this workflow is the CLI launcher (`main_engine.py` if running from source). It provides a menu-driven interface for managing your project from the terminal.

### Starting the CLI Launcher

```
# If running from source, navigate to the Scribe Engine directory
python3 main_engine.py
```

This will bring up the main menu with options for creating, opening, and managing projects.

## The Development Server

The most important feature for CLI development is the built-in web server. It runs your game and provides live reloading, so you can see your changes instantly in a web browser without needing the IDE's preview panel.

### Starting the Server

1. From the CLI launcher, open your project.
    
2. From the project menu, select **"Start Development Server"**.
    
3. The server will start, typically on `http://127.0.0.1:5000`.
    
4. Open this URL in your web browser to play and test your game.
    

Now, you can edit your project's files (`.tgame`, `.py`, `.css`) in your favorite editor. Every time you save a file, the development server will detect the change and automatically reload the game in your browser.

## External Editor Integration

You can enhance your experience by configuring your editor for Scribe Engine development.

### Visual Studio Code

We recommend telling VS Code to treat `.tgame` files as Markdown for good syntax highlighting. You can also add custom snippets.

1. Create a file at `.vscode/settings.json` in your project root:
```json
// .vscode/settings.json
{
    "files.associations": {
        "*.tgame": "markdown"
    },
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "files.autoSave": "onFocusChange"
}
```

2. Create a file at `.vscode/tgame.json` to add custom snippets for common Scribe Engine syntax:
```json
// .vscode/snippets/tgame.json
{
    "Passage": {
        "prefix": "passage",
        "body": [
            ":: ${1:passage_name}",
            "${2:Content goes here...}",
            "",
            "[[${3:Link text}->${4:target_passage}]]"
        ],
        "description": "Create a new passage"
    },
    "Python Block": {
        "prefix": "pyblock",
        "body": [
            "{$-",
            "${1:# Python code here}",
            "-$}"
        ],
        "description": "Multi-line Python block"
    },
    "Inline Python": {
        "prefix": "py",
        "body": [
            "{$ ${1:python_code} $}"
        ],
        "description": "Inline Python code"
    }
}
```

#### Vim/Neovim
Custom syntax highlighting for .tgame files:

```lua
" ~/.vim/syntax/tgame.vim
if exists("b:current_syntax")
  finish
endif

" Passage definitions
syntax match tgamePassage "^:: .*$"
highlight link tgamePassage Title

" Python blocks
syntax region tgamePythonBlock start="{$-" end="-$}" contains=@pythonTop
syntax region tgamePythonInline start="{$" end="$}" contains=@pythonTop
highlight link tgamePythonBlock Special
highlight link tgamePythonInline Special

" Template variables
syntax region tgameVariable start="{{" end="}}"
highlight link tgameVariable Identifier

" Template logic
syntax region tgameLogic start="{%" end="%}"
highlight link tgameLogic Statement

" Links
syntax region tgameLink start="\[\[" end="\]\]"
highlight link tgameLink Underlined

" Comments
syntax region tgameComment start="{#" end="#}"
highlight link tgameComment Comment

let b:current_syntax = "tgame"
```

Add to your `.vimrc`:
```vim
autocmd BufRead,BufNewFile *.tgame set filetype=tgame
```

---
## Building from the CLI

You can also build your game for distribution without using the IDE's "Build" button.

1. From the CLI launcher, open your project.
    
2. Select **"Build Game"** from the project menu.
    
3. The build process will run in the terminal, and the final distribution folder will be created in your project's `builds` directory, just as it would when using the IDE.
    

This feature is particularly useful for automation and continuous integration (CI/CD) pipelines.

## Version Control (Git)

The CLI workflow is perfect for use with version control systems like Git. Since all project files are plain text, they are easy to track.

### Recommended `.gitignore`

Create a `.gitignore` file in your project's root directory to prevent temporary files from being committed to your repository.

```
# Scribe Engine specific
saves/
builds/
debug.log

# Python cache
__pycache__/
*.pyc

# OS-specific
.DS_Store
Thumbs.db
```

This completes the Scribe Engine User Guide. You now have a comprehensive knowledge of how to create, test, and distribute sophisticated text-based games using either the integrated IDE or your own external development tools. Happy creating!
