"""
HEX-AVG File Traversal Module
Handles recursive file system traversal with permission handling
"""

import os
from pathlib import Path
from typing import Iterator, List, Set, Optional
from config import HEXAVGConfig


class FileTraversal:
    """Handles efficient file system traversal with smart filtering"""
    
    def __init__(
        self,
        skip_hidden: bool = True,
        skip_system: bool = True,
        max_depth: int = None
    ):
        """
        Initialize file traversal
        
        Args:
            skip_hidden: Skip hidden files and directories
            skip_system: Skip system directories
            max_depth: Maximum traversal depth (None = unlimited)
        """
        self.skip_hidden = skip_hidden
        self.skip_system = skip_system
        self.max_depth = max_depth
        
        # System directories to skip (platform-specific)
        self.system_dirs = self._get_system_directories()
        
        # Hidden file prefixes
        self.hidden_prefixes = {'.', '$'} if skip_hidden else set()
        
        # Statistics
        self.stats = {
            'files_scanned': 0,
            'files_skipped': 0,
            'dirs_scanned': 0,
            'dirs_skipped': 0,
            'permission_errors': 0
        }
    
    def _get_system_directories(self) -> Set[str]:
        """Get platform-specific system directories to skip"""
        if HEXAVGConfig.IS_WINDOWS:
            return {
                'Windows',
                '$Recycle.Bin',
                'System Volume Information',
                'ProgramData',
                'AppData',
                'Temporary Internet Files'
            }
        elif HEXAVGConfig.IS_LINUX:
            return {
                'proc',
                'sys',
                'dev',
                'run',
                'tmp',
                'var/run',
                'var/lock',
                'var/tmp'
            }
        return set()
    
    def _is_hidden(self, path: Path) -> bool:
        """Check if a path is hidden"""
        if not self.skip_hidden:
            return False
        
        # Check file/directory name
        name = path.name
        if any(name.startswith(prefix) for prefix in self.hidden_prefixes):
            return True
        
        return False
    
    def _is_system_dir(self, path: Path) -> bool:
        """Check if a path is a system directory"""
        if not self.skip_system:
            return False
        
        # Check against system directory list
        for part in path.parts:
            if part in self.system_dirs:
                return True
        
        return False
    
    def _should_skip(self, path: Path, is_dir: bool = False) -> bool:
        """
        Determine if a path should be skipped
        
        Args:
            path: Path to check
            is_dir: Whether the path is a directory
        
        Returns:
            True if should skip, False otherwise
        """
        # Check if hidden
        if self._is_hidden(path):
            return True
        
        # Check if system directory
        if is_dir and self._is_system_dir(path):
            return True
        
        # Check if path exists
        if not path.exists():
            return True
        
        return False
    
    def _can_read(self, path: Path) -> bool:
        """
        Check if a path can be read
        
        Args:
            path: Path to check
        
        Returns:
            True if readable, False otherwise
        """
        try:
            # Check read permission
            if os.access(path, os.R_OK):
                return True
            return False
        except (OSError, PermissionError):
            return False
    
    def traverse(
        self,
        root_path: Path,
        extensions_filter: Optional[List[str]] = None,
        skip_extensions: Optional[List[str]] = None
    ) -> Iterator[Path]:
        """
        Traverse file system recursively
        
        Args:
            root_path: Root directory to traverse
            extensions_filter: List of extensions to include (None = all)
            skip_extensions: List of extensions to skip
        
        Yields:
            Path objects for files to scan
        
        Raises:
            FileNotFoundError: If root_path doesn't exist
            ValueError: If root_path is not a directory
        """
        # Validate root path
        if not root_path.exists():
            raise FileNotFoundError(f"Path not found: {root_path}")
        
        if not root_path.is_dir():
            raise ValueError(f"Path is not a directory: {root_path}")
        
        # Normalize extensions for comparison
        if extensions_filter:
            extensions_filter = [ext.lower().lstrip('.') for ext in extensions_filter]
        
        if skip_extensions:
            skip_extensions = [ext.lower().lstrip('.') for ext in skip_extensions]
        
        # Traverse using scandir for better performance
        try:
            for entry in os.scandir(root_path):
                entry_path = Path(entry.path)
                
                # Check if should skip
                if self._should_skip(entry_path, entry.is_dir()):
                    if entry.is_dir():
                        self.stats['dirs_skipped'] += 1
                    else:
                        self.stats['files_skipped'] += 1
                    continue
                
                # Handle directories
                if entry.is_dir():
                    self.stats['dirs_scanned'] += 1
                    
                    # Recursively traverse if within depth limit
                    if self.max_depth is None or len(entry_path.parts) < len(Path(root_path).parts) + self.max_depth:
                        try:
                            yield from self.traverse(
                                entry_path,
                                extensions_filter,
                                skip_extensions
                            )
                        except (PermissionError, OSError):
                            self.stats['permission_errors'] += 1
                
                # Handle files
                elif entry.is_file():
                    # Check if file is readable
                    if not self._can_read(entry_path):
                        self.stats['permission_errors'] += 1
                        self.stats['files_skipped'] += 1
                        continue
                    
                    # Check extension filter
                    if extensions_filter:
                        ext = entry_path.suffix.lstrip('.').lower()
                        if ext not in extensions_filter:
                            self.stats['files_skipped'] += 1
                            continue
                    
                    # Check skip extensions
                    if skip_extensions:
                        ext = entry_path.suffix.lstrip('.').lower()
                        if ext in skip_extensions:
                            self.stats['files_skipped'] += 1
                            continue
                    
                    # Yield file path
                    self.stats['files_scanned'] += 1
                    yield entry_path
                
                else:
                    # Handle other types (symlinks, etc.)
                    self.stats['files_skipped'] += 1
        
        except (PermissionError, OSError):
            self.stats['permission_errors'] += 1
            raise
    
    def get_files_list(
        self,
        root_path: Path,
        extensions_filter: Optional[List[str]] = None,
        skip_extensions: Optional[List[str]] = None
    ) -> List[Path]:
        """
        Get a list of all files to scan
        
        Args:
            root_path: Root directory to traverse
            extensions_filter: List of extensions to include (None = all)
            skip_extensions: List of extensions to skip
        
        Returns:
            List of Path objects
        """
        return list(self.traverse(root_path, extensions_filter, skip_extensions))
    
    def get_statistics(self) -> dict:
        """Get traversal statistics"""
        return self.stats.copy()
    
    def reset_statistics(self) -> None:
        """Reset traversal statistics"""
        self.stats = {
            'files_scanned': 0,
            'files_skipped': 0,
            'dirs_scanned': 0,
            'dirs_skipped': 0,
            'permission_errors': 0
        }
    
    def estimate_time(
        self,
        file_count: int,
        avg_time_per_file: float = 0.01
    ) -> float:
        """
        Estimate time to scan files
        
        Args:
            file_count: Number of files to scan
            avg_time_per_file: Average time per file in seconds
        
        Returns:
            Estimated time in seconds
        """
        return file_count * avg_time_per_file