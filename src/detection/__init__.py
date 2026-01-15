"""
HEX-AVG Detection Module
Contains all detection engines (signature, heuristic, YARA)
"""

from .signature import SignatureDetector
from .heuristic import HeuristicDetector
from .yara_engine import YARADetector

__all__ = [
    "SignatureDetector",
    "HeuristicDetector",
    "YARADetector"
]