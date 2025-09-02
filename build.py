import PyInstaller.__main__
import os
import sys

# --- Helper function for building standalone game executables ---
def build_standalone_game(project_name: str, project_root_dir: str):
    print(f"Building standalone executable for project: {project_name}")

    # Determine the absolute path to the specific game project directory
    project_absolute_path = os.path.join(project_root_dir, project_name)

    # Determine the base directory for the engine's bundled files
    # This will be sys._MEIPASS when running from the main engine executable
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_base_dir = sys._MEIPASS
    else:
        bundle_base_dir = os.path.dirname(os.path.abspath(__file__))

    # Define paths to include relative to the bundle_base_dir
    engine_path = os.path.join(bundle_base_dir, 'engine')
    templates_path = os.path.join(bundle_base_dir, 'templates')
    static_path = os.path.join(bundle_base_dir, 'static')
    config_path = os.path.join(bundle_base_dir, 'config.py')
    app_path = os.path.join(bundle_base_dir, 'app.py')
    webview_wrapper_path = os.path.join(bundle_base_dir, 'webview_wrapper.py')

    # PyInstaller options
    # --noconsole: Do not open a console window (for GUI apps)
    # --onefile: Create a single executable file
    # --name: Name of the executable
    # --add-data: Add non-binary files or folders to the executable
    # Format: <source_path><os.pathsep><destination_path_in_bundle>
    
    # The destination path in bundle should be relative to the executable's root
    # For example, if you add 'templates' folder, it will be accessible as 'templates' in the bundle

    pyinstaller_args = [
        webview_wrapper_path,  # Main script to execute
        '--noconsole',         # For GUI application
        '--onefile',           # Create a single executable file
        f'--name={project_name}_game', # Name of the executable
        
        # Add data files/folders
        f'--add-data={engine_path}{os.pathsep}engine',
        f'--add-data={templates_path}{os.pathsep}templates',
        f'--add-data={static_path}{os.pathsep}static',
        f'--add-data={config_path}{os.pathsep}.',
        f'--add-data={app_path}{os.pathsep}.',
        
        # Add the specific game project being built
        f'--add-data={project_absolute_path}{os.pathsep}game_data/{project_name}',
        
        # Optional: Specify where to put the dist and build folders
        '--distpath=./dist',
        '--workpath=./build',
        '--specpath=./spec',
    ]

    # If running on Linux, you might want to include a custom icon
    # if sys.platform.startswith('linux'):
    #     pyinstaller_args.append('--icon=path/to/your/icon.png')

    PyInstaller.__main__.run(pyinstaller_args)

    print(f"Build process for {project_name} completed. Executable can be found in the 'dist' directory.")
