This guide will walk you through the initial steps of downloading the PyVN engine, configuring your workspace, and creating a new game project.

### Obtaining the PyVN Engine

The PyVN engine is distributed as a single, self-contained executable for Windows and Linux. You do not need to install Python or any dependencies separately.

- **Download:** Obtain the latest `pyvn-engine` executable for your operating system from the official distribution channels (e.g., GitHub releases).
    

### Running the Engine

Simply run the `pyvn-engine` executable from your terminal or command line.

- **Windows:** Double-click `pyvn-engine.exe`.
    
- **Linux:** Make the executable runnable (`chmod +x pyvn-engine`) and then run `./pyvn-engine`.
    

### First-Run Experience: Setting Your Project Root

The first time you run `pyvn-engine`, it will prompt you to set a directory where all your game projects will be stored. This is your "project root."

```
No project root configured or found. Please specify one.
Enter the path for your PyVN game projects (e.g., ~/PyVN_Games):
```

Enter an absolute path (e.g., `/home/youruser/PyVN_Games` on Linux, or `C:\Users\YourUser\Documents\PyVN_Games` on Windows). The engine will create this directory if it doesn't exist and remember it for future sessions.

You can override this path for a single session using the `--project-root` or `-r` argument:

```
./pyvn-engine --project-root /path/to/another/games/folder
```

### Main Menu Options

Once the engine is running, you'll see the main menu:

```
--- PyVN Engine Launcher (Project Root: /path/to/your/PyVN_Games) ---

Options:
1. Create New Project
2. Load Existing Project
3. Build Standalone Game
4. Change Project Root Path
5. Exit
```

- **1. Create New Project:** Guides you through creating a new game with a basic skeleton structure.
    
- **2. Load Existing Project:** Lists projects in your project root and lets you select one to run for development. This starts the local web server.
    
- **3. Build Standalone Game:** Packages an existing game project into a distributable executable.
    
- **4. Change Project Root Path:** Prompts you to set a new default directory for your game projects.
    
- **5. Exit:** Closes the engine.