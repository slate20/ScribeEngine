import PyInstaller.__main__
import os
import sys

version = '1.0'

def build_engine_executable():
    # Determine platform for naming
    if sys.platform.startswith('linux'):
        platform_suffix = 'linux'
    elif sys.platform.startswith('win'):
        platform_suffix = 'windows'
    elif sys.platform.startswith('darwin'):  # macOS
        platform_suffix = 'macos'
    else:
        platform_suffix = 'unknown'

    # Determine the base directory of the project
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Check for command line argument to determine build type
    if len(sys.argv) > 1 and sys.argv[1] == 'gui':
        print("Building GUI Scribe Engine executable...")
        build_type = 'gui'
        main_script = 'gui_launcher.py'
        executable_name = f'scribe-engine-v{version}-{platform_suffix}'
        pyinstaller_options = ['--noconsole']
    else:
        print("Building CLI Scribe Engine executable...")
        build_type = 'cli'
        main_script = 'main_engine.py'
        executable_name = f'scribe-engine-cli-v{version}-{platform_suffix}'
        pyinstaller_options = []

    main_script_path = os.path.join(script_dir, main_script)

    # Define paths to include
    main_engine_path = os.path.join(script_dir, 'main_engine.py')
    gui_launcher_path = os.path.join(script_dir, 'gui_launcher.py')
    app_path = os.path.join(script_dir, 'app.py')
    engine_dir = os.path.join(script_dir, 'engine')
    templates_dir = os.path.join(script_dir, 'templates')
    static_dir = os.path.join(script_dir, 'static')
    game_server_path = os.path.join(script_dir, 'game_server.py')
    game_server_wrapper_path = os.path.join(script_dir, 'game_server_wrapper.py')
    config_manager_path = os.path.join(script_dir, 'config_manager.py')
    loading_window_path = os.path.join(script_dir, 'loading_window.py')
    build_standalone_path = os.path.join(script_dir, 'build_standalone.py')

    # Standalone builder executable path (platform-specific)
    if sys.platform.startswith('linux'):
        builder_name = 'ScribeBuilder-linux'
    elif sys.platform.startswith('win'):
        builder_name = 'ScribeBuilder-windows.exe'
    elif sys.platform.startswith('darwin'):
        builder_name = 'ScribeBuilder-macos'
    else:
        builder_name = 'ScribeBuilder-unknown'

    standalone_builder_path = os.path.join(script_dir, 'dist_tools', builder_name)

    # Check if standalone builder exists
    if not os.path.exists(standalone_builder_path):
        print(f"Warning: Standalone builder not found at {standalone_builder_path}")
        print(f"Run 'python build_build_tool.py' to create the standalone builder first.")
        print("Continuing without bundled builder...")
        standalone_builder_path = None

    # PyInstaller arguments
    pyinstaller_args = [
        main_script_path,
        '--onefile',
        f'--name={executable_name}',
        f'--icon={script_dir}/SE_icon.png',

        # Add Python source files that are imported dynamically or needed
        f'--add-data={main_engine_path}{os.pathsep}.',
        f'--add-data={gui_launcher_path}{os.pathsep}.',
        f'--add-data={app_path}{os.pathsep}.',
        f'--add-data={game_server_path}{os.pathsep}.',
        f'--add-data={game_server_wrapper_path}{os.pathsep}.',
        f'--add-data={config_manager_path}{os.pathsep}.',
        f'--add-data={loading_window_path}{os.pathsep}.',
        f'--add-data={build_standalone_path}{os.pathsep}.',

        # Add directories
        f'--add-data={engine_dir}{os.pathsep}engine',
        f'--add-data={templates_dir}{os.pathsep}templates',
        f'--add-data={static_dir}{os.pathsep}static',

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

        # Specify where to put the dist and build folders
        '--distpath=./dist_engine',
        '--workpath=./build_engine',
        '--specpath=./spec_engine',
    ]

    # Add standalone builder if it exists
    if standalone_builder_path and os.path.exists(standalone_builder_path):
        pyinstaller_args.append(f'--add-data={standalone_builder_path}{os.pathsep}tools')
        print(f"Including standalone builder: {builder_name}")

    # Add conditional options (like --noconsole for GUI)
    pyinstaller_args.extend(pyinstaller_options)

    PyInstaller.__main__.run(pyinstaller_args)

    print(f"Scribe Engine {build_type} build completed. Executable can be found in the 'dist_engine' directory.")

if __name__ == '__main__':
    build_engine_executable()

