"""
HEX-AVG Core Module
Contains the main scanning engine and core functionality
"""

from .scanner import HEXAVGScanner
from .file_traversal import FileTraversal
from .hasher import FileHasher
from .multithreading import ThreadManager

__all__ = [
    "HEXAVGScanner",
    "FileTraversal",
    "FileHasher",
    "ThreadManager"
]