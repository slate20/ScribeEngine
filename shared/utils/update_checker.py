"""
Scribe Engine Update Checker

This module provides automatic update checking functionality for the Scribe Engine.
It integrates with GitHub releases to check for new versions and can automatically
download and install updates.

Features:
- Automatic version detection from executable names or build scripts
- Semantic version comparison
- GitHub API integration for release checking
- Cross-platform executable replacement
- User preference management (skip versions, check frequency)
- GUI and CLI interfaces

Usage:
- GUI: Automatically triggered on startup, shows dialog for updates
- CLI: Automatically triggered on startup, shows console prompts

Configuration:
- Settings stored in config_manager under 'update_settings'
- Can be disabled or frequency adjusted by users

Repository Configuration:
- Default: "slate20/ScribeEngine"
- Looks for assets matching current platform (linux/windows/macos)
- Prefers GUI versions over CLI versions when available
"""

import os
import sys
import json
import re
import requests
import shutil
import tempfile
import subprocess
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from shared.utils import config_manager

class UpdateChecker:
    def __init__(self, github_repo: str = "slate20/ScribeEngine", current_version: str = None):
        """
        Initialize the update checker.

        Args:
            github_repo: GitHub repository in format "owner/repo"
            current_version: Current version string, auto-detected if None
        """
        self.github_repo = github_repo
        self.current_version = current_version or self._detect_current_version()
        self.api_url = f"https://api.github.com/repos/{github_repo}/releases/latest"

    def _detect_current_version(self) -> str:
        """
        Detect current version from multiple sources with robust fallbacks.

        Priority order:
        1. version_info.py (embedded in executable)
        2. Executable name pattern (for renamed executables)
        3. build_engine.py version variable
        4. Default fallback
        """
        # Primary source: version_info.py module
        try:
            if getattr(sys, 'frozen', False):
                # Running as bundled executable - version_info should be embedded
                import version_info
                return version_info.get_version()
            else:
                # Running as script - try to import from local directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                version_info_path = os.path.join(script_dir, 'version_info.py')
                if os.path.exists(version_info_path):
                    # Import the module dynamically
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("version_info", version_info_path)
                    version_info = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(version_info)
                    return version_info.get_version()
        except Exception:
            # Continue to fallbacks if version_info import fails
            pass

        # Fallback 1: Try to get from executable name
        if getattr(sys, 'frozen', False):
            # Running as bundled executable
            exe_name = os.path.basename(sys.executable)
            version_match = re.search(r'v(\d+\.\d+\.\d+)', exe_name)
            if version_match:
                return version_match.group(1)

        # Fallback 2: build_engine.py version
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            build_engine_path = os.path.join(script_dir, 'build_engine.py')
            if os.path.exists(build_engine_path):
                with open(build_engine_path, 'r') as f:
                    content = f.read()
                    version_match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", content)
                    if version_match:
                        return version_match.group(1)
        except Exception:
            pass

        # Final fallback - this should rarely be reached now
        return "1.0.0"

    def _parse_version(self, version_str: str) -> Tuple[int, int, int]:
        """
        Parse version string into tuple of integers for comparison.
        """
        # Remove 'v' prefix if present
        clean_version = version_str.lstrip('v')
        parts = clean_version.split('.')

        # Ensure we have at least 3 parts
        while len(parts) < 3:
            parts.append('0')

        try:
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            return (0, 0, 0)

    def _is_newer_version(self, latest_version: str) -> bool:
        """
        Compare current version with latest version.
        """
        current = self._parse_version(self.current_version)
        latest = self._parse_version(latest_version)
        return latest > current

    def _should_check_for_updates(self) -> bool:
        """
        Check if we should perform an update check based on settings and last check time.
        """
        config = config_manager.load_config()
        update_settings = config.get('update_settings', {})

        # Check if updates are disabled
        if not update_settings.get('check_for_updates', True):
            return False

        # Check frequency (default: daily)
        check_frequency = update_settings.get('check_frequency', 'daily')
        last_check_str = update_settings.get('last_check')

        if not last_check_str:
            return True

        try:
            last_check = datetime.fromisoformat(last_check_str)
            now = datetime.now()

            if check_frequency == 'daily':
                return now - last_check > timedelta(days=1)
            elif check_frequency == 'weekly':
                return now - last_check > timedelta(weeks=1)
            else:  # 'startup' or any other value
                return True
        except Exception:
            return True

    def _update_last_check_time(self):
        """
        Update the last check timestamp in config.
        """
        config = config_manager.load_config()
        if 'update_settings' not in config:
            config['update_settings'] = {}
        config['update_settings']['last_check'] = datetime.now().isoformat()
        config_manager.save_config(config)

    def check_for_updates(self, force: bool = False) -> Optional[Dict]:
        """
        Check for available updates.

        Args:
            force: Force check even if settings say not to

        Returns:
            Dict with update info if available, None otherwise
        """
        if not force and not self._should_check_for_updates():
            return None

        try:
            # Make request to GitHub API
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()

            release_data = response.json()
            latest_version = release_data['tag_name'].lstrip('v')

            # Update last check time
            self._update_last_check_time()

            # Check if this version was skipped
            config = config_manager.load_config()
            skipped_versions = config.get('update_settings', {}).get('skipped_versions', [])
            if latest_version in skipped_versions:
                return None

            if self._is_newer_version(latest_version):
                # Find appropriate asset for current platform
                platform_suffix = self._get_platform_suffix()
                asset_url = None
                asset_name = None

                for asset in release_data.get('assets', []):
                    asset_name_lower = asset['name'].lower()
                    if platform_suffix in asset_name_lower and 'scribe-engine' in asset_name_lower:
                        # Prefer GUI version if available
                        if 'cli' not in asset_name_lower or asset_url is None:
                            asset_url = asset['browser_download_url']
                            asset_name = asset['name']

                return {
                    'version': latest_version,
                    'current_version': self.current_version,
                    'release_url': release_data['html_url'],
                    'release_notes': release_data.get('body', ''),
                    'asset_url': asset_url,
                    'asset_name': asset_name,
                    'published_at': release_data.get('published_at')
                }

        except requests.RequestException:
            # Network error, fail silently
            pass
        except Exception:
            # Other errors, fail silently
            pass

        return None

    def _get_platform_suffix(self) -> str:
        """
        Get platform suffix for executable matching.
        """
        if sys.platform.startswith('linux'):
            return 'linux'
        elif sys.platform.startswith('win'):
            return 'windows'
        elif sys.platform.startswith('darwin'):
            return 'macos'
        else:
            return 'unknown'

    def skip_version(self, version: str):
        """
        Mark a version as skipped.
        """
        config = config_manager.load_config()
        if 'update_settings' not in config:
            config['update_settings'] = {}
        if 'skipped_versions' not in config['update_settings']:
            config['update_settings']['skipped_versions'] = []

        if version not in config['update_settings']['skipped_versions']:
            config['update_settings']['skipped_versions'].append(version)
            config_manager.save_config(config)

    def download_and_replace(self, asset_url: str, asset_name: str) -> bool:
        """
        Download and replace the current executable.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current executable path
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                # Development mode - can't really update
                return False

            # Create backup
            backup_path = current_exe + '.backup'
            shutil.copy2(current_exe, backup_path)

            # Download new version to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_file:
                temp_path = temp_file.name

                response = requests.get(asset_url, stream=True, timeout=30)
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded += len(chunk)

                        # Simple progress indication
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rDownloading: {percent:.1f}%", end='', flush=True)

            print()  # New line after progress

            # Make new file executable on Unix systems
            if not sys.platform.startswith('win'):
                os.chmod(temp_path, 0o755)

            # Replace current executable
            shutil.move(temp_path, current_exe)

            # Clean up backup after successful replacement
            try:
                os.remove(backup_path)
            except Exception:
                pass  # Keep backup if we can't remove it

            return True

        except Exception as e:
            # Restore backup if something went wrong
            backup_path = current_exe + '.backup'
            if os.path.exists(backup_path):
                try:
                    shutil.move(backup_path, current_exe)
                except Exception:
                    pass

            # Clean up temp file
            try:
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass

            return False

    def restart_application(self):
        """
        Restart the application after update.
        """
        try:
            if getattr(sys, 'frozen', False):
                # Running as executable
                current_exe = sys.executable

                if sys.platform.startswith('win'):
                    # Windows: start new process and exit
                    subprocess.Popen([current_exe],
                                   creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    # Unix: use os.execv to replace current process
                    os.execv(current_exe, [current_exe])
            else:
                # Development mode
                python_exe = sys.executable
                script_path = os.path.abspath(sys.argv[0])
                os.execv(python_exe, [python_exe, script_path] + sys.argv[1:])

        except Exception:
            # If restart fails, just exit and let user restart manually
            print("Please restart the application manually to complete the update.")
            sys.exit(0)


def check_for_updates_cli(github_repo: str = "slate20/ScribeEngine") -> bool:
    """
    CLI interface for checking updates.

    Returns:
        True if user chose to update, False otherwise
    """
    checker = UpdateChecker(github_repo)
    update_info = checker.check_for_updates()

    if not update_info:
        return False

    print(f"\n🎉 Update Available!")
    print(f"Current version: v{update_info['current_version']}")
    print(f"Latest version: v{update_info['version']}")
    print(f"Release page: {update_info['release_url']}")

    if update_info['release_notes']:
        print(f"\nRelease Notes:")
        # Show first few lines of release notes
        lines = update_info['release_notes'].split('\n')[:5]
        for line in lines:
            print(f"  {line}")
        if len(update_info['release_notes'].split('\n')) > 5:
            print("  ...")

    print("\nOptions:")
    print("1. Update now")
    print("2. Skip this version")
    print("3. Remind me later")

    while True:
        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == '1':
            if not update_info['asset_url']:
                print("❌ No compatible download found for your platform.")
                return False

            print(f"\nDownloading {update_info['asset_name']}...")
            if checker.download_and_replace(update_info['asset_url'], update_info['asset_name']):
                print("✅ Update completed successfully!")
                print("Restarting application...")
                time.sleep(1)
                checker.restart_application()
                return True
            else:
                print("❌ Update failed. Please try again later.")
                return False

        elif choice == '2':
            checker.skip_version(update_info['version'])
            print(f"Version {update_info['version']} skipped.")
            return False

        elif choice == '3':
            print("You'll be reminded next time you start the application.")
            return False

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def check_for_updates_gui(github_repo: str = "slate20/ScribeEngine") -> Optional[Dict]:
    """
    GUI interface for checking updates - returns update info for GUI to handle.

    Returns:
        Update info dict if available, None otherwise
    """
    checker = UpdateChecker(github_repo)
    return checker.check_for_updates()