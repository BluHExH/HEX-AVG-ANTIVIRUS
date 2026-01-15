"""
HEX-AVG Antivirus - Core Package
Professional Cross-Platform Antivirus for Cyber Security Learning
"""

__version__ = "1.0.0"
__author__ = "HEX-AVG Development Team"
__description__ = "Professional Cross-Platform Antivirus for Cyber Security"

# Import configuration
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import HEXAVGConfig

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "HEXAVGConfig"
]