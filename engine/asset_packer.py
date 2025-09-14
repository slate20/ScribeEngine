"""
Scribe Engine Asset Packer
Handles packaging game projects into obfuscated archives for distribution.
"""

import os
import io
import json
import zipfile
import hashlib
import random
import struct
from datetime import datetime
from typing import Dict, List, Tuple, BinaryIO


class ObfuscationUtils:
    """Utilities for simple file obfuscation."""

    @staticmethod
    def generate_key(seed: str) -> bytes:
        """Generate a consistent key from a string seed."""
        return hashlib.sha256(seed.encode()).digest()[:16]

    @staticmethod
    def xor_data(data: bytes, key: bytes) -> bytes:
        """XOR data with a repeating key."""
        result = bytearray()
        for i, byte in enumerate(data):
            result.append(byte ^ key[i % len(key)])
        return bytes(result)

    @staticmethod
    def obfuscate_filename(filename: str, seed: int) -> str:
        """Create an obfuscated filename that can be reversed."""
        # Simple XOR-based obfuscation
        key = seed.to_bytes(4, 'big') * (len(filename) // 4 + 1)
        filename_bytes = filename.encode('utf-8')

        obfuscated_bytes = bytes(a ^ b for a, b in zip(filename_bytes, key))

        # Encode as base64-like but filesystem safe
        import base64
        encoded = base64.b64encode(obfuscated_bytes).decode('ascii')
        # Make filesystem safe
        safe_encoded = encoded.replace('/', '_').replace('+', '-').rstrip('=')

        return f"f{seed}_{safe_encoded}"

    @staticmethod
    def deobfuscate_filename(obfuscated: str) -> Tuple[str, int]:
        """Reverse filename obfuscation."""
        if not obfuscated.startswith('f'):
            return obfuscated, 0

        try:
            # Parse format: f{seed}_{encoded}
            parts = obfuscated[1:].split('_', 1)
            if len(parts) != 2:
                return obfuscated, 0

            seed = int(parts[0])
            safe_encoded = parts[1]

            # Restore base64 format
            encoded = safe_encoded.replace('_', '/').replace('-', '+')
            # Add padding if needed
            while len(encoded) % 4:
                encoded += '='

            import base64
            obfuscated_bytes = base64.b64decode(encoded)

            # XOR decrypt
            key = seed.to_bytes(4, 'big') * (len(obfuscated_bytes) // 4 + 1)
            filename_bytes = bytes(a ^ b for a, b in zip(obfuscated_bytes, key))

            original = filename_bytes.decode('utf-8')
            return original, seed

        except (ValueError, IndexError, base64.binascii.Error) as e:
            return obfuscated, 0


class GameArchive:
    """Handles reading/writing obfuscated game archives."""

    MAGIC_HEADER = b'SCGM'  # Scribe Game Magic
    VERSION = 1

    def __init__(self):
        self.files = {}  # filename -> data mapping
        self.metadata = {}

    def add_file(self, filename: str, data: bytes):
        """Add a file to the archive."""
        self.files[filename] = data

    def add_directory(self, dir_path: str, base_path: str = ""):
        """Recursively add directory contents."""
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, base_path if base_path else dir_path)

                try:
                    with open(file_path, 'rb') as f:
                        self.add_file(relative_path.replace('\\', '/'), f.read())
                except Exception as e:
                    print(f"Warning: Could not add file {file_path}: {e}")

    def save(self, output_path: str, project_name: str):
        """Save archive with obfuscation."""
        # Generate seed for this archive
        seed = hash(project_name + datetime.now().isoformat()) & 0x7FFFFFFF
        key = ObfuscationUtils.generate_key(project_name + str(seed))

        # Create in-memory ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add metadata
            metadata = {
                'project_name': project_name,
                'created': datetime.now().isoformat(),
                'version': self.VERSION,
                'file_count': len(self.files)
            }
            zf.writestr('_metadata.json', json.dumps(metadata, indent=2))

            # Add files with obfuscated names
            for filename, data in self.files.items():
                obfuscated_name = ObfuscationUtils.obfuscate_filename(filename, seed)
                obfuscated_data = ObfuscationUtils.xor_data(data, key)
                zf.writestr(obfuscated_name, obfuscated_data)

        # Get ZIP data
        zip_data = zip_buffer.getvalue()

        # Write obfuscated archive
        with open(output_path, 'wb') as f:
            # Write fake header to mask ZIP signature
            f.write(self.MAGIC_HEADER)
            f.write(struct.pack('<I', self.VERSION))
            f.write(struct.pack('<I', seed))
            f.write(struct.pack('<I', len(zip_data)))

            # XOR the ZIP data itself
            obfuscated_zip = ObfuscationUtils.xor_data(zip_data, key)
            f.write(obfuscated_zip)

    def load(self, archive_path: str, project_name: str) -> Dict[str, bytes]:
        """Load and deobfuscate archive."""
        with open(archive_path, 'rb') as f:
            # Read header
            magic = f.read(4)
            if magic != self.MAGIC_HEADER:
                raise ValueError("Invalid archive format")

            version = struct.unpack('<I', f.read(4))[0]
            seed = struct.unpack('<I', f.read(4))[0]
            zip_size = struct.unpack('<I', f.read(4))[0]

            # Read and deobfuscate ZIP data
            key = ObfuscationUtils.generate_key(project_name + str(seed))
            obfuscated_zip = f.read(zip_size)
            zip_data = ObfuscationUtils.xor_data(obfuscated_zip, key)

        # Read ZIP contents
        files = {}
        zip_buffer = io.BytesIO(zip_data)
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            for info in zf.infolist():
                if info.filename == '_metadata.json':
                    continue

                # Deobfuscate filename
                original_name, file_seed = ObfuscationUtils.deobfuscate_filename(info.filename)

                # Read and deobfuscate data
                obfuscated_data = zf.read(info.filename)
                original_data = ObfuscationUtils.xor_data(obfuscated_data, key)

                files[original_name] = original_data

        return files


class AssetPacker:
    """Main asset packer for Scribe Engine games."""

    def __init__(self):
        self.archive = GameArchive()

    def scan_project(self, project_path: str) -> List[str]:
        """Scan project directory and return list of files to pack."""
        if not os.path.exists(project_path):
            raise FileNotFoundError(f"Project path does not exist: {project_path}")

        files_to_pack = []

        # Define what to include
        include_patterns = [
            '*.tgame',    # Story files
            '*.py',       # Custom logic files
            '*.json',     # Configuration files
            '*.css',      # Custom styles
            'assets/**/*' # All asset files
        ]

        # Define what to exclude
        exclude_patterns = {
            'saves', 'temp_build', 'build', 'dist', 'spec',
            '__pycache__', '.git', '.vscode', '.idea',
            'venv', 'env', '*.pyc', '*.pyo'
        }

        for root, dirs, files in os.walk(project_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_patterns]

            for file in files:
                if file.startswith('.') or any(file.endswith(ext) for ext in ['.pyc', '.pyo']):
                    continue

                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_path)
                files_to_pack.append(relative_path.replace('\\', '/'))

        return files_to_pack

    def pack_project(self, project_path: str, output_dir: str, project_name: str = None) -> str:
        """Pack a project into an obfuscated archive."""
        if not os.path.exists(project_path):
            raise FileNotFoundError(f"Project path does not exist: {project_path}")

        # Get project name from config or path
        if not project_name:
            config_path = os.path.join(project_path, 'project.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    project_name = config.get('title', os.path.basename(project_path))
            else:
                project_name = os.path.basename(project_path)

        # Clean project name for filename
        clean_name = ''.join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_name = clean_name.replace(' ', '_')

        # Scan and add files
        files_to_pack = self.scan_project(project_path)
        print(f"Packing {len(files_to_pack)} files...")

        for file_path in files_to_pack:
            full_path = os.path.join(project_path, file_path)
            try:
                with open(full_path, 'rb') as f:
                    self.archive.add_file(file_path, f.read())
            except Exception as e:
                print(f"Warning: Could not pack file {file_path}: {e}")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save archive
        archive_path = os.path.join(output_dir, 'game.dat')
        self.archive.save(archive_path, clean_name)

        return archive_path

    def extract_embedded_player(self, output_dir: str, player_name: str = None) -> str:
        """Extract embedded ScribePlayer.exe from the engine."""
        import sys
        import shutil

        if not player_name:
            if sys.platform.startswith('win'):
                player_name = "ScribePlayer.exe"
            else:
                player_name = "ScribePlayer"

        player_path = os.path.join(output_dir, player_name)

        # Try to extract from embedded resources first
        embedded_player = None

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running from PyInstaller bundle - look for embedded player
            # Use platform-appropriate name for embedded player
            if sys.platform.startswith('win'):
                embedded_player_name = 'ScribePlayer.exe'
            else:
                embedded_player_name = 'ScribePlayer'

            resources_dir = os.path.join(sys._MEIPASS, 'resources')
            embedded_player = os.path.join(resources_dir, embedded_player_name)

            if not os.path.exists(embedded_player):
                # Try alternative locations
                embedded_player = os.path.join(sys._MEIPASS, embedded_player_name)

        # Fallback to development location
        if not embedded_player or not os.path.exists(embedded_player):
            engine_dir = os.path.dirname(os.path.dirname(__file__))
            # Try both with and without .exe extension
            source_player_exe = os.path.join(engine_dir, 'dist_tools', 'ScribePlayer.exe')
            source_player_no_exe = os.path.join(engine_dir, 'dist_tools', 'ScribePlayer')

            if os.path.exists(source_player_exe):
                embedded_player = source_player_exe
            elif os.path.exists(source_player_no_exe):
                embedded_player = source_player_no_exe
            else:
                print(f"Warning: ScribePlayer not found in development location:")
                print(f"  Tried: {source_player_exe}")
                print(f"  Tried: {source_player_no_exe}")

        # Extract/copy the player
        if embedded_player and os.path.exists(embedded_player):
            try:
                shutil.copy2(embedded_player, player_path)
                print(f"Extracted ScribePlayer to: {player_path}")

                # Make executable on Unix systems
                if not sys.platform.startswith('win'):
                    os.chmod(player_path, 0o755)

                return player_path
            except Exception as e:
                print(f"Error extracting ScribePlayer: {e}")
                return None
        else:
            print("Error: ScribePlayer not found in embedded resources or development location")
            return None

    def create_distribution(self, project_path: str, output_dir: str) -> dict:
        """Create complete game distribution."""
        import sys

        # Load project config
        config_path = os.path.join(project_path, 'project.json')
        if not os.path.exists(config_path):
            raise FileNotFoundError("project.json not found")

        with open(config_path, 'r') as f:
            config = json.load(f)

        project_title = config.get('title', 'Game')
        clean_title = ''.join(c for c in project_title if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_title = clean_title.replace(' ', '_')

        # Create distribution directory
        dist_dir = os.path.join(output_dir, f"{clean_title}_Distribution")
        os.makedirs(dist_dir, exist_ok=True)

        # Pack game data
        archive_path = self.pack_project(project_path, dist_dir, project_title)

        # Extract and rename player
        if sys.platform.startswith('win'):
            player_exe = f"{clean_title}.exe"
        else:
            player_exe = clean_title
        player_path = self.extract_embedded_player(dist_dir, player_exe)

        # Create distribution info
        info = {
            'project_title': project_title,
            'clean_title': clean_title,
            'distribution_dir': dist_dir,
            'game_archive': archive_path,
            'player_executable': player_path,
            'total_size': self._calculate_total_size(dist_dir),
            'created': datetime.now().isoformat()
        }

        # Save distribution info
        info_path = os.path.join(dist_dir, 'distribution_info.json')
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)

        return info

    def _calculate_total_size(self, directory: str) -> int:
        """Calculate total size of distribution."""
        total = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total += os.path.getsize(file_path)
                except OSError:
                    pass
        return total


# Utility functions for archive handling
def load_game_archive(archive_path: str, project_name: str) -> Dict[str, bytes]:
    """Load a game archive and return file contents."""
    archive = GameArchive()
    return archive.load(archive_path, project_name)

def is_game_archive(file_path: str) -> bool:
    """Check if a file is a valid game archive."""
    try:
        with open(file_path, 'rb') as f:
            magic = f.read(4)
            return magic == GameArchive.MAGIC_HEADER
    except Exception:
        return False