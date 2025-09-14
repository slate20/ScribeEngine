# Scribe Engine - A Robust Text-Based Game Engine

<img width="1921" height="1080" alt="Screenshot from 2025-09-11 01-33-33" src="https://github.com/user-attachments/assets/db2c82bc-33c4-48e6-9bb1-fcd6f27dba3b" />




Scribe Engine is a powerful and versatile text-based game engine designed for creating rich, interactive experiences. Featuring an integrated IDE with syntax highlighting, live preview, and one-click builds, it empowers developers to craft complex visual novels and interactive fiction without external tools or setup complexity.

Leveraging Python for deep game logic, Jinja2 for flexible content rendering, and modern web technologies for smooth gameplay, Scribe Engine allows you to build intricate systems and responsive narratives with professional development tools built right in. It's designed for creators who demand both powerful functionality and an intuitive development experience.

## Quick Start

**Get the Engine:** Download the latest `scribe-engine` executable from [Releases](https://github.com/your-github-username/scribe-engine/releases) - no installation required.

**Create Your First Game:**
1. Launch the engine and set your project directory
2. Click "Create New Project" and name your game
3. Start writing in the integrated editor with live preview
4. Click "Build" for instant distribution (5-15 seconds)

**Basic Story Format:**
```
:: Start
Welcome to your adventure! What's your name?

{$ player_name = "Hero" $}

Hello, {{player_name}}! Your journey begins...

[[Enter the forest->Forest]]
[[Visit the town->Town]]

:: Forest
{$ player.health = 100 $}
You venture into the dark forest...
```

## Get Started

To begin creating your game, you'll need the Scribe Engine executable. This single, self-contained file includes an integrated development environment with everything you need to create and build your games.

### 1. Download & Launch

Download the `scribe-engine` executable for your platform and run it directly. The engine will guide you through setting up your project directory on first run.

### 2. Create Your Project

Use the integrated interface to create a new project or load an existing one. The engine provides starter templates and handles all project structure setup automatically.

### 3. Develop with Integrated IDE

Write your story using the built-in editor featuring:
- **Syntax highlighting** for `.tgame` story files
- **Live preview** panel showing your game in real-time
- **Debug terminal** displaying current game state and variables
- **Project management** with visual file organization

### 4. Build & Distribute

Click the **"Build"** button to instantly package your game (5-15 seconds). The engine creates a standalone distribution in your project's `builds/` folder that players can run without any additional setup.

## Documentation

For detailed instructions on writing your story, managing game logic, customizing your game, and advanced features, please refer to the comprehensive [User Documentation](https://github.com/slate20/ScribeEngine/wiki).