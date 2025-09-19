# Scribe Engine - A Robust Text-Based Game Engine

<img width="1921" height="1080" alt="Screenshot from 2025-09-11 01-33-33" src="https://github.com/user-attachments/assets/db2c82bc-33c4-48e6-9bb1-fcd6f27dba3b" />




Scribe Engine is a powerful text-based game engine that makes creating interactive stories and visual novels effortless. With an integrated IDE featuring syntax highlighting, live preview, and lightning-fast builds, you can craft complex narratives without wrestling with external tools or complicated setup processes.

Built on Python for deep game logic, Jinja2 for dynamic content, and modern web technologies for smooth gameplay, Scribe Engine gives you professional development tools and the flexibility to create everything from simple interactive fiction to sophisticated narrative systems.

## Quick Start

Download the `scribe-engine` executable from [Releases](https://github.com/slate20/scribeengine/releases) and you're ready to go - no installation needed.

**Create Your First Game:**
1. Launch the engine and choose your project directory
2. Click "Create New Project" and name your game
3. Write your story in the integrated editor with live preview
4. Click "Build" for instant packaging for distribution (5-15 seconds)

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

## Development Experience

The Scribe Engine comes as a single executable that includes everything you need to create games. Most users will want the **GUI version** with the integrated development environment, though a **CLI version** is also available for developers who prefer working with external editors.

### Integrated Development Environment

The built-in IDE provides a complete development experience:
- **Syntax highlighting** for `.tgame` story files
- **Live preview** panel showing your game in real-time as you write
- **Debug terminal** displaying current game state and variables
- **Visual project management** with intuitive file organization
- **One-click builds** that package your game in seconds

### Lightning-Fast Distribution

Hit the "Build" button and your game is packaged into a standalone distribution in under 15 seconds. Players can run your games immediately without installing anything - just download and play.

## Documentation

For detailed instructions on writing your story, managing game logic, customizing your game, and advanced features, please refer to the comprehensive [User Documentation](https://github.com/slate20/ScribeEngine/wiki).

## Feedback & Discussions

If you want to offer any feedback, report issues, or just engage with other users and myself, head over to the [Discussions](https://github.com/slate20/ScribeEngine/discussions)!
