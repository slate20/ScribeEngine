"""
Game Installer for Scribe Engine
Provides a professional installation UI using tkinter for first-launch game setup.
"""

import os
import json
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, Callable, Optional
from .asset_packer import GameArchive, ObfuscationUtils, clean_project_title


class GameInstaller:
    """Professional game installer with tkinter UI."""

    def __init__(self, executable_dir: str, archive_path: str):
        self.executable_dir = executable_dir
        self.archive_path = archive_path
        self.game_data_dir = os.path.join(executable_dir, 'game_data')
        self.install_marker = os.path.join(self.game_data_dir, '.install_complete')
        self.install_info_path = os.path.join(self.game_data_dir, 'install_info.json')

        # UI components
        self.root = None
        self.progress_var = None
        self.status_var = None
        self.progress_bar = None

        # Installation state
        self.total_files = 0
        self.current_file = 0
        self.cancelled = False
        self.game_title = "Scribe Engine Game"

    def is_installed(self) -> bool:
        """Check if game is already installed."""
        return (os.path.exists(self.install_marker) and
                os.path.exists(self.game_data_dir) and
                os.path.exists(self.install_info_path))

    def needs_reinstall(self) -> bool:
        """Check if game needs to be reinstalled (archive changed)."""
        if not self.is_installed():
            return True

        try:
            # Check if archive is newer than installation
            archive_mtime = os.path.getmtime(self.archive_path)

            with open(self.install_info_path, 'r') as f:
                install_info = json.load(f)

            installed_mtime = install_info.get('archive_mtime', 0)
            return archive_mtime > installed_mtime

        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return True

    def get_game_info(self) -> Dict:
        """Extract basic game information from archive."""
        try:
            archive = GameArchive()
            files = archive.load(self.archive_path)

            if 'project.json' in files:
                config = json.loads(files['project.json'].decode('utf-8'))
                self.game_title = config.get('title', 'Scribe Engine Game')
                return {
                    'title': self.game_title,
                    'author': config.get('author', 'Unknown'),
                    'version': config.get('version', '1.0'),
                    'file_count': len(files)
                }
        except Exception:
            pass

        return {
            'title': self.game_title,
            'author': 'Unknown',
            'version': '1.0',
            'file_count': 0
        }

    def create_installer_ui(self) -> tk.Tk:
        """Create the installation UI window."""
        # Get game info to set proper title
        game_info = self.get_game_info()
        self.game_title = game_info['title']

        root = tk.Tk()
        root.title(f"Installing {self.game_title}")
        root.geometry("500x300")
        root.resizable(False, False)

        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (500 // 2)
        y = (root.winfo_screenheight() // 2) - (300 // 2)
        root.geometry(f"500x300+{x}+{y}")

        # Configure style
        style = ttk.Style()
        style.theme_use('clam')

        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Game title
        title_label = ttk.Label(main_frame, text=self.game_title,
                               font=('Segoe UI', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Installation status
        ttk.Label(main_frame, text="Installing game files...",
                 font=('Segoe UI', 10)).grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var,
                                           maximum=100, length=400)
        self.progress_bar.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))

        # Status text
        self.status_var = tk.StringVar(value="Preparing installation...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var,
                                font=('Segoe UI', 9), foreground='#666666')
        status_label.grid(row=3, column=0, columnspan=2, pady=(0, 20))

        # File count info
        game_info = self.get_game_info()
        info_text = f"Author: {game_info['author']} | Version: {game_info['version']} | Files: {game_info['file_count']}"
        ttk.Label(main_frame, text=info_text, font=('Segoe UI', 8),
                 foreground='#888888').grid(row=4, column=0, columnspan=2, pady=(0, 20))

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # Cancel button
        self.cancel_button = ttk.Button(button_frame, text="Cancel",
                                       command=self.cancel_installation)
        self.cancel_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(0, weight=1)

        # Prevent window closing during installation
        root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.root = root
        return root

    def cancel_installation(self):
        """Handle installation cancellation."""
        result = messagebox.askyesno(
            "Cancel Installation",
            "Are you sure you want to cancel the installation?\n\nThe game will not be playable until installation is complete.",
            icon='warning'
        )
        if result:
            self.cancelled = True
            self.status_var.set("Cancelling installation...")
            self.cancel_button.configure(state='disabled')

    def on_window_close(self):
        """Handle window close attempt."""
        self.cancel_installation()

    def update_progress(self, current: int, total: int, status: str):
        """Update installation progress (thread-safe)."""
        if self.root and not self.cancelled:
            try:
                progress = (current / total * 100) if total > 0 else 0

                # Schedule UI update on main thread
                def update_ui():
                    try:
                        if not self.cancelled:
                            self.progress_var.set(progress)
                            self.status_var.set(status)
                    except tk.TclError:
                        # Window was destroyed
                        pass

                self.root.after(0, update_ui)
            except (tk.TclError, RuntimeError):
                # Window was destroyed or not in main loop
                pass

    def install_game_files(self, progress_callback: Callable = None) -> bool:
        """Install game files to local directory."""
        try:
            # Create game data directory
            os.makedirs(self.game_data_dir, exist_ok=True)

            # Load archive
            if progress_callback:
                progress_callback(0, 100, "Loading game archive...")

            archive = GameArchive()
            files = archive.load(self.archive_path)
            self.total_files = len(files)

            if progress_callback:
                progress_callback(5, 100, f"Preparing {self.total_files} files...")

            # Get project info for encryption
            project_config = {}
            if 'project.json' in files:
                project_config = json.loads(files['project.json'].decode('utf-8'))
                self.game_title = project_config.get('title', self.game_title)

            clean_title = clean_project_title(self.game_title)
            archive_hash = self._calculate_archive_hash()
            encryption_key = self._generate_encryption_key(clean_title, archive_hash)
            seed = int(archive_hash[:8], 16) if archive_hash else 12345

            if progress_callback:
                progress_callback(10, 100, f"Installing {self.game_title}...")

            # Install files with encryption and obfuscation
            self.current_file = 0
            filename_mapping = {}  # Store original -> obfuscated mapping

            for file_path, file_data in files.items():
                if self.cancelled:
                    return False

                self.current_file += 1

                if progress_callback:
                    progress = 10 + (self.current_file / self.total_files * 80)
                    progress_callback(progress, 100, f"Installing: {os.path.basename(file_path)}")

                try:
                    # Encrypt file data
                    encrypted_data = ObfuscationUtils.xor_data(file_data, encryption_key)

                    # Obfuscate filename
                    obfuscated_name = ObfuscationUtils.obfuscate_filename(file_path, seed)

                    # Determine output path
                    if file_path.startswith('assets/'):
                        # Keep assets in subdirectory
                        asset_subpath = file_path[7:]  # Remove 'assets/' prefix
                        if asset_subpath:
                            obfuscated_name = ObfuscationUtils.obfuscate_filename(asset_subpath, seed)
                            output_dir = os.path.join(self.game_data_dir, 'assets')
                            os.makedirs(output_dir, exist_ok=True)
                            output_path = os.path.join(output_dir, f"{obfuscated_name}.enc")
                            filename_mapping[f"assets/{asset_subpath}"] = os.path.join('assets', f"{obfuscated_name}.enc")
                        else:
                            continue
                    else:
                        output_path = os.path.join(self.game_data_dir, f"{obfuscated_name}.enc")
                        filename_mapping[file_path] = f"{obfuscated_name}.enc"

                    # Write encrypted file
                    with open(output_path, 'wb') as f:
                        f.write(encrypted_data)

                except Exception as file_error:
                    print(f"Warning: Failed to install file {file_path}: {file_error}")
                    # Continue with other files
                    continue

                # Force UI update every few files
                if self.current_file % 5 == 0:
                    time.sleep(0.01)

            if self.cancelled:
                return False

            # Create installation info
            if progress_callback:
                progress_callback(95, 100, "Finalizing installation...")

            install_info = {
                'game_title': self.game_title,
                'installed_date': datetime.now().isoformat(),
                'archive_path': os.path.basename(self.archive_path),
                'archive_mtime': os.path.getmtime(self.archive_path),
                'archive_size': os.path.getsize(self.archive_path),
                'file_count': self.total_files,
                'encryption_key_hash': archive_hash,
                'filename_mapping': filename_mapping,
                'version': '1.0'
            }

            with open(self.install_info_path, 'w') as f:
                json.dump(install_info, f, indent=2)

            # Create completion marker
            with open(self.install_marker, 'w') as f:
                f.write(datetime.now().isoformat())

            if progress_callback:
                progress_callback(100, 100, "Installation complete!")

            return True

        except Exception as e:
            print(f"Installation error: {e}")
            if progress_callback:
                progress_callback(0, 100, f"Installation failed: {str(e)}")
            return False

    def _calculate_archive_hash(self) -> str:
        """Calculate hash for archive."""
        import hashlib
        stat = os.stat(self.archive_path)
        hash_input = f"{os.path.basename(self.archive_path)}:{stat.st_size}:{stat.st_mtime}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def _generate_encryption_key(self, clean_title: str, archive_hash: str) -> bytes:
        """Generate encryption key for installed files."""
        key_seed = f"{clean_title}:{archive_hash}"
        return ObfuscationUtils.generate_key(key_seed)

    def run_installation(self, show_ui: bool = True) -> bool:
        """Run the complete installation process."""
        if show_ui:
            return self._run_installation_with_ui()
        else:
            return self.install_game_files()

    def _run_installation_with_ui(self) -> bool:
        """Run installation with GUI (simplified, no threading)."""
        root = self.create_installer_ui()

        try:
            # Run installation on main thread with UI updates
            success = self._install_with_ui_updates(root)

            if success and not self.cancelled:
                # Show completion message briefly
                self.status_var.set("Installation complete! Starting game...")
                self.cancel_button.configure(text="Starting...", state='disabled')
                root.update()
                time.sleep(1)

                root.destroy()
                return True
            else:
                # Installation failed or was cancelled
                if not self.cancelled:
                    messagebox.showerror(
                        "Installation Failed",
                        "The game installation failed. Please try again or contact support."
                    )

                # Cleanup partial installation
                self.cleanup_failed_installation()
                root.destroy()
                return False

        except Exception as e:
            print(f"Installation error: {e}")
            try:
                messagebox.showerror("Installation Error", f"Installation failed: {str(e)}")
            except:
                pass

            self.cleanup_failed_installation()
            try:
                root.destroy()
            except:
                pass
            return False

    def _install_with_ui_updates(self, root) -> bool:
        """Install files with periodic UI updates on main thread."""
        try:
            # Create game data directory
            os.makedirs(self.game_data_dir, exist_ok=True)

            # Update: Loading archive
            self.update_progress_direct(0, 100, "Loading game archive...")
            root.update()

            archive = GameArchive()
            files = archive.load(self.archive_path)
            self.total_files = len(files)

            # Update: Preparing files
            self.update_progress_direct(5, 100, f"Preparing {self.total_files} files...")
            root.update()

            # Get project info for encryption
            project_config = {}
            if 'project.json' in files:
                project_config = json.loads(files['project.json'].decode('utf-8'))
                self.game_title = project_config.get('title', self.game_title)

            clean_title = clean_project_title(self.game_title)
            archive_hash = self._calculate_archive_hash()
            encryption_key = self._generate_encryption_key(clean_title, archive_hash)
            seed = int(archive_hash[:8], 16) if archive_hash else 12345

            # Update: Starting installation
            self.update_progress_direct(10, 100, f"Installing {self.game_title}...")
            root.update()

            # Install files with UI updates
            self.current_file = 0
            filename_mapping = {}

            for file_path, file_data in files.items():
                if self.cancelled:
                    return False

                self.current_file += 1

                # Update progress every file
                progress = 10 + (self.current_file / self.total_files * 80)
                self.update_progress_direct(progress, 100, f"Installing: {os.path.basename(file_path)}")

                # Update UI every 5 files to keep it responsive
                if self.current_file % 5 == 0:
                    root.update()
                    if self.cancelled:
                        return False

                try:
                    # Encrypt file data
                    encrypted_data = ObfuscationUtils.xor_data(file_data, encryption_key)

                    # Obfuscate filename
                    obfuscated_name = ObfuscationUtils.obfuscate_filename(file_path, seed)

                    # Determine output path
                    if file_path.startswith('assets/'):
                        asset_subpath = file_path[7:]
                        if asset_subpath:
                            obfuscated_name = ObfuscationUtils.obfuscate_filename(asset_subpath, seed)
                            output_dir = os.path.join(self.game_data_dir, 'assets')
                            os.makedirs(output_dir, exist_ok=True)
                            output_path = os.path.join(output_dir, f"{obfuscated_name}.enc")
                            filename_mapping[f"assets/{asset_subpath}"] = os.path.join('assets', f"{obfuscated_name}.enc")
                        else:
                            continue
                    else:
                        output_path = os.path.join(self.game_data_dir, f"{obfuscated_name}.enc")
                        filename_mapping[file_path] = f"{obfuscated_name}.enc"

                    # Write encrypted file
                    with open(output_path, 'wb') as f:
                        f.write(encrypted_data)

                except Exception as file_error:
                    print(f"Warning: Failed to install file {file_path}: {file_error}")
                    continue

            if self.cancelled:
                return False

            # Finalize installation
            self.update_progress_direct(95, 100, "Finalizing installation...")
            root.update()

            install_info = {
                'game_title': self.game_title,
                'installed_date': datetime.now().isoformat(),
                'archive_path': os.path.basename(self.archive_path),
                'archive_mtime': os.path.getmtime(self.archive_path),
                'archive_size': os.path.getsize(self.archive_path),
                'file_count': self.total_files,
                'encryption_key_hash': archive_hash,
                'filename_mapping': filename_mapping,
                'version': '1.0'
            }

            with open(self.install_info_path, 'w') as f:
                json.dump(install_info, f, indent=2)

            # Create completion marker
            with open(self.install_marker, 'w') as f:
                f.write(datetime.now().isoformat())

            self.update_progress_direct(100, 100, "Installation complete!")
            root.update()

            return True

        except Exception as e:
            print(f"Installation error: {e}")
            self.update_progress_direct(0, 100, f"Installation failed: {str(e)}")
            root.update()
            return False

    def update_progress_direct(self, current: int, total: int, status: str):
        """Update installation progress directly (no threading)."""
        if self.root and not self.cancelled:
            try:
                progress = (current / total * 100) if total > 0 else 0
                self.progress_var.set(progress)
                self.status_var.set(status)
            except tk.TclError:
                pass

    def cleanup_failed_installation(self):
        """Clean up after failed installation."""
        try:
            import shutil
            if os.path.exists(self.game_data_dir):
                shutil.rmtree(self.game_data_dir)
        except Exception:
            pass

    def validate_installation(self) -> bool:
        """Validate installation integrity."""
        if not self.is_installed():
            return False

        try:
            # Load installation info
            with open(self.install_info_path, 'r') as f:
                install_info = json.load(f)

            expected_file_count = install_info.get('file_count', 0)
            if expected_file_count == 0:
                return False

            # Check if archive has changed
            current_archive_mtime = os.path.getmtime(self.archive_path)
            current_archive_size = os.path.getsize(self.archive_path)

            if (install_info.get('archive_mtime', 0) != current_archive_mtime or
                install_info.get('archive_size', 0) != current_archive_size):
                return False

            # Count installed files
            installed_file_count = 0

            # Count main directory files
            if os.path.exists(self.game_data_dir):
                for file in os.listdir(self.game_data_dir):
                    if file.endswith('.enc') and not file.startswith('.'):
                        installed_file_count += 1

            # Count assets directory files
            assets_dir = os.path.join(self.game_data_dir, 'assets')
            if os.path.exists(assets_dir):
                for file in os.listdir(assets_dir):
                    if file.endswith('.enc'):
                        installed_file_count += 1

            # Verify file count matches
            if installed_file_count != expected_file_count:
                return False

            # Test loading a few files to verify encryption/decryption works
            mapping = self.get_installed_files_mapping()
            test_files = list(mapping.keys())[:3]  # Test first 3 files

            for file_path in test_files:
                try:
                    data = self.load_installed_file(file_path)
                    if data is None:
                        return False
                except Exception:
                    return False

            return True

        except Exception:
            return False

    def repair_installation(self, progress_callback: Callable = None) -> bool:
        """Attempt to repair a corrupted installation."""
        try:
            if progress_callback:
                progress_callback(0, 100, "Analyzing installation...")

            # Remove corrupted installation
            self.cleanup_failed_installation()

            if progress_callback:
                progress_callback(10, 100, "Removed corrupted files...")

            # Reinstall from scratch
            success = self.install_game_files(progress_callback)

            return success

        except Exception:
            return False

    def get_installation_info(self) -> Dict:
        """Get installation information."""
        if not self.is_installed():
            return {}

        try:
            with open(self.install_info_path, 'r') as f:
                install_info = json.load(f)

            # Add runtime info
            install_info['installation_path'] = self.game_data_dir
            install_info['installation_size'] = self._calculate_installation_size()
            install_info['is_valid'] = self.validate_installation()

            return install_info

        except Exception:
            return {}

    def _calculate_installation_size(self) -> int:
        """Calculate total size of installation."""
        total_size = 0

        if not os.path.exists(self.game_data_dir):
            return 0

        for root, dirs, files in os.walk(self.game_data_dir):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                except OSError:
                    pass

        return total_size

    def uninstall(self) -> bool:
        """Uninstall the game (remove installation)."""
        try:
            if os.path.exists(self.game_data_dir):
                import shutil
                shutil.rmtree(self.game_data_dir)
                return True
        except Exception:
            pass

        return False

    def get_installed_files_mapping(self) -> Dict[str, str]:
        """Get mapping of original filenames to installed encrypted files."""
        if not self.is_installed():
            return {}

        try:
            with open(self.install_info_path, 'r') as f:
                install_info = json.load(f)

            # Use stored filename mapping (more reliable than deobfuscation)
            stored_mapping = install_info.get('filename_mapping', {})

            # Convert relative paths to absolute paths
            mapping = {}
            for original_path, relative_encrypted_path in stored_mapping.items():
                absolute_encrypted_path = os.path.join(self.game_data_dir, relative_encrypted_path)
                if os.path.exists(absolute_encrypted_path):
                    mapping[original_path] = absolute_encrypted_path

            return mapping

        except Exception:
            # Fallback to old deobfuscation method if mapping not available
            try:
                with open(self.install_info_path, 'r') as f:
                    install_info = json.load(f)

                clean_title = clean_project_title(install_info['game_title'])
                archive_hash = install_info['encryption_key_hash']
                seed = int(archive_hash[:8], 16)

                # Build mapping by scanning installed files
                mapping = {}

                # Scan main directory
                for file in os.listdir(self.game_data_dir):
                    if file.endswith('.enc') and not file.startswith('.'):
                        original_name, file_seed = ObfuscationUtils.deobfuscate_filename(
                            file[:-4]  # Remove .enc extension
                        )
                        if original_name and file_seed == seed:
                            mapping[original_name] = os.path.join(self.game_data_dir, file)

                # Scan assets directory
                assets_dir = os.path.join(self.game_data_dir, 'assets')
                if os.path.exists(assets_dir):
                    for file in os.listdir(assets_dir):
                        if file.endswith('.enc'):
                            original_name, file_seed = ObfuscationUtils.deobfuscate_filename(
                                file[:-4]  # Remove .enc extension
                            )
                            if original_name and file_seed == seed:
                                mapping[f"assets/{original_name}"] = os.path.join(assets_dir, file)

                return mapping

            except Exception:
                return {}

    def load_installed_file(self, file_path: str) -> Optional[bytes]:
        """Load a specific file from the installation."""
        try:
            mapping = self.get_installed_files_mapping()
            if file_path not in mapping:
                return None

            encrypted_file_path = mapping[file_path]
            if not os.path.exists(encrypted_file_path):
                return None

            # Get decryption key
            with open(self.install_info_path, 'r') as f:
                install_info = json.load(f)

            clean_title = clean_project_title(install_info['game_title'])
            archive_hash = install_info['encryption_key_hash']
            encryption_key = self._generate_encryption_key(clean_title, archive_hash)

            # Read and decrypt file
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()

            return ObfuscationUtils.xor_data(encrypted_data, encryption_key)

        except Exception:
            return None