"""
Secure Cache System for Scribe Engine
Provides encrypted persistent caching with obfuscated filenames to maintain
security while improving game launch performance.
"""

import os
import json
import hashlib
import tempfile
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from .asset_packer import ObfuscationUtils, clean_project_title


class SecureCache:
    """Encrypted persistent cache for game files with tamper protection."""

    CACHE_VERSION = 1
    METADATA_FILE = "_cache_meta.enc"

    def __init__(self):
        self.cache_root = self._get_cache_directory()
        self.memory_cache = {}  # LRU cache for frequently accessed decrypted files
        self.memory_cache_size = 50 * 1024 * 1024  # 50MB limit
        self.memory_cache_usage = 0

    def _get_cache_directory(self) -> str:
        """Get platform-appropriate cache directory."""
        if os.name == 'nt':  # Windows
            cache_dir = os.path.join(os.environ.get('APPDATA', ''), 'ScribeEngine', 'cache')
        else:  # Linux/macOS
            cache_dir = os.path.join(os.path.expanduser('~'), '.cache', 'scribe-engine')

        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    def _generate_archive_hash(self, archive_path: str) -> str:
        """Generate unique hash for archive based on path, size, and modification time."""
        stat = os.stat(archive_path)
        hash_input = f"{archive_path}:{stat.st_size}:{stat.st_mtime}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def _get_cache_path(self, archive_hash: str) -> str:
        """Get cache directory path for specific archive."""
        cache_path = os.path.join(self.cache_root, archive_hash)
        os.makedirs(cache_path, exist_ok=True)
        return cache_path

    def _generate_encryption_key(self, project_title: str, archive_hash: str) -> bytes:
        """Generate encryption key from project title and archive hash."""
        clean_title = clean_project_title(project_title)
        key_seed = f"{clean_title}:{archive_hash}"
        return ObfuscationUtils.generate_key(key_seed)

    def _sanitize_project_config(self, config: Dict) -> Dict:
        """Sanitize project.json to remove sensitive development information."""
        sanitized = {}

        # Safe fields to include
        safe_fields = {
            'title', 'starting_passage', 'features', 'theme',
            'author', 'version', 'description'
        }

        for key, value in config.items():
            if key in safe_fields:
                sanitized[key] = value
            elif key == 'paths':
                # Skip all path information
                continue
            elif key == 'debug_mode':
                # Always disable debug mode in distribution
                sanitized[key] = False
            elif isinstance(value, (str, int, float, bool, list)):
                # Include simple data types that don't contain paths
                if not isinstance(value, str) or not ('/' in value or '\\' in value):
                    sanitized[key] = value

        return sanitized

    def _create_cache_metadata(self, archive_path: str, project_title: str,
                              file_manifest: List[str]) -> Dict:
        """Create cache metadata with integrity information."""
        archive_stat = os.stat(archive_path)

        return {
            'version': self.CACHE_VERSION,
            'created': datetime.now().isoformat(),
            'archive_path': os.path.basename(archive_path),  # Only filename, not full path
            'archive_size': archive_stat.st_size,
            'archive_mtime': archive_stat.st_mtime,
            'project_title': project_title,
            'file_count': len(file_manifest),
            'file_manifest': file_manifest,
            'integrity_hash': self._calculate_manifest_hash(file_manifest)
        }

    def _calculate_manifest_hash(self, file_manifest: List[str]) -> str:
        """Calculate integrity hash for file manifest."""
        manifest_str = ':'.join(sorted(file_manifest))
        return hashlib.sha256(manifest_str.encode()).hexdigest()

    def _classify_files(self, files: Dict[str, bytes]) -> Tuple[Dict[str, bytes], Dict[str, bytes]]:
        """Classify files into immediate (critical) and lazy (on-demand) categories."""
        immediate_files = {}
        lazy_files = {}

        for file_path, file_data in files.items():
            # Files needed immediately for engine initialization
            if (file_path.endswith(('.py', '.tgame', '.css')) or
                file_path == 'project.json' or
                file_path.startswith('templates/') or
                len(file_data) < 100 * 1024):  # Small files (< 100KB)
                immediate_files[file_path] = file_data
            else:
                # Large assets that can be loaded on-demand
                lazy_files[file_path] = file_data

        return immediate_files, lazy_files

    def _store_encrypted_file(self, cache_path: str, file_path: str, file_data: bytes,
                             encryption_key: bytes, seed: int) -> str:
        """Store file in cache with encryption and filename obfuscation."""
        # Encrypt file data
        encrypted_data = ObfuscationUtils.xor_data(file_data, encryption_key)

        # Obfuscate filename
        obfuscated_name = ObfuscationUtils.obfuscate_filename(file_path, seed)
        cache_file_path = os.path.join(cache_path, f"{obfuscated_name}.enc")

        # Write encrypted file
        with open(cache_file_path, 'wb') as f:
            f.write(encrypted_data)

        return cache_file_path

    def _load_encrypted_file(self, cache_file_path: str, encryption_key: bytes) -> bytes:
        """Load and decrypt file from cache."""
        with open(cache_file_path, 'rb') as f:
            encrypted_data = f.read()

        return ObfuscationUtils.xor_data(encrypted_data, encryption_key)

    def cache_archive(self, archive_path: str, files: Dict[str, bytes],
                     project_config: Dict) -> Tuple[str, Dict[str, bytes]]:
        """Cache archive files with encryption and return immediate files."""
        archive_hash = self._generate_archive_hash(archive_path)
        cache_path = self._get_cache_path(archive_hash)

        project_title = project_config.get('title', 'Game')
        encryption_key = self._generate_encryption_key(project_title, archive_hash)
        seed = int(archive_hash[:8], 16)  # Use part of hash as seed

        # Classify files
        immediate_files, lazy_files = self._classify_files(files)

        # Sanitize and store project config
        sanitized_config = self._sanitize_project_config(project_config)
        config_data = json.dumps(sanitized_config, indent=2).encode('utf-8')
        self._store_encrypted_file(cache_path, 'project.json', config_data,
                                  encryption_key, seed)

        # Store immediate files in cache
        immediate_manifest = []
        for file_path, file_data in immediate_files.items():
            if file_path != 'project.json':  # Already stored above
                self._store_encrypted_file(cache_path, file_path, file_data,
                                          encryption_key, seed)
                immediate_manifest.append(file_path)

        # Store lazy files in cache
        lazy_manifest = []
        for file_path, file_data in lazy_files.items():
            self._store_encrypted_file(cache_path, file_path, file_data,
                                      encryption_key, seed)
            lazy_manifest.append(file_path)

        # Create and store cache metadata
        all_manifest = ['project.json'] + immediate_manifest + lazy_manifest
        metadata = self._create_cache_metadata(archive_path, project_title, all_manifest)
        metadata_data = json.dumps(metadata, indent=2).encode('utf-8')

        metadata_encrypted = ObfuscationUtils.xor_data(metadata_data, encryption_key)
        metadata_path = os.path.join(cache_path, self.METADATA_FILE)
        with open(metadata_path, 'wb') as f:
            f.write(metadata_encrypted)

        return archive_hash, immediate_files

    def is_cache_valid(self, archive_path: str) -> bool:
        """Check if cache is valid for given archive."""
        try:
            archive_hash = self._generate_archive_hash(archive_path)
            cache_path = self._get_cache_path(archive_hash)
            metadata_path = os.path.join(cache_path, self.METADATA_FILE)

            if not os.path.exists(metadata_path):
                return False

            # Load and validate metadata
            metadata = self._load_cache_metadata(archive_hash, archive_path)
            if not metadata:
                return False

            # Check archive hasn't changed
            archive_stat = os.stat(archive_path)
            if (metadata['archive_size'] != archive_stat.st_size or
                metadata['archive_mtime'] != archive_stat.st_mtime):
                return False

            # Verify file manifest integrity
            current_hash = self._calculate_manifest_hash(metadata['file_manifest'])
            if current_hash != metadata['integrity_hash']:
                return False

            return True

        except Exception:
            return False

    def _load_cache_metadata(self, archive_hash: str, archive_path: str) -> Optional[Dict]:
        """Load and decrypt cache metadata."""
        try:
            cache_path = self._get_cache_path(archive_hash)
            metadata_path = os.path.join(cache_path, self.METADATA_FILE)

            # Read project title from archive to generate decryption key
            from .asset_packer import GameArchive
            archive = GameArchive()
            # Load just metadata to get project title
            with open(archive_path, 'rb') as f:
                magic = f.read(4)
                if magic != archive.MAGIC_HEADER:
                    return None

                version = f.read(4)
                title_length = int.from_bytes(f.read(4), 'little')
                project_title = f.read(title_length).decode('utf-8')

            encryption_key = self._generate_encryption_key(project_title, archive_hash)

            with open(metadata_path, 'rb') as f:
                encrypted_metadata = f.read()

            metadata_data = ObfuscationUtils.xor_data(encrypted_metadata, encryption_key)
            return json.loads(metadata_data.decode('utf-8'))

        except Exception:
            return None

    def load_immediate_files(self, archive_path: str) -> Optional[Dict[str, bytes]]:
        """Load immediate files from cache."""
        try:
            archive_hash = self._generate_archive_hash(archive_path)
            metadata = self._load_cache_metadata(archive_hash, archive_path)

            if not metadata:
                return None

            cache_path = self._get_cache_path(archive_hash)
            project_title = metadata['project_title']
            encryption_key = self._generate_encryption_key(project_title, archive_hash)
            seed = int(archive_hash[:8], 16)

            immediate_files = {}

            # Load files that should be available immediately
            for file_path in metadata['file_manifest']:
                if (file_path.endswith(('.py', '.tgame', '.css', '.json')) or
                    file_path.startswith('templates/')):

                    obfuscated_name = ObfuscationUtils.obfuscate_filename(file_path, seed)
                    cache_file_path = os.path.join(cache_path, f"{obfuscated_name}.enc")

                    if os.path.exists(cache_file_path):
                        file_data = self._load_encrypted_file(cache_file_path, encryption_key)
                        immediate_files[file_path] = file_data

            return immediate_files

        except Exception:
            return None

    def load_file_on_demand(self, archive_path: str, file_path: str) -> Optional[bytes]:
        """Load specific file from cache on-demand."""
        # Check memory cache first
        cache_key = f"{archive_path}:{file_path}"
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]

        try:
            archive_hash = self._generate_archive_hash(archive_path)
            metadata = self._load_cache_metadata(archive_hash, archive_path)

            if not metadata or file_path not in metadata['file_manifest']:
                return None

            cache_path = self._get_cache_path(archive_hash)
            project_title = metadata['project_title']
            encryption_key = self._generate_encryption_key(project_title, archive_hash)
            seed = int(archive_hash[:8], 16)

            obfuscated_name = ObfuscationUtils.obfuscate_filename(file_path, seed)
            cache_file_path = os.path.join(cache_path, f"{obfuscated_name}.enc")

            if not os.path.exists(cache_file_path):
                return None

            file_data = self._load_encrypted_file(cache_file_path, encryption_key)

            # Add to memory cache if there's space
            self._add_to_memory_cache(cache_key, file_data)

            return file_data

        except Exception:
            return None

    def _add_to_memory_cache(self, cache_key: str, file_data: bytes):
        """Add file to memory cache with LRU eviction."""
        data_size = len(file_data)

        # Don't cache very large files in memory
        if data_size > 10 * 1024 * 1024:  # 10MB limit per file
            return

        # Evict items if necessary
        while (self.memory_cache_usage + data_size > self.memory_cache_size and
               self.memory_cache):
            # Remove oldest item (simple FIFO for now)
            oldest_key = next(iter(self.memory_cache))
            oldest_data = self.memory_cache.pop(oldest_key)
            self.memory_cache_usage -= len(oldest_data)

        self.memory_cache[cache_key] = file_data
        self.memory_cache_usage += data_size

    def invalidate_cache(self, archive_path: str):
        """Invalidate and remove cache for specific archive."""
        try:
            archive_hash = self._generate_archive_hash(archive_path)
            cache_path = self._get_cache_path(archive_hash)

            if os.path.exists(cache_path):
                shutil.rmtree(cache_path)

            # Clear related memory cache entries
            keys_to_remove = [key for key in self.memory_cache.keys()
                             if key.startswith(f"{archive_path}:")]
            for key in keys_to_remove:
                data = self.memory_cache.pop(key)
                self.memory_cache_usage -= len(data)

        except Exception:
            pass

    def cleanup_old_caches(self, max_age_days: int = 30):
        """Clean up old cache directories."""
        try:
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)

            for cache_dir in os.listdir(self.cache_root):
                cache_path = os.path.join(self.cache_root, cache_dir)
                if os.path.isdir(cache_path):
                    if os.path.getctime(cache_path) < cutoff_time:
                        shutil.rmtree(cache_path)

        except Exception:
            pass