import os
import json

def get_config_dir():
    """Returns the appropriate configuration directory based on the OS."""
    if os.name == 'nt':  # Windows
        return os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'ScribeEngine')
    else:  # Linux, macOS, etc.
        return os.path.join(os.path.expanduser('~'), '.config', 'scribe_engine')

def get_config_file_path():
    """Returns the absolute path to the configuration file."""
    config_dir = get_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, 'config.json')

def load_config():
    """Loads the configuration from the config file."""
    config_file = get_config_file_path()
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """Saves the configuration to the config file."""
    config_file = get_config_file_path()
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

def get_project_root():
    """Retrieves the stored project root from the configuration."""
    config = load_config()
    return config.get('project_root')

def set_project_root(path):
    """Saves the project root to the configuration."""
    config = load_config()
    config['project_root'] = path
    save_config(config)
