import PyInstaller.__main__
import os
import sys

version = '1.0'

def build_engine_executable():

    # Default to a console application
    build_type = 'cli'
    pyinstaller_options = []

    # Check for command line argument
    if len(sys.argv) > 1 and sys.argv[1] == 'gui':
        print("Building GUI Scribe Engine executable...")
        build_type = 'gui'
        pyinstaller_options.append('--noconsole')
    else:
        print("Building CLI Scribe Engine executable...")
    
    # Determine the base directory of the project
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define paths to include
    main_engine_path = os.path.join(script_dir, 'main_engine.py')
    app_path = os.path.join(script_dir, 'app.py')
    engine_dir = os.path.join(script_dir, 'engine')
    templates_dir = os.path.join(script_dir, 'templates')
    static_dir = os.path.join(script_dir, 'static')
    config_py_path = os.path.join(script_dir, 'config.py')
    webview_wrapper_path = os.path.join(script_dir, 'webview_wrapper.py')
    build_py_path = os.path.join(script_dir, 'build.py')
    config_manager_path = os.path.join(script_dir, 'config_manager.py')

    # Determine platform for naming
    if sys.platform.startswith('linux'):
        platform_suffix = 'linux'
    elif sys.platform.startswith('win'):
        platform_suffix = 'windows'
    elif sys.platform.startswith('darwin'): # macOS
        platform_suffix = 'macos'
    else:
        platform_suffix = 'unknown'

    # PyInstaller options
    # --noconsole: Do not open a console window (for GUI apps)
    # --onefile: Create a single executable file
    # --name: Name of the executable
    # --add-data: Add non-binary files or folders to the executable
    # Format: <source_path><os.pathsep><destination_path_in_bundle>
    
    # The destination path in bundle should be relative to the executable's root
    # For example, if you add 'templates' folder, it will be accessible as 'templates' in the bundle

    pyinstaller_args = [
        main_engine_path,  # Main script to execute
        '--onefile',           # Create a single executable file
        f'--name=scribe-engine-v{version}-{platform_suffix}',  # Name of the executable
        f'--icon={script_dir}/SE_icon.png',
        
        # Add Python source files that are imported dynamically or needed by other parts
        f'--add-data={app_path}{os.pathsep}.',
        f'--add-data={build_py_path}{os.pathsep}.',
        f'--add-data={webview_wrapper_path}{os.pathsep}.',
        f'--add-data={config_manager_path}{os.pathsep}.',

        # Add directories
        f'--add-data={engine_dir}{os.pathsep}engine',
        f'--add-data={templates_dir}{os.pathsep}templates',
        f'--add-data={static_dir}{os.pathsep}static',
        
        # Add config.py (if it's a separate file and not just part of app.py)
        

        # Hidden imports for modules that PyInstaller might miss
        '--hidden-import=flask',
        '--hidden-import=jinja2',
        '--hidden-import=werkzeug',
        '--hidden-import=pywebview',
        '--hidden-import=pywebview.platforms.qt',
        '--hidden-import=qtpy',
        '--hidden-import=qtpy.QtCore',
        '--hidden-import=qtpy.QtGui',
        '--hidden-import=qtpy.QtWidgets',
        
        # Optional: Specify where to put the dist and build folders
        '--distpath=./dist_engine',
        '--workpath=./build_engine',
        '--specpath=./spec_engine',
    ]

    # add the conditional options to the main list
    pyinstaller_args.extend(pyinstaller_options)

    # If running on Linux, you might want to include a custom icon
    # if sys.platform.startswith('linux'):
    #     pyinstaller_args.append('--icon=path/to/your/icon.png')

    PyInstaller.__main__.run(pyinstaller_args)

    print(f"Scribe Engine {build_type} build completed. Executable can be found in the 'dist_engine' directory.")

if __name__ == '__main__':
    build_engine_executable()
