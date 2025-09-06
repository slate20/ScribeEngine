
This document outlines the final step in the GUI implementation plan: updating the PyInstaller build process to create a separate GUI executable that complements the existing CLI version.

## Objective

The goal is to modify the `build_engine.py` script so it can generate two distinct, single-file executables:

1. **A CLI Executable:** The standard `scribe-engine` that runs in the terminal, identical to the current version.
    
2. **A GUI Executable:** A new `scribe-engine-gui` that launches a native desktop window.
    

This approach ensures that both user groups—those who prefer the command line and those who prefer a GUI—are fully supported.

## Updating `build_engine.py`

The existing `build_engine.py` script already handles the PyInstaller process. We will add a simple conditional check to determine which executable to build based on a command-line argument.UId

### Step 1: Add a Command-Line Argument

We will use a simple `sys.argv` check to determine the build target.

```
# build_engine.py

... (existing imports)

def build_engine_executable():
    
    # Use 'cli' as the default build type
    build_type = 'cli'
    main_script_path = os.path.join(os.path.dirname(__file__), 'main_engine.py')
    name = 'scribe-engine'
    pyinstaller_options = []
    
    # Check for a 'gui' argument
    if len(sys.argv) > 1 and sys.argv[1] == 'gui':
        print("Building GUI Scribe Engine executable...")
        build_type = 'gui'
        main_script_path = os.path.join(os.path.dirname(__file__), 'gui_launcher.py')
        name = 'scribe-engine-gui'
        pyinstaller_options.append('--noconsole')
        
    ... (rest of the function)

```

This change sets the primary script (`main_script_path`) and the executable name based on the `gui` argument.

### Step 2: Include GUI-Specific Files

The GUI executable needs to bundle the new HTML, CSS, and JavaScript files. The `pyinstaller_args` list in `build_engine.py` must be updated to include these.

```
# build_engine.py

...

    # PyInstaller options
    pyinstaller_args = [
        main_script_path,
        '--onefile',
        f'--name={name}',
        f'--icon={os.path.join(script_dir, "SE_icon.png")}',
        
        # Add the existing core files
        f'--add-data={app_path}{os.pathsep}.',
        f'--add-data={build_py_path}{os.path.sep}.',
        f'--add-data={webview_wrapper_path}{os.path.sep}.',
        f'--add-data={config_manager_path}{os.path.sep}.',
        f'--add-data={engine_dir}{os.pathsep}engine',
        f'--add-data={templates_dir}{os.pathsep}templates',
        f'--add-data={static_dir}{os.pathsep}static',
        
        # Hidden imports
        '--hidden-import=flask',
        ...
    ]
    
    # If this is a GUI build, add the no-console option
    if build_type == 'gui':
        pyinstaller_args.append('--noconsole')
        # Add a custom hook to ensure the new HTML/JS files are included
        # PyInstaller's default --add-data should handle this, but for clarity...
        pyinstaller_args.append(f'--add-data={os.path.join(templates_dir, "launcher.html")}{os.path.sep}templates')
        pyinstaller_args.append(f'--add-data={os.path.join(templates_dir, "editor.html")}{os.path.sep}templates')
        pyinstaller_args.append(f'--add-data={os.path.join(templates_dir, "_fragments")}{os.path.sep}templates/_fragments')

    PyInstaller.__main__.run(pyinstaller_args)

    print(f"Scribe Engine {build_type} build completed. Executable can be found in the 'dist_engine' directory.")

...

```

## How to Build

Once the changes are in place, the build process will be as simple as running the following commands from the terminal:

### Building the CLI Executable

```
python build_engine.py

```

This will produce `scribe-engine-v{version}-{platform}` in the `dist_engine` folder.

### Building the GUI Executable

```
python build_engine.py gui

```

This will produce `scribe-engine-gui-v{version}-{platform}` in the `dist_engine` folder, ready for distribution.