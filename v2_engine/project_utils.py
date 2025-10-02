"""
V2 Project Utilities
Helper functions for creating and managing V2 projects.
"""

import os
import json
import shutil


def create_v2_project(project_name: str, project_root_dir: str, config: dict):
    """
    Creates a new V2 game project with directory structure and template files.

    Args:
        project_name: URL-friendly project name (e.g., "my-platformer")
        project_root_dir: Parent directory where project will be created
        config: Dictionary with project configuration:
            - game_title: Display title (e.g., "My Platformer")
            - window_size: "WIDTHxHEIGHT" (e.g., "800x600")
            - template: "empty" or "platformer"

    Returns:
        str: Full path to created project

    Raises:
        FileExistsError: If project already exists
        ValueError: If configuration is invalid
    """
    project_path = os.path.join(project_root_dir, project_name)

    if os.path.exists(project_path):
        raise FileExistsError(f"Project '{project_name}' already exists at {project_path}")

    print(f"[V2 Project] Creating new V2 project: {project_name} at {project_path}")

    # Parse configuration
    game_title = config.get('game_title', project_name.replace('_', ' ').replace('-', ' ').title())
    window_size = config.get('window_size', '800x600')
    template = config.get('template', 'empty')

    try:
        width, height = map(int, window_size.split('x'))
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid window size: {window_size}. Expected format: WIDTHxHEIGHT")

    # Determine template source
    engine_root = os.path.dirname(os.path.abspath(__file__))
    if template == 'platformer':
        template_source = os.path.join(engine_root, 'templates', 'platformer')
    else:  # empty
        template_source = os.path.join(engine_root, 'templates', 'empty_project')

    if not os.path.exists(template_source):
        raise FileNotFoundError(f"Template not found: {template_source}")

    # Copy template to project directory
    print(f"[V2 Project] Copying template from: {template_source}")
    shutil.copytree(template_source, project_path)

    # Update 2d_project.json with user configuration
    config_path = os.path.join(project_path, '2d_project.json')
    with open(config_path, 'r') as f:
        project_config = json.load(f)

    # Apply user settings
    project_config['title'] = game_title
    project_config['window']['title'] = game_title
    project_config['window']['width'] = width
    project_config['window']['height'] = height

    # Write updated config
    with open(config_path, 'w') as f:
        json.dump(project_config, f, indent=2)

    # Create asset directories if they don't exist
    asset_dirs = [
        'assets/sprites',
        'assets/sounds',
        'assets/music',
        'assets/fonts'
    ]

    for asset_dir in asset_dirs:
        dir_path = os.path.join(project_path, asset_dir)
        os.makedirs(dir_path, exist_ok=True)

    # Note: scripts directory and game_objects.py are copied from template
    # No need to create them separately

    print(f"[V2 Project] Project created successfully: {project_path}")
    print(f"[V2 Project] Template: {template}, Window: {width}x{height}")

    return project_path
