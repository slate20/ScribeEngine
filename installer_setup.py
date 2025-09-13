#!/usr/bin/env python3
"""
Scribe Engine Dependency Installer
Automatically installs Python and PyInstaller if needed.
Creates a self-contained installer executable for easy distribution.
"""

import os
import sys
import subprocess
import urllib.request
import tempfile
import winreg
import json
from pathlib import Path
from datetime import datetime

def check_python_installed():
    """Check if Python is installed and return version info."""
    python_candidates = [
        'python',
        'python3',
        'py',
        r'C:\Python312\python.exe',
        r'C:\Python311\python.exe',
        r'C:\Python310\python.exe',
    ]

    # Also check registry
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Python\PythonCore") as key:
            for i in range(10):
                try:
                    version = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, f"{version}\\InstallPath") as install_key:
                        install_path = winreg.QueryValue(install_key, "")
                        python_candidates.append(os.path.join(install_path, "python.exe"))
                except WindowsError:
                    continue
    except WindowsError:
        pass

    for python_exe in python_candidates:
        try:
            result = subprocess.run([python_exe, '--version'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                return python_exe, version
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    return None, None

def check_pyinstaller_installed(python_exe):
    """Check if PyInstaller is installed for the given Python."""
    try:
        result = subprocess.run([python_exe, '-m', 'PyInstaller', '--version'],
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, None

def download_python_installer():
    """Download Python installer from python.org."""
    print("Downloading Python installer...")

    # Python 3.12 installer URL (64-bit)
    python_url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"

    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as temp_file:
        urllib.request.urlretrieve(python_url, temp_file.name)
        return temp_file.name

def check_pip_installed(python_exe):
    """Check if pip is available."""
    try:
        result = subprocess.run([python_exe, '-m', 'pip', '--version'],
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def install_pip(python_exe):
    """Install pip using ensurepip or get-pip.py."""
    print("Installing pip...")

    # Method 1: Try ensurepip (built into Python 3.4+)
    try:
        result = subprocess.run([python_exe, '-m', 'ensurepip', '--upgrade'],
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ pip installed via ensurepip")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Method 2: Download and run get-pip.py
    try:
        import tempfile
        import urllib.request

        print("Downloading get-pip.py...")
        get_pip_url = "https://bootstrap.pypa.io/get-pip.py"

        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            urllib.request.urlretrieve(get_pip_url, temp_file.name)
            get_pip_path = temp_file.name

        print("Running get-pip.py...")
        result = subprocess.run([python_exe, get_pip_path],
                              capture_output=True, text=True, timeout=60)

        # Clean up
        try:
            os.unlink(get_pip_path)
        except:
            pass

        if result.returncode == 0:
            print("✓ pip installed via get-pip.py")
            return True
        else:
            print(f"get-pip.py failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"Error installing pip: {e}")
        return False

def install_python(installer_path):
    """Install Python using the downloaded installer."""
    print("Installing Python...")

    # Run Python installer with silent install options
    cmd = [
        installer_path,
        '/quiet',           # Silent install
        'InstallAllUsers=1', # Install for all users
        'PrependPath=1',    # Add to PATH
        'Include_pip=1',    # Ensure pip is installed
        'Include_test=0',   # Don't install test suite
        'Include_doc=0',    # Don't install documentation
    ]

    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0

def install_pyinstaller(python_exe):
    """Install PyInstaller using pip."""
    print("Installing PyInstaller...")

    result = subprocess.run([python_exe, '-m', 'pip', 'install', 'pyinstaller'],
                          capture_output=True, text=True)
    return result.returncode == 0

def create_config_file():
    """Create a configuration file with installation details."""
    config = {
        'scribe_engine_setup': True,
        'install_date': str(datetime.now()),
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
    """Main installer function - smart dependency checker."""
    print("=" * 60)
    print("Scribe Engine Dependency Checker")
    print("=" * 60)

    needs_python = False
    needs_pyinstaller = False
    python_exe = None

    # Check current Python installation
    python_exe, python_version = check_python_installed()

    if python_exe:
        print(f"✓ Python found: {python_version} at {python_exe}")
    else:
        print("✗ Python not found")
        needs_python = True

    # If we have Python, check pip and PyInstaller
    if python_exe:
        pip_available = check_pip_installed(python_exe)
        if pip_available:
            print("✓ pip available")
        else:
            print("✗ pip not available")

        # Check PyInstaller (even if pip is missing, we can install pip first)
        if pip_available:
            pyinstaller_available, pyinstaller_version = check_pyinstaller_installed(python_exe)
            if pyinstaller_available:
                print(f"✓ PyInstaller found: {pyinstaller_version}")
            else:
                print("✗ PyInstaller not found")
                needs_pyinstaller = True
        else:
            # Can't check PyInstaller without pip, but we'll need it after installing pip
            print("✗ PyInstaller check skipped (pip required)")
            needs_pyinstaller = True

    # Summary of what we found
    print("=" * 60)

    # Check if pip needs to be installed separately
    needs_pip = python_exe and not check_pip_installed(python_exe)

    if not needs_python and not needs_pip and not needs_pyinstaller:
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
        print("Installing Python...")
        try:
            installer_path = download_python_installer()
            if install_python(installer_path):
                print("✓ Python installed successfully!")

                # Refresh PATH and try to find Python again
                python_exe, python_version = check_python_installed()
                if not python_exe:
                    print("✗ Python installation failed or not found in PATH.")
                    input("Press Enter to exit...")
                    return False
                else:
                    print(f"✓ Python ready: {python_version}")
            else:
                print("✗ Python installation failed.")
                input("Press Enter to exit...")
                return False
        except Exception as e:
            print(f"✗ Error installing Python: {e}")
            input("Press Enter to exit...")
            return False
        finally:
            try:
                os.unlink(installer_path)
            except:
                pass

    # Install pip if needed
    if needs_pip:
        print("Installing pip...")
        if install_pip(python_exe):
            print("✓ pip installed successfully!")
        else:
            print("✗ pip installation failed.")
            print("You may need to install pip manually or reinstall Python.")
            input("Press Enter to exit...")
            return False

    if needs_pyinstaller:
        print("Installing PyInstaller...")
        if install_pyinstaller(python_exe):
            print("✓ PyInstaller installed successfully!")
        else:
            print("✗ PyInstaller installation failed.")
            print("You may need to install it manually: pip install pyinstaller")
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
    if sys.platform.startswith('win'):
        main()
    else:
        print("This installer is designed for Windows. Please install Python and PyInstaller manually on other platforms.")