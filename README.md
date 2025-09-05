# Scribe Engine - A Robust Text-Based Game Engine

<img width="1204" height="649" alt="Screenshot from 2025-09-05 13-54-54" src="https://github.com/user-attachments/assets/33785820-f0ba-4f94-851c-bcc802082469" />


Scribe Engine is a powerful and versatile text-based game engine designed for creating rich, interactive experiences. While perfectly capable of building simpler visual novels and interactive fiction, its core strength lies in empowering developers to craft more complex and dynamic games, overcoming the limitations often found in traditional story-authoring tools.

Leveraging Python for deep game logic, Jinja2 for flexible content rendering, and modern web technologies for a smooth player experience, Scribe Engine allows you to build intricate systems and responsive narratives without the constraints of page reloads or fragmented logic. It's built for creators who demand refined control over game mechanics, state management, and narrative flow, delivering a seamless and engaging experience for players.

## Get Started

To begin creating your visual novel, you'll need the Scribe Engine executable. This single, self-contained file contains everything you need to run the engine and build your games.

### 1. Download the Executable

Obtain the latest `scribe-engine` executable for your operating system (Windows or Linux) from the [Releases](https://github.com/your-github-username/scribe-engine/releases) page.

### 2. Run the Engine

Simply run the `scribe-engine` executable from your terminal or command line:

*   **Windows:** Double-click `scribe-engine.exe`.
*   **Linux:** Make the executable runnable (`chmod +x scribe-engine`) and then run `./scribe-engine`.

On the first run, the engine will prompt you to set a **Project Root** directory where all your game projects will be stored. This directory will be remembered for future sessions.

### 3. Create or Load a Project

Once the engine is running, you'll be presented with a menu. You can:

*   **Create New Project:** Set up a new game project with a basic structure. The engine will guide you through naming your project.
*   **Load Existing Project:** Select an existing game project from your Project Root to work on.

### 4. Start Development Server

After creating or loading a project, you'll enter the **Project Menu**. Choose **"Start Development Server"** to launch your game in a web browser (typically at `http://127.0.0.1:5000`). The engine features **live-reloading**, so changes to your game files will automatically update in your browser.

### 5. Build Your Game

When your game is ready for distribution, select **"Build Standalone Game"** from the **Project Menu**. The engine will package your game into a single executable file, located in the `dist/` folder next to your `scribe-engine` executable. This self-contained game can then be shared with players.

## Documentation

For detailed instructions on writing your story, managing game logic, customizing your game, and advanced features, please refer to the comprehensive [Scribe Engine Documentation](docs/Guide/0.%20Introduction.md).

## Contributing

Scribe Engine is open-source! If you're interested in contributing to the engine's development, please see the [CONTRIBUTING.md](CONTRIBUTING.md) file (coming soon) for guidelines and setup instructions.
