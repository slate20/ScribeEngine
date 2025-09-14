import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
import os

class LoadingWindow:
    """
    A simple loading window that displays while the application is starting up.
    Uses tkinter for lightweight, dependency-free implementation.
    """
    
    def __init__(self, title="Scribe Engine", subtitle="Loading...", icon_path=None):
        self.title = title
        self.subtitle = subtitle
        self.icon_path = icon_path
        self.window = None
        self.progress_var = None
        self.status_var = None
        self.is_closed = False
        
    def show(self):
        """Create and display the loading window."""
        self.window = tk.Tk()
        self.window.title("Starting...")
        self.window.geometry("400x200")
        self.window.resizable(False, False)
        
        # Center the window on screen
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (200 // 2)
        self.window.geometry(f"400x200+{x}+{y}")
        
        # Configure window properties
        self.window.configure(bg='#2b2b2b')
        self.window.overrideredirect(True)  # Remove window decorations for cleaner look
        
        # Set window icon if provided
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                # Try to set as window icon (works with .ico files)
                if self.icon_path.lower().endswith('.ico'):
                    self.window.iconbitmap(self.icon_path)
                else:
                    # For PNG files, we'll display the icon in the window content instead
                    pass
            except:
                pass  # Ignore icon loading errors
        
        # Create main frame
        main_frame = tk.Frame(self.window, bg='#2b2b2b', padx=40, pady=40)
        main_frame.pack(fill='both', expand=True)
        
        # Icon display (if PNG file is provided)
        if self.icon_path and os.path.exists(self.icon_path) and not self.icon_path.lower().endswith('.ico'):
            try:
                # Load and resize the PNG icon
                icon_image = tk.PhotoImage(file=self.icon_path)
                # Resize to a reasonable size (64x64) if needed
                if icon_image.width() > 64 or icon_image.height() > 64:
                    # Calculate subsample factor to fit within 64x64
                    subsample_factor = max(icon_image.width() // 64, icon_image.height() // 64, 1)
                    icon_image = icon_image.subsample(subsample_factor, subsample_factor)
                
                icon_label = tk.Label(
                    main_frame,
                    image=icon_image,
                    bg='#2b2b2b'
                )
                icon_label.image = icon_image  # Keep a reference to prevent garbage collection
                icon_label.pack(pady=(0, 15))
            except Exception as e:
                # If icon loading fails, just continue without it
                pass
        
        # Title label
        title_label = tk.Label(
            main_frame,
            text=self.title,
            font=('Arial', 18, 'bold'),
            fg='#ffffff',
            bg='#2b2b2b'
        )
        title_label.pack(pady=(0, 10))
        
        # Subtitle/status label  
        self.status_var = tk.StringVar(value=self.subtitle)
        status_label = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=('Arial', 10),
            fg='#cccccc',
            bg='#2b2b2b'
        )
        status_label.pack(pady=(0, 20))
        
        # Progress bar (indeterminate spinner style)
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            'Loading.Horizontal.TProgressbar',
            background='#4a9eff',
            troughcolor='#404040',
            borderwidth=0,
            lightcolor='#4a9eff',
            darkcolor='#4a9eff'
        )
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            main_frame,
            style='Loading.Horizontal.TProgressbar',
            mode='indeterminate',
            length=300
        )
        progress_bar.pack(pady=(0, 20))
        progress_bar.start(10)  # Start the animation
        
        # Version/info label
        info_label = tk.Label(
            main_frame,
            text="Please wait while the application starts up...",
            font=('Arial', 8),
            fg='#888888',
            bg='#2b2b2b'
        )
        info_label.pack()
        
        # Make window stay on top
        self.window.attributes('-topmost', True)
        
        # Start the window update loop in a separate thread
        self.start_update_loop()
        
        return self.window
        
    def start_update_loop(self):
        """Start the tkinter main loop in the main thread."""
        # This should be called from the main thread
        pass
        
    def update_status(self, status_text):
        """Update the status text displayed in the loading window."""
        if self.status_var and not self.is_closed:
            try:
                self.status_var.set(status_text)
                if self.window:
                    self.window.update_idletasks()
            except tk.TclError:
                # Window was closed
                self.is_closed = True
                
    def close(self):
        """Close the loading window."""
        self.is_closed = True
        if self.window:
            try:
                self.window.destroy()
            except tk.TclError:
                # Window was already closed
                pass
            self.window = None
            
    def run_with_loading(self, startup_function, *args, **kwargs):
        """
        Run a startup function while displaying the loading window.
        This method handles the threading and timing automatically.
        """
        # Variable to track when startup is complete
        startup_complete = threading.Event()
        startup_error = None
        startup_result = None
        
        def startup_wrapper():
            nonlocal startup_error, startup_result
            try:
                # Brief pause to show the loading window
                time.sleep(1.0)  
                startup_result = startup_function(*args, **kwargs)
                startup_complete.set()
            except Exception as e:
                startup_error = e
                startup_complete.set()
        
        # Create and show the loading window
        self.show()
        
        # Start the startup function in a background thread
        startup_thread = threading.Thread(target=startup_wrapper)
        startup_thread.daemon = True
        startup_thread.start()
        
        # Counter for status updates
        status_counter = 0
        
        # Keep the loading window running until startup is complete
        while not startup_complete.is_set() and not self.is_closed:
            try:
                # Update status periodically
                status_counter += 1
                if status_counter == 20:  # After ~1 second (20 * 0.05)
                    self.update_status("Starting web server...")
                elif status_counter == 40:  # After ~2 seconds
                    self.update_status("Loading interface...")
                    
                self.window.update()
                time.sleep(0.05)  # Small delay to prevent excessive CPU usage
            except tk.TclError:
                # Window was closed
                break
                
        # Brief pause to show final status
        if not self.is_closed:
            self.update_status("Ready!")
            try:
                self.window.update()
                time.sleep(0.3)
            except tk.TclError:
                pass
                
        # Close the loading window
        self.close()
        
        # If there was an error during startup, raise it
        if startup_error:
            raise startup_error
            
        return startup_result