"""
Project Creation Wizard for Scribe Engine V2

Simple dialog for creating new projects from templates.
"""

import os
import shutil
import json
import tkinter as tk
from tkinter import filedialog, messagebox


class ProjectWizard:
    """Wizard for creating new V2 projects."""

    def __init__(self):
        self.project_name = ""
        self.project_path = ""

    def run(self):
        """
        Run the project wizard.

        Returns:
            Project path if created successfully, None otherwise
        """
        root = tk.Tk()
        root.title("New Project - Scribe Engine V2")
        root.geometry("500x350")
        root.resizable(False, False)

        # Title
        title_label = tk.Label(root, text="Create New Project", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # Project Name
        name_frame = tk.Frame(root)
        name_frame.pack(pady=10, padx=40, fill='x')

        name_label = tk.Label(name_frame, text="Project Name:", font=("Arial", 11))
        name_label.pack(anchor='w')

        name_entry = tk.Entry(name_frame, font=("Arial", 11))
        name_entry.pack(fill='x', pady=5)
        name_entry.insert(0, "MyGame")
        name_entry.focus()

        # Project Location
        location_frame = tk.Frame(root)
        location_frame.pack(pady=10, padx=40, fill='x')

        location_label = tk.Label(location_frame, text="Location:", font=("Arial", 11))
        location_label.pack(anchor='w')

        location_display = tk.Entry(location_frame, font=("Arial", 10), state='readonly')
        location_display.pack(fill='x', pady=5, side='left', expand=True)

        # Default location
        default_location = os.path.expanduser("~/ScribeEngineProjects")
        location_var = tk.StringVar(value=default_location)
        location_display.config(textvariable=location_var)

        def browse_location():
            path = filedialog.askdirectory(title="Select Project Location",
                                           initialdir=location_var.get())
            if path:
                location_var.set(path)

        browse_btn = tk.Button(location_frame, text="Browse...", command=browse_location,
                               font=("Arial", 10))
        browse_btn.pack(side='right', padx=(5, 0))

        # Full Path Preview
        preview_frame = tk.Frame(root)
        preview_frame.pack(pady=10, padx=40, fill='x')

        preview_label = tk.Label(preview_frame, text="Project will be created at:",
                                 font=("Arial", 9), fg='gray')
        preview_label.pack(anchor='w')

        def update_preview(*args):
            name = name_entry.get().strip()
            loc = location_var.get()
            if name and loc:
                full_path = os.path.join(loc, name)
                preview_path.config(text=full_path)
            else:
                preview_path.config(text="")

        preview_path = tk.Label(preview_frame, text="", font=("Arial", 9, "italic"), fg='blue')
        preview_path.pack(anchor='w')

        # Update preview on changes
        name_entry.bind('<KeyRelease>', update_preview)
        location_var.trace('w', update_preview)
        update_preview()

        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)

        created_path = [None]  # Mutable container for result

        def create_project():
            name = name_entry.get().strip()
            location = location_var.get()

            if not name:
                messagebox.showerror("Error", "Please enter a project name")
                return

            if not location:
                messagebox.showerror("Error", "Please select a location")
                return

            # Validate project name
            if not name.replace('_', '').replace('-', '').isalnum():
                messagebox.showerror("Error", "Project name can only contain letters, numbers, hyphens, and underscores")
                return

            full_path = os.path.join(location, name)

            # Check if directory already exists
            if os.path.exists(full_path):
                messagebox.showerror("Error", f"Directory already exists:\n{full_path}")
                return

            # Create project
            try:
                self._create_project_from_template(name, full_path)
                created_path[0] = full_path
                messagebox.showinfo("Success", f"Project created successfully!\n{full_path}")
                root.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create project:\n{str(e)}")

        create_btn = tk.Button(button_frame, text="Create", command=create_project,
                               font=("Arial", 11), width=10, bg='#4CAF50', fg='white')
        create_btn.pack(side='left', padx=5)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=root.destroy,
                               font=("Arial", 11), width=10)
        cancel_btn.pack(side='left', padx=5)

        # Run dialog
        root.mainloop()

        return created_path[0]

    def _create_project_from_template(self, project_name, project_path):
        """
        Create a new project from the empty_project template.

        Args:
            project_name: Name of the project
            project_path: Full path where project will be created
        """
        # Find template
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(script_dir, '..', 'templates', 'empty_project')
        template_path = os.path.abspath(template_path)

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")

        # Copy template to new location
        print(f"[ProjectWizard] Copying template from {template_path}")
        print(f"[ProjectWizard] To {project_path}")

        shutil.copytree(template_path, project_path)

        # Update project config
        config_path = os.path.join(project_path, '2d_project.json')
        with open(config_path, 'r') as f:
            config = json.load(f)

        config['title'] = project_name
        config['window']['title'] = project_name

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        # Create asset directories
        for asset_dir in ['sprites', 'sounds', 'music', 'fonts']:
            asset_path = os.path.join(project_path, 'assets', asset_dir)
            os.makedirs(asset_path, exist_ok=True)

        print(f"[ProjectWizard] Project created successfully: {project_path}")
