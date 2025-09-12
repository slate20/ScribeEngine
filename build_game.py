import PyInstaller.__main__
import os
import sys
import json
import shutil
from datetime import datetime
from PIL import Image

# Global reference to active builds for progress updates
# This will be set by the calling module (app.py)
active_builds = None
build_status_lock = None

def set_build_status_globals(builds_dict, lock):
    """Set references to the global build status tracking from app.py"""
    global active_builds, build_status_lock
    active_builds = builds_dict
    build_status_lock = lock

def update_build_progress(project_name: str, progress_message: str):
    """Update the build progress for a project"""
    if active_builds is not None and build_status_lock is not None:
        with build_status_lock:
            if project_name in active_builds:
                active_builds[project_name]['progress'] = progress_message

def disable_debug_mode_for_build(project_path: str):
    """
    Temporarily disable debug mode in project.json for the build.
    Returns the original debug_mode value and backup file path if changes were made.
    """
    project_config_path = os.path.join(project_path, 'project.json')
    backup_path = os.path.join(project_path, 'project.json.build_backup')
    
    if not os.path.exists(project_config_path):
        return None, None
    
    try:
        # Read the current project configuration
        with open(project_config_path, 'r') as f:
            config = json.load(f)
        
        # Check if debug mode is currently enabled
        original_debug_mode = config.get('debug_mode', False)
        
        if original_debug_mode:
            # Create a backup of the original config
            shutil.copy2(project_config_path, backup_path)
            print(f"Debug mode was enabled - temporarily disabling for production build")
            
            # Disable debug mode
            config['debug_mode'] = False
            
            # Write the modified config
            with open(project_config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            return original_debug_mode, backup_path
        else:
            print(f"Debug mode already disabled - no changes needed")
        
        return original_debug_mode, None
        
    except Exception as e:
        print(f"Warning: Could not modify debug mode setting: {e}")
        return None, None

def restore_debug_mode_after_build(backup_path: str):
    """Restore the original project.json from backup after build completion"""
    if backup_path and os.path.exists(backup_path):
        try:
            # Get the original project.json path
            original_path = backup_path.replace('.build_backup', '')
            
            # Restore the backup
            shutil.move(backup_path, original_path)
            print("Debug mode setting restored to original state")
            
        except Exception as e:
            print(f"Warning: Could not restore original debug mode setting: {e}")

def convert_image_to_ico(image_path: str, project_path: str) -> str:
    """
    Convert an image file to .ico format for use with PyInstaller.
    Returns the path to the converted .ico file.
    """
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Convert to RGBA if not already (for transparency support)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Generate output path for the .ico file
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            ico_path = os.path.join(project_path, f"{base_name}_converted.ico")
            
            # Create multiple icon sizes (standard Windows icon sizes)
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            
            # Resize image to different sizes
            images = []
            for size in icon_sizes:
                resized_img = img.resize(size, Image.Resampling.LANCZOS)
                images.append(resized_img)
            
            # Save as .ico with multiple sizes
            images[0].save(ico_path, format='ICO', sizes=[img.size for img in images])
            
            print(f"Converted {os.path.basename(image_path)} to {os.path.basename(ico_path)}")
            return ico_path
            
    except Exception as e:
        print(f"Error converting image to .ico: {e}")
        return None

def cleanup_old_build_artifacts(project_path: str, project_name: str):
    """Remove old build, dist, and spec directories to prevent build conflicts"""
    artifacts_to_clean = [
        os.path.join(project_path, 'build'),
        os.path.join(project_path, 'dist'), 
        os.path.join(project_path, 'spec'),
        os.path.join(project_path, f'{project_name}_game.spec')  # PyInstaller spec file
    ]
    
    # Also clean up any converted .ico files from previous builds
    try:
        for file in os.listdir(project_path):
            if file.endswith('_converted.ico'):
                artifacts_to_clean.append(os.path.join(project_path, file))
    except OSError:
        pass  # Directory might not exist or be accessible
    
    cleaned_items = []
    
    for artifact_path in artifacts_to_clean:
        try:
            if os.path.exists(artifact_path):
                if os.path.isdir(artifact_path):
                    shutil.rmtree(artifact_path)
                    cleaned_items.append(f"directory '{os.path.basename(artifact_path)}'")
                elif os.path.isfile(artifact_path):
                    os.remove(artifact_path)
                    cleaned_items.append(f"file '{os.path.basename(artifact_path)}'")
        except Exception as e:
            print(f"Warning: Could not remove {artifact_path}: {e}")
    
    if cleaned_items:
        print(f"Cleaned up old build artifacts: {', '.join(cleaned_items)}")
    else:
        print("No old build artifacts found to clean up")

# --- Helper function for building standalone game executables ---
def build_standalone_game(project_name: str, project_root_dir: str):
    print(f"Building standalone executable for project: {project_name}")
    update_build_progress(project_name, f"Preparing build environment for {project_name}...")

    # Determine the absolute path to the specific game project directory
    project_absolute_path = os.path.join(project_root_dir, project_name)
    update_build_progress(project_name, "Locating project files and engine components...")
    
    # Clean up old build artifacts to prevent conflicts
    update_build_progress(project_name, "Cleaning up old build artifacts...")
    cleanup_old_build_artifacts(project_absolute_path, project_name)
    
    # Temporarily disable debug mode for the build
    update_build_progress(project_name, "Configuring project for production build...")
    original_debug_mode, backup_path = disable_debug_mode_for_build(project_absolute_path)
    
    try:
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
        config_manager_path = os.path.join(bundle_base_dir, 'config_manager.py')
        game_server_path = os.path.join(bundle_base_dir, 'game_server.py')
        game_server_wrapper_path = os.path.join(bundle_base_dir, 'game_server_wrapper.py')
        loading_window_path = os.path.join(bundle_base_dir, 'loading_window.py')
        
        # Check for custom icon in project configuration
        icon_path = None
        project_config_path = os.path.join(project_absolute_path, 'project.json')
        if os.path.exists(project_config_path):
            try:
                with open(project_config_path, 'r') as f:
                    project_config = json.load(f)
                    icon_relative_path = project_config.get('icon_path', '').strip()
                    if icon_relative_path:
                        icon_absolute_path = os.path.join(project_absolute_path, icon_relative_path)
                        if os.path.exists(icon_absolute_path):
                            # Check if the file is already a .ico file
                            if icon_absolute_path.lower().endswith('.ico'):
                                icon_path = icon_absolute_path
                                print(f"Using custom .ico icon: {icon_relative_path}")
                            else:
                                # Convert the image to .ico format
                                update_build_progress(project_name, f"Converting {os.path.basename(icon_absolute_path)} to .ico format...")
                                print(f"Converting custom icon to .ico format: {icon_relative_path}")
                                converted_icon_path = convert_image_to_ico(icon_absolute_path, project_absolute_path)
                                if converted_icon_path:
                                    icon_path = converted_icon_path
                                else:
                                    print(f"Failed to convert icon, proceeding without custom icon")
                        else:
                            print(f"Warning: Icon file not found: {icon_relative_path}")
            except Exception as e:
                print(f"Warning: Could not read icon setting from project.json: {e}")
        
        update_build_progress(project_name, "Configuring PyInstaller build settings...")

        # PyInstaller options
        # --noconsole: Do not open a console window (for GUI apps)
        # --onefile: Create a single executable file
        # --name: Name of the executable
        # --add-data: Add non-binary files or folders to the executable
        # Format: <source_path><os.pathsep><destination_path_in_bundle>
        
        # The destination path in bundle should be relative to the executable's root
        # For example, if you add 'templates' folder, it will be accessible as 'templates' in the bundle

        pyinstaller_args = [
            game_server_wrapper_path,  # Main script to execute (NEW: game server wrapper)
            '--noconsole',             # For GUI application
            '--onefile',               # Create a single executable file
            f'--name={project_name}_game', # Name of the executable
            
            # Add data files/folders
            f'--add-data={engine_path}{os.pathsep}engine',
            f'--add-data={templates_path}{os.pathsep}templates',
            f'--add-data={static_path}{os.pathsep}static',
            f'--add-data={config_manager_path}{os.pathsep}.',
            f'--add-data={game_server_path}{os.pathsep}.',  # NEW: game server instead of full app.py
            f'--add-data={loading_window_path}{os.pathsep}.',
            
            # Add the specific game project being built
            f'--add-data={project_absolute_path}{os.pathsep}game_data/{project_name}',
            
            # Put build outputs in the project directory for easier access
            f'--distpath={os.path.join(project_absolute_path, "dist")}',
            f'--workpath={os.path.join(project_absolute_path, "build")}',
            f'--specpath={os.path.join(project_absolute_path, "spec")}',
        ]

        # Add custom icon if specified
        if icon_path:
            pyinstaller_args.append(f'--icon={icon_path}')
            update_build_progress(project_name, f"Using custom icon: {os.path.basename(icon_path)}")
        else:
            print("No custom icon specified - using default")

        update_build_progress(project_name, "Building Project - this may take several minutes...")
        PyInstaller.__main__.run(pyinstaller_args)
        
        update_build_progress(project_name, "Finalizing build and cleaning up temporary files...")

        dist_path = os.path.join(project_absolute_path, "dist")
        print(f"Build process for {project_name} completed. Executable can be found in: {dist_path}")
        update_build_progress(project_name, f"Build completed! Executable available at: {dist_path}")
        
    finally:
        # Clean up any temporary .ico files created during the build
        try:
            for file in os.listdir(project_absolute_path):
                if file.endswith('_converted.ico'):
                    temp_ico_path = os.path.join(project_absolute_path, file)
                    os.remove(temp_ico_path)
                    print(f"Cleaned up temporary icon file: {file}")
        except OSError:
            pass  # Directory might not exist or be accessible
        
        # Always restore the original debug mode setting
        if backup_path:
            update_build_progress(project_name, "Restoring original project settings...")
            restore_debug_mode_after_build(backup_path)
