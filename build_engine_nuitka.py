#!/usr/bin/env python3
"""
Nuitka-based build script for Scribe Engine executables.
This replaces PyInstaller with Nuitka for better performance and to enable integrated building.
"""

import subprocess
import os
import sys
import shutil

version = '2.0'

def build_engine_executable():
    """Build Scribe Engine executable using Nuitka."""

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
        print("Building GUI Scribe Engine executable with Nuitka...")
        build_type = 'gui'
        main_script = 'gui_launcher.py'
        executable_name = f'scribe-engine-v{version}-{platform_suffix}'
        # Only disable console on Windows
        nuitka_options = ['--disable-console'] if sys.platform.startswith('win') else []
    else:
        print("Building CLI Scribe Engine executable with Nuitka...")
        build_type = 'cli'
        main_script = 'main_engine.py'
        executable_name = f'scribe-engine-cli-v{version}-{platform_suffix}'
        nuitka_options = []  # Keep console for CLI

    main_script_path = os.path.join(script_dir, main_script)

    # Clean up previous builds
    dist_dir = './dist_engine_nuitka'
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir, exist_ok=True)

    # Define paths to include
    engine_dir = os.path.join(script_dir, 'engine')
    templates_dir = os.path.join(script_dir, 'templates')
    static_dir = os.path.join(script_dir, 'static')

    # Nuitka command arguments (use current Python interpreter)
    nuitka_args = [
        sys.executable, '-m', 'nuitka',
        main_script_path,
        '--standalone',
        '--onefile',
        f'--output-filename={executable_name}',
        f'--output-dir={dist_dir}',

        # Enable PyWebview and PyQt6 plugins for desktop integration
        '--plugin-enable=pywebview',
        '--plugin-enable=pyqt6',

        # Include data directories
        f'--include-data-dir={engine_dir}=engine',
        f'--include-data-dir={templates_dir}=templates',
        f'--include-data-dir={static_dir}=static',

        # Include additional Python files needed by the engine
        f'--include-module=app',
        f'--include-module=config_manager',
        f'--include-module=loading_window',

        # Performance optimizations
        '--lto=yes',  # Link Time Optimization for better performance
        '--assume-yes-for-downloads',  # Auto-download dependencies

        # Python flags for optimization
        '--python-flag=no_warnings',
        '--python-flag=no_asserts',
    ]

    # Add conditional options
    nuitka_args.extend(nuitka_options)

    # Add icon if available (convert PNG to ICO for Windows)
    icon_path = os.path.join(script_dir, 'SE_icon.png')
    if os.path.exists(icon_path) and sys.platform.startswith('win'):
        nuitka_args.extend([f'--windows-icon-from-ico={icon_path}'])

    print(f"Running Nuitka with command:")
    print(" ".join(nuitka_args))
    print()

    try:
        # Run Nuitka compilation
        result = subprocess.run(nuitka_args, check=True, capture_output=True, text=True)

        print("Nuitka compilation completed successfully!")
        print(f"Executable: {os.path.join(dist_dir, executable_name)}")

        # Display executable size
        exe_path = os.path.join(dist_dir, executable_name)
        if sys.platform.startswith('win') and not exe_path.endswith('.exe'):
            exe_path += '.exe'

        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) // (1024 * 1024)
            print(f"Size: {size_mb} MB")

        print(f"\nScribe Engine {build_type} build completed successfully!")
        print(f"Executable can be found in the '{dist_dir}' directory.")

        return True

    except subprocess.CalledProcessError as e:
        print(f"Nuitka compilation failed with return code {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"Build error: {e}")
        return False

if __name__ == '__main__':
    success = build_engine_executable()
    sys.exit(0 if success else 1)
