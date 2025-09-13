#!/usr/bin/env python3
"""
Scribe Engine Dependency Installer - Linux Version
Automatically installs Python and PyInstaller if needed.
"""

import os
import sys
import subprocess
import json
import shutil
from datetime import datetime
from pathlib import Path

def get_linux_distribution():
    """Detect Linux distribution."""
    try:
        with open('/etc/os-release') as f:
            lines = f.readlines()

        distro_info = {}
        for line in lines:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                distro_info[key] = value.strip('"')

        return distro_info.get('ID', 'unknown').lower()
    except:
        return 'unknown'

def check_python_installed():
    """Check if Python is installed and return version info."""
    python_candidates = [
        'python3',
        'python',
        '/usr/bin/python3',
        '/usr/bin/python',
        '/usr/local/bin/python3',
    ]

    for python_exe in python_candidates:
        try:
            result = subprocess.run([python_exe, '--version'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                # Check if it's Python 3.8+
                if 'Python 3.' in version:
                    version_parts = version.replace('Python ', '').split('.')
                    if len(version_parts) >= 2 and int(version_parts[1]) >= 8:
                        return python_exe, version
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            continue

    return None, None

def check_pip_installed(python_exe):
    """Check if pip is available."""
    try:
        result = subprocess.run([python_exe, '-m', 'pip', '--version'],
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_pyinstaller_installed(python_exe):
    """Check if PyInstaller is installed for the given Python."""
    try:
        result = subprocess.run([python_exe, '-m', 'PyInstaller', '--version'],
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, None

def install_python_linux():
    """Install Python using system package manager."""
    distro = get_linux_distribution()

    install_commands = {
        'ubuntu': ['sudo', 'apt', 'update', '&&', 'sudo', 'apt', 'install', '-y', 'python3', 'python3-pip'],
        'debian': ['sudo', 'apt', 'update', '&&', 'sudo', 'apt', 'install', '-y', 'python3', 'python3-pip'],
        'fedora': ['sudo', 'dnf', 'install', '-y', 'python3', 'python3-pip'],
        'centos': ['sudo', 'yum', 'install', '-y', 'python3', 'python3-pip'],
        'rhel': ['sudo', 'yum', 'install', '-y', 'python3', 'python3-pip'],
        'arch': ['sudo', 'pacman', '-S', '--noconfirm', 'python', 'python-pip'],
        'manjaro': ['sudo', 'pacman', '-S', '--noconfirm', 'python', 'python-pip'],
    }

    if distro in install_commands:
        print(f"Detected {distro.title()} Linux. Installing Python...")
        cmd_str = ' '.join(install_commands[distro])
        result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    else:
        print(f"Unknown distribution: {distro}")
        print("Please install Python 3.8+ manually using your package manager:")
        print("  Ubuntu/Debian: sudo apt install python3 python3-pip")
        print("  Fedora: sudo dnf install python3 python3-pip")
        print("  Arch: sudo pacman -S python python-pip")
        return False

def install_pyinstaller(python_exe):
    """Install PyInstaller using pip."""
    print("Installing PyInstaller...")

    # Try user install first, then system-wide
    commands_to_try = [
        [python_exe, '-m', 'pip', 'install', '--user', 'pyinstaller'],
        [python_exe, '-m', 'pip', 'install', 'pyinstaller'],
    ]

    for cmd in commands_to_try:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return True
        except subprocess.TimeoutExpired:
            continue

    return False

def create_config_file():
    """Create a configuration file with installation details."""
    config = {
        'scribe_engine_setup': True,
        'install_date': str(datetime.now()),
        'platform': 'linux',
        'python_path': None,
        'pyinstaller_available': False
    }

    python_exe, python_version = check_python_installed()
    if python_exe:
        config['python_path'] = python_exe
        config['python_version'] = python_version

        pyinstaller_available, pyinstaller_version = check_pyinstaller_installed(python_exe)
        config['pyinstaller_available'] = pyinstaller_available
        if pyinstaller_available:
            config['pyinstaller_version'] = pyinstaller_version

    config_path = os.path.join(os.path.expanduser('~'), '.scribe_engine_config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    return config_path

def main():
    """Main installer function for Linux - smart dependency checker."""
    print("=" * 60)
    print("Scribe Engine Dependency Checker - Linux")
    print("=" * 60)

    needs_python = False
    needs_pyinstaller = False
    python_exe = None

    # Check current Python installation
    python_exe, python_version = check_python_installed()

    if python_exe:
        print(f"✓ Python found: {python_version} at {python_exe}")
    else:
        print("✗ Python 3.8+ not found")
        needs_python = True

    # If we have Python, check pip and PyInstaller
    if python_exe:
        if not check_pip_installed(python_exe):
            print("✗ pip not available")
            needs_python = True  # Need to reinstall Python with pip
        else:
            print("✓ pip available")

            pyinstaller_available, pyinstaller_version = check_pyinstaller_installed(python_exe)
            if pyinstaller_available:
                print(f"✓ PyInstaller found: {pyinstaller_version}")
            else:
                print("✗ PyInstaller not found")
                needs_pyinstaller = True

    # Summary of what we found
    print("=" * 60)

    if not needs_python and not needs_pyinstaller:
        print("[SUCCESS] Great! You already have everything you need:")
        print(f"   • Python: {python_version}")
        print(f"   • PyInstaller: {pyinstaller_version}")
        print("\nScribe Engine is ready to build games!")
        print("=" * 60)
        input("Press Enter to exit...")
        return True

    # Install missing dependencies
    print("Installing missing dependencies...")
    print("=" * 60)

    if needs_python:
        print("Installing Python and pip...")
        if install_python_linux():
            print("✓ Python installation attempted!")

            # Try to find Python again
            python_exe, python_version = check_python_installed()
            if not python_exe:
                print("✗ Python still not found after installation.")
                print("Please install Python 3.8+ manually and try again.")
                input("Press Enter to exit...")
                return False
            else:
                print(f"✓ Python ready: {python_version}")
        else:
            print("✗ Python installation failed or requires manual intervention.")
            input("Press Enter to exit...")
            return False

    if needs_pyinstaller:
        print("Installing PyInstaller...")
        if install_pyinstaller(python_exe):
            print("✓ PyInstaller installed successfully!")
        else:
            print("✗ PyInstaller installation failed.")
            print("You may need to install it manually:")
            print(f"  {python_exe} -m pip install --user pyinstaller")
            input("Press Enter to exit...")
            return False

    # Create configuration file
    config_path = create_config_file()
    print(f"✓ Configuration saved to: {config_path}")

    print("=" * 60)
    print("✓ All dependencies installed successfully!")
    print("Scribe Engine is now ready to build games.")
    print("=" * 60)
    input("Press Enter to exit...")
    return True

if __name__ == "__main__":
    if not sys.platform.startswith('linux'):
        print("This installer is designed for Linux. Use installer_setup.py on Windows.")
        sys.exit(1)
    main()