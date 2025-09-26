#!/usr/bin/env python3
"""
Build ScribePlayer.exe - Universal Game Runtime
Creates a standalone executable that can load and run obfuscated game archives.
"""

import PyInstaller.__main__
import os
import sys


def build_scribe_player():
    """Build the ScribePlayer.exe executable."""
    print("Building ScribePlayer.exe...")

    # Determine platform for naming
    if sys.platform.startswith('linux'):
        platform_suffix = 'linux'
        exe_extension = ''
    elif sys.platform.startswith('win'):
        platform_suffix = 'windows'
        exe_extension = '.exe'
    elif sys.platform.startswith('darwin'):  # macOS
        platform_suffix = 'macos'
        exe_extension = ''
    else:
        platform_suffix = 'unknown'
        exe_extension = ''

    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define paths
    game_server_path = os.path.join(script_dir, 'game_server.py')
    webview_wrapper_path = os.path.join(script_dir, 'webview_wrapper.py')
    engine_dir = os.path.join(script_dir, 'engine')
    templates_dir = os.path.join(script_dir, 'templates')
    static_dir = os.path.join(script_dir, 'static')

    # Check required files exist
    required_files = [game_server_path, engine_dir, templates_dir, static_dir]
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"Error: Required file/directory not found: {file_path}")
            return False

    # Create player launcher script
    launcher_content = '''#!/usr/bin/env python3
"""
ScribePlayer - Universal Scribe Engine Game Runtime
Loads and runs obfuscated game archives (.dat files).
"""

import os
import sys
import json
import threading
import time
from datetime import datetime

# Add the base directory to Python path for imports
if getattr(sys, 'frozen', False):
    # Running from PyInstaller bundle
    base_dir = sys._MEIPASS
    executable_dir = os.path.dirname(sys.executable)
else:
    # Running from source
    base_dir = os.path.dirname(os.path.abspath(__file__))
    executable_dir = base_dir

sys.path.insert(0, base_dir)

# Global installer for on-demand loading
game_installer = None

# Import required modules
try:
    import webview
    from game_server import app as game_app, set_game_project_path
    from engine.asset_packer import load_game_archive, is_game_archive
except ImportError as e:
    print(f"Error importing required modules: {e}")
    input("Press Enter to exit...")
    sys.exit(1)


def find_game_archive():
    """Find game.dat file in the executable directory."""
    game_dat_path = os.path.join(executable_dir, 'game.dat')

    if os.path.exists(game_dat_path) and is_game_archive(game_dat_path):
        return game_dat_path

    # Also check for other .dat files
    for file in os.listdir(executable_dir):
        if file.endswith('.dat'):
            file_path = os.path.join(executable_dir, file)
            if is_game_archive(file_path):
                return file_path

    return None


def setup_game_installation():
    """Setup game installation - install if needed, then extract to temp directory."""
    archive_path = find_game_archive()

    if not archive_path:
        print("Error: No game.dat archive found!")
        print(f"Expected in: {executable_dir}")
        return None

    print(f"Found game archive: {archive_path}")

    # Initialize installer
    from engine.game_installer import GameInstaller
    installer = GameInstaller(executable_dir, archive_path)

    # Check if installation is needed
    if not installer.is_installed() or installer.needs_reinstall():
        print("First launch detected - installing game...")

        try:
            # Run installation with UI
            success = installer.run_installation(show_ui=True)
            if not success:
                print("Installation failed or was cancelled.")
                return None

            print("Game installation completed successfully!")

        except Exception as e:
            print(f"Installation error: {e}")
            return None

    else:
        print("Game already installed - validating installation...")

        # Validate existing installation
        if not installer.validate_installation():
            print("Installation validation failed - repairing...")

            try:
                # Attempt repair with UI
                root = installer.create_installer_ui()
                installer.status_var.set("Repairing installation...")

                # Repair in background thread
                repair_success = False
                repair_complete = False

                def repair_thread():
                    nonlocal repair_success, repair_complete
                    try:
                        repair_success = installer.repair_installation(installer.update_progress)
                    finally:
                        repair_complete = True

                import threading
                thread = threading.Thread(target=repair_thread, daemon=True)
                thread.start()

                # Wait for repair to complete
                while not repair_complete:
                    try:
                        root.update_idletasks()
                        root.update()
                        time.sleep(0.05)
                    except Exception:
                        break

                root.destroy()

                if not repair_success:
                    print("Installation repair failed.")
                    return None

                print("Installation repaired successfully!")

            except Exception as e:
                print(f"Repair error: {e}")
                return None

        else:
            print("Installation validated successfully - loading game...")

    # Store installer globally for file loading
    global game_installer
    game_installer = installer

    # Now extract installed files to temp directory for the game engine
    return extract_installed_files_to_temp(installer)


def extract_installed_files_to_temp(installer):
    """Extract installed files to temporary directory for game engine."""
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix='scribe_game_')

    try:
        print("Loading installed game files...")

        # Get file mapping from installation
        file_mapping = installer.get_installed_files_mapping()

        if not file_mapping:
            print("Error: No installed files found!")
            return None

        # Load and extract each file
        extracted_count = 0
        for original_path in file_mapping.keys():
            file_data = installer.load_installed_file(original_path)
            if file_data is None:
                continue

            full_path = os.path.join(temp_dir, original_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Determine write mode based on file extension
            if original_path.endswith(('.tgame', '.json', '.py', '.css', '.txt', '.md')):
                # Text files
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(file_data.decode('utf-8'))
            else:
                # Binary files
                with open(full_path, 'wb') as f:
                    f.write(file_data)

            extracted_count += 1

        print(f"Extracted {extracted_count} files from installation to: {temp_dir}")
        return temp_dir

    except Exception as e:
        print(f"Error extracting installed files: {e}")
        print("Attempting fallback to direct archive extraction...")

        # Fallback to direct archive loading
        try:
            archive_path = find_game_archive()
            files = load_game_archive(archive_path)

            for file_path, file_data in files.items():
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                if file_path.endswith(('.tgame', '.json', '.py', '.css', '.txt', '.md')):
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(file_data.decode('utf-8'))
                else:
                    with open(full_path, 'wb') as f:
                        f.write(file_data)

            print(f"Fallback: Extracted {len(files)} files to: {temp_dir}")
            return temp_dir

        except Exception as fallback_e:
            print(f"Fallback extraction also failed: {fallback_e}")
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None


def load_installed_file_on_demand(file_path):
    """Load file on-demand from installation."""
    global game_installer

    if game_installer:
        try:
            return game_installer.load_installed_file(file_path)
        except Exception:
            pass

    return None


def start_game_server(project_path):
    """Start the game server."""
    try:
        set_game_project_path(project_path)
        game_app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Error starting game server: {e}")
        sys.exit(1)


def get_game_title(project_path):
    """Get game title from project.json."""
    try:
        config_path = os.path.join(project_path, 'project.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('title', 'Scribe Engine Game')
    except Exception:
        pass
    return 'Scribe Engine Game'


def main():
    """Main entry point for the ScribePlayer."""
    print("ScribePlayer - Universal Scribe Engine Runtime")
    print("=" * 50)

    # Setup game installation and extract to temp
    project_path = setup_game_installation()
    if not project_path:
        input("Press Enter to exit...")
        sys.exit(1)

    game_title = get_game_title(project_path)
    print(f"Starting: {game_title}")

    # Start the game server in a separate thread
    server_thread = threading.Thread(target=start_game_server, args=(project_path,), daemon=True)
    server_thread.start()

    # Give the server a moment to start
    time.sleep(2)

    # Create and start the webview window
    try:
        webview.create_window(
            game_title,
            'http://127.0.0.1:5001',
            width=1024,
            height=768,
            resizable=True,
            min_size=(800, 600)
        )
        webview.start()
    except Exception as e:
        print(f"Error starting game window: {e}")
        print("You can play the game by opening http://127.0.0.1:5001 in your web browser")
        input("Press Enter to exit...")

    # Cleanup
    try:
        import shutil
        shutil.rmtree(project_path, ignore_errors=True)
    except Exception:
        pass


if __name__ == "__main__":
    main()
'''

    # Write launcher script
    launcher_path = os.path.join(script_dir, 'scribe_player_launcher.py')
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)

    # Check if webview_wrapper.py exists, if not create a simple one
    if not os.path.exists(webview_wrapper_path):
        webview_content = '''"""Simple webview wrapper for compatibility."""
import webview

def create_window(*args, **kwargs):
    return webview.create_window(*args, **kwargs)

def start():
    return webview.start()
'''
        with open(webview_wrapper_path, 'w') as f:
            f.write(webview_content)

    executable_name = f'ScribePlayer{exe_extension}'

    # PyInstaller arguments
    pyinstaller_args = [
        launcher_path,
        '--onefile',
        f'--name={executable_name}',
        f'--icon={script_dir}/SE_icon.png',

        # Add game server and required Python files
        f'--add-data={game_server_path}{os.pathsep}.',

        # Add engine directory
        f'--add-data={engine_dir}{os.pathsep}engine',

        # Add templates and static directories
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
        '--hidden-import=markupsafe',

        # Output directories
        '--distpath=./dist_tools',
        '--workpath=./build_player',
        '--specpath=./spec_player',

        # Additional options
        '--noconsole',  # No console window for games
        '--clean',
        '--noconfirm'
    ]

    try:
        PyInstaller.__main__.run(pyinstaller_args)

        player_path = os.path.join(script_dir, 'dist_tools', executable_name)
        if os.path.exists(player_path):
            size_mb = os.path.getsize(player_path) // (1024 * 1024)
            print(f"✓ ScribePlayer build completed successfully!")
            print(f"  Executable: {player_path}")
            print(f"  Size: {size_mb} MB")

            # Clean up temporary launcher
            try:
                os.remove(launcher_path)
            except Exception:
                pass

            return True
        else:
            print("✗ Build completed but executable not found!")
            return False

    except Exception as e:
        print(f"✗ Build failed: {e}")
        return False

    finally:
        # Clean up temporary launcher if it exists
        try:
            if os.path.exists(launcher_path):
                os.remove(launcher_path)
        except Exception:
            pass


if __name__ == '__main__':
    success = build_scribe_player()
    if success:
        print("\n" + "=" * 60)
        print("ScribePlayer.exe built successfully!")
        print("This executable can now run any Scribe Engine game archive.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Build failed! Check error messages above.")
        print("=" * 60)
        sys.exit(1)