import sys
import io
import os
import threading
import time
import webview
import requests

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app as flask_app
from app import set_game_project_path, set_debug_mode, reset_game_engine, set_gui_mode
import config_manager
from loading_window import LoadingWindow
from update_checker import check_for_updates_gui, UpdateChecker

# Global variables for server management
flask_thread_instance = None
project_root_path = None
active_project_path = None

class Api:
    """
    API class exposed to the webview frontend.
    """
    def open_folder_dialog(self):
        """
        Opens a folder selection dialog and returns the selected path.
        """
        # Get the active webview window and create a folder dialog
        if webview.windows:
            window = webview.windows[0]
            result = window.create_file_dialog(webview.FileDialog.FOLDER)
            if result:
                # result is a tuple, the first element is the path
                return result[0]

def start_flask_app():
    """Starts the Flask server in a separate thread."""
    flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def handle_update_gui(update_info):
    """Handle update notification in GUI mode."""
    try:
        import tkinter as tk
        from tkinter import messagebox

        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()

        message = f"""A new version of Scribe Engine is available!

Current version: v{update_info['current_version']}
Latest version: v{update_info['version']}

Would you like to update now?

The application will restart after updating."""

        result = messagebox.askyesnocancel(
            "Update Available",
            message,
            icon='question'
        )

        if result is True:  # Yes - Update now
            if not update_info['asset_url']:
                messagebox.showerror("Update Error", "No compatible download found for your platform.")
                root.destroy()
                return

            # Show progress dialog (simplified)
            progress_window = tk.Toplevel()
            progress_window.title("Updating...")
            progress_window.geometry("400x100")
            progress_window.resizable(False, False)

            tk.Label(progress_window, text="Downloading update...").pack(pady=20)
            progress_window.update()

            # Download and update
            checker = UpdateChecker()
            success = checker.download_and_replace(update_info['asset_url'], update_info['asset_name'])

            progress_window.destroy()

            if success:
                messagebox.showinfo("Update Complete", "Update completed successfully!\nThe application will now restart.")
                root.destroy()
                checker.restart_application()
            else:
                messagebox.showerror("Update Failed", "Update failed. Please try again later or download manually.")

        elif result is False:  # No - Skip this version
            checker = UpdateChecker()
            checker.skip_version(update_info['version'])

        # result is None for Cancel - do nothing

        root.destroy()

    except ImportError:
        # tkinter not available, fall back to console
        print(f"\n🎉 Update Available: v{update_info['current_version']} → v{update_info['version']}")
        print(f"Visit: {update_info['release_url']}")
    except Exception:
        # Any other error, fail silently
        pass

def run_gui_app():
    """Main function to launch the GUI and the Flask server."""
    global project_root_path, flask_thread_instance
    
    # Determine icon path for the loading window
    if getattr(sys, 'frozen', False):
        # Running as a bundled executable
        base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
    else:
        # Running as a script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    icon_path = os.path.join(base_path, 'SE_icon.png')
    
    # Create loading window
    loading_window = LoadingWindow(
        title="Scribe Engine",
        subtitle="Starting integrated development environment...",
        icon_path=icon_path if os.path.exists(icon_path) else None
    )
    
    def flask_startup_sequence():
        """The Flask startup sequence that runs behind the loading window."""
        global project_root_path, flask_thread_instance
        
        # Set the application to run in GUI mode
        set_gui_mode(True)

        # Check for the project root and handle first-run setup
        project_root_path = config_manager.get_project_root()
        if not project_root_path or not os.path.isdir(project_root_path):
            # Determine the base path for the application
            if getattr(sys, 'frozen', False):
                # Running as a bundled executable
                base_path = os.path.dirname(sys.executable)
            else:
                # Running as a script
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            project_root_path = os.path.join(base_path, 'ScribeEngine_Projects')
            os.makedirs(project_root_path, exist_ok=True)
            config_manager.set_project_root(project_root_path)

        # Start Flask in a separate thread
        flask_thread_instance = threading.Thread(target=start_flask_app)
        flask_thread_instance.daemon = True
        flask_thread_instance.start()
        time.sleep(2) # Give Flask a moment to start up
        
        return True  # Signal that Flask startup is complete
    
    # Run the Flask startup sequence with the loading window
    loading_window.run_with_loading(flask_startup_sequence)

    # Check for updates after Flask startup
    try:
        update_info = check_for_updates_gui()
        if update_info:
            handle_update_gui(update_info)
    except Exception:
        # Silently fail if update check encounters any issues
        pass

    # Create an API instance to expose to the webview
    api = Api()

    # Create the webview window (this must run on main thread after loading window closes)
    webview.create_window('Scribe Engine', 'http://127.0.0.1:5000/gui', js_api=api, width=1920, height=1080)
    webview.start()

    # Wait for the user to close the window
    # try:
    #     input("Press Enter to stop the server and exit...")
    # except KeyboardInterrupt:
    #     print("\nExiting...")
    
if __name__ == '__main__':
    run_gui_app()
