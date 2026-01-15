"""
HEX-AVG Background Services Module
Contains background service implementations for LEVEL-2 protection
"""

from .windows_service import HEXAVGWindowsService
from .linux_daemon import HEXAVGLinuxDaemon

__all__ = [
    "HEXAVGWindowsService",
    "HEXAVGLinuxDaemon"
]