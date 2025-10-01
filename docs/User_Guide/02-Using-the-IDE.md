This guide covers all aspects of the Scribe Engine Integrated Development Environment (IDE), your primary tool for creating, testing, and distributing games.

## IDE Overview

The IDE is designed to provide everything you need in one window. It has four main components:


1. **Header Bar** - High-level project actions like building and closing.
    
2. **Sidebar** - File management and project settings.
    
3. **Editor Panel** - Where you write your story and code.
    
4. **Preview Panel** - A live, playable version of your game.
    

## Header Bar

The header bar provides quick access to essential functions.

- **Project Info**: Displays the name and file path of your current project.
    
- **Theme Toggle**: Switches the IDE between light and dark modes.
    
- **Open in Browser**: Opens your game in your default web browser for testing outside the IDE.
    
- **Preview Toggle**: Shows or hides the Preview Panel to maximize editor space.
    
- **Build Game**: Packages your game into a standalone executable for distribution. This creates a `builds` folder in your project directory containing a distribution-ready folder.
    
- **Project Actions**: A dropdown menu to **Reset Game State** (clearing all progress) or **Close Project**.
    

## Sidebar

The sidebar has two tabs for managing your project.


### Files Tab

This tab organizes all your project's files. Use the **+** button in each section to create new files and the **X** button to delete them.

- **Story Files (.tgame)**: Your primary game files containing passages, logic, and text.
    
- **Game Logic (.py)**: Optional Python files for creating complex, reusable systems (e.g., a combat engine or a custom player class).
    
- **Styling (.css)**: CSS files to customize your game's appearance.
    
- **Assets**: Your game's media, such as images, music, and sound effects.
    
    - ***NOTE*** Assets will need to be added to this directory on your device. When you open a project, any files found will show in this section and can be clicked on to copy the path for use in passages.
        

### Settings Tab

This tab allows you to configure your project's metadata and features. Key settings include:

- **Game Title / Author**: The metadata for your game.
    
- **Starting Passage**: The passage where the game begins.
    
- **Features**: Toggles for engine features like the default player object.
    
- **Development**: Toggles for debug mode.
    

## Editor Panel

This is where you'll do most of your writing and coding.


### Syntax Highlighting

The editor automatically color-codes your `.tgame` files to make them easy to read:

- **Passage Definitions**: `:: passage_name`
    
- **Python Code**: `{$ ... $}` and `{$- ... -$}`
    
- **Template Variables**: `{{ variable }}`
    
- **Template Logic**: `{% if ... %}`
    
- **Links**: `[[ text->target ]]`

- **Action Buttons**: `<<text||{$ ... $}>>`
    
- **Comments**: `{# comment #}`
    
- **HTML** will also have syntax highlighting
    

### Keyboard Shortcuts

- **Ctrl+S**: Save current file.
    
- **Ctrl+F**: Find text.
    
- **Ctrl+H**: Find and replace.
    
- **Tab / Shift+Tab**: Indent or unindent lines.
    

## Preview Panel

The preview panel provides a live, real-time version of your game.


### Live Preview

- **Instant Updates**: The preview automatically refreshes every time you save a file.
    
- **Full Interactivity**: You can click links and play your game exactly as a player would.
    
- **Error Display**: If you make a syntax error, the error message will be displayed in the preview if debug_mode is enabled.
    

### Debug Terminal

At the bottom of the preview is the debug terminal, one of the most powerful features of the IDE. It shows you the current value of **every variable** in your game in real-time.

- **State Visualization**: Watch variables change as you click links and progress through your story.
    
- **Object Inspection**: Expand objects (like the `player` object) to see all their properties.
    
- **Troubleshooting**: Instantly see if a variable isn't being set correctly or if a calculation is wrong.
    

## Building and Distributing Your Game

Once your game is ready to share, the IDE makes it simple to package it for distribution.

### The Build Process

1. Click the **"Build"** button in the IDE's header bar.
    
2. A progress window will appear, showing the status of the build. This process typically takes 10-20 seconds.
    
3. Once complete, a link to the output folder will be shown.
    

### Distribution Contents

The build process creates a distribution folder inside your project directory (in a new folder named `builds`). This folder contains:

- **YourGameTitle.exe** (or an equivalent for your OS): The standalone executable file for your game.
    
- **game.dat**: A file containing all your project's compressed and packaged assets (`.tgame` files, Python code, images, etc.).
    

### Sharing Your Game

To share your game with others:

1. Zip the **entire distribution folder**.
    
2. Share the resulting `.zip` file.
    

Players can then unzip the folder on their own computer and run the executable to play your game. No installation is required.

**Next:** You're now familiar with the tools. Let's dive deep into the syntax for creating your story. Continue to [**Game Structure and Syntax**](3.-Game-Structure-and-Syntax).