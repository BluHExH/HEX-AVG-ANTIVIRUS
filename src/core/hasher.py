"""
HEX-AVG File Hasher Module
Handles cryptographic hash calculations for files
"""

import hashlib
from pathlib import Path
from typing import Dict, Optional
from config import HEXAVGConfig


class FileHasher:
    """Handles file hashing operations with multiple algorithms"""
    
    def __init__(self):
        """Initialize the file hasher"""
        self.chunk_size = HEXAVGConfig.CHUNK_SIZE
        self.algorithms = HEXAVGConfig.HASH_ALGORITHMS
    
    def hash_file(
        self,
        file_path: Path,
        algorithms: Optional[list] = None
    ) -> Dict[str, str]:
        """
        Calculate hashes for a file using specified algorithms
        
        Args:
            file_path: Path to the file
            algorithms: List of hash algorithms to use (default: from config)
        
        Returns:
            Dictionary mapping algorithm names to hash values
        
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        if algorithms is None:
            algorithms = self.algorithms
        
        # Initialize hash objects for each algorithm
        hashers = {
            algo: hashlib.new(algo)
            for algo in algorithms
        }
        
        try:
            # Read file in chunks and update hashes
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    # Update all hashers with the same chunk
                    for hasher in hashers.values():
                        hasher.update(chunk)
            
            # Return hex digest for each algorithm
            return {
                algo: hasher.hexdigest()
                for algo, hasher in hashers.items()
            }
        
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Error hashing file {file_path}: {str(e)}")
    
    def hash_file_single(
        self,
        file_path: Path,
        algorithm: str = HEXAVGConfig.DEFAULT_HASH
    ) -> str:
        """
        Calculate a single hash for a file
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use
        
        Returns:
            Hexadecimal hash string
        """
        hashes = self.hash_file(file_path, [algorithm])
        return hashes[algorithm]
    
    def hash_string(
        self,
        data: str,
        algorithm: str = HEXAVGConfig.DEFAULT_HASH
    ) -> str:
        """
        Calculate hash of a string
        
        Args:
            data: String to hash
            algorithm: Hash algorithm to use
        
        Returns:
            Hexadecimal hash string
        """
        hasher = hashlib.new(algorithm)
        hasher.update(data.encode('utf-8'))
        return hasher.hexdigest()
    
    def hash_bytes(
        self,
        data: bytes,
        algorithm: str = HEXAVGConfig.DEFAULT_HASH
    ) -> str:
        """
        Calculate hash of bytes
        
        Args:
            data: Bytes to hash
            algorithm: Hash algorithm to use
        
        Returns:
            Hexadecimal hash string
        """
        hasher = hashlib.new(algorithm)
        hasher.update(data)
        return hasher.hexdigest()
    
    def compare_hashes(
        self,
        hash1: str,
        hash2: str,
        algorithm: str = None
    ) -> bool:
        """
        Compare two hash strings
        
        Args:
            hash1: First hash string
            hash2: Second hash string
            algorithm: Algorithm used (for validation)
        
        Returns:
            True if hashes match, False otherwise
        """
        # Normalize hashes (lowercase, strip whitespace)
        hash1 = hash1.lower().strip()
        hash2 = hash2.lower().strip()
        
        # Validate hash length if algorithm specified
        if algorithm:
            expected_lengths = {
                'md5': 32,
                'sha1': 40,
                'sha256': 64
            }
            expected_length = expected_lengths.get(algorithm)
            if expected_length:
                if len(hash1) != expected_length or len(hash2) != expected_length:
                    return False
        
        return hash1 == hash2
    
    def verify_file_integrity(
        self,
        file_path: Path,
        expected_hash: str,
        algorithm: str = HEXAVGConfig.DEFAULT_HASH
    ) -> bool:
        """
        Verify file integrity by comparing hash
        
        Args:
            file_path: Path to the file
            expected_hash: Expected hash value
            algorithm: Hash algorithm to use
        
        Returns:
            True if hash matches, False otherwise
        """
        try:
            actual_hash = self.hash_file_single(file_path, algorithm)
            return self.compare_hashes(actual_hash, expected_hash, algorithm)
        except Exception:
            return False
    
    def get_file_info_hash(
        self,
        file_path: Path
    ) -> Dict[str, str]:
        """
        Get file information and hash for quick identification
        
        Args:
            file_path: Path to the file
        
        Returns:
            Dictionary with file info and hashes
        """
        try:
            file_stat = file_path.stat()
            hashes = self.hash_file(file_path, ['md5', 'sha256'])
            
            return {
                'path': str(file_path),
                'size': file_stat.st_size,
                'modified': file_stat.st_mtime,
                'md5': hashes['md5'],
                'sha256': hashes['sha256']
            }
        except Exception as e:
            return {
                'path': str(file_path),
                'error': str(e)
            }
    
    @staticmethod
    def is_valid_hash(
        hash_string: str,
        algorithm: str = None
    ) -> bool:
        """
        Validate if a string is a valid hash
        
        Args:
            hash_string: Hash string to validate
            algorithm: Algorithm to check against
        
        Returns:
            True if valid hash, False otherwise
        """
        if not hash_string or not isinstance(hash_string, str):
            return False
        
        # Remove whitespace and convert to lowercase
        hash_string = hash_string.strip().lower()
        
        # Check if it's a hexadecimal string
        if not all(c in '0123456789abcdef' for c in hash_string):
            return False
        
        # Check length if algorithm specified
        if algorithm:
            expected_lengths = {
                'md5': 32,
                'sha1': 40,
                'sha256': 64
            }
            expected_length = expected_lengths.get(algorithm)
            if expected_length and len(hash_string) != expected_length:
                return False
        
        # Generally valid lengths for common algorithms
        valid_lengths = [32, 40, 64]
        return len(hash_string) in valid_lengths