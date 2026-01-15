# HEX-AVG Configuration
# Central configuration management for HEX-AVG Antivirus

import os
import platform
from pathlib import Path
from typing import Dict, Any

class HEXAVGConfig:
    """Main configuration class for HEX-AVG"""
    
    # Version Information
    VERSION = "1.0.0"
    VERSION_NAME = "Phoenix"
    
    # Application Information
    APP_NAME = "HEX-AVG"
    APP_DESCRIPTION = "Professional Cross-Platform Antivirus for Cyber Security"
    
    # Base Directory Configuration
    BASE_DIR = Path(__file__).parent.absolute()
    
    # Platform Detection
    PLATFORM = platform.system().lower()
    IS_WINDOWS = PLATFORM == "windows"
    IS_LINUX = PLATFORM == "linux"
    
    # Directory Structure
    SRC_DIR = BASE_DIR / "src"
    SIGNATURES_DIR = BASE_DIR / "signatures"
    QUARANTINE_DIR = BASE_DIR / "quarantine"
    LOGS_DIR = BASE_DIR / "logs"
    REPORTS_DIR = BASE_DIR / "reports"
    TESTS_DIR = BASE_DIR / "tests"
    
    # Database Configuration
    SIGNATURE_DB = SIGNATURES_DIR / "signatures.db"
    SIGNATURE_BACKUP_DB = SIGNATURES_DIR / "signatures_backup.db"
    
    # YARA Rules Directory (Linux only)
    YARA_RULES_DIR = SIGNATURES_DIR / "rules"
    
    # Scanning Configuration
    DEFAULT_THREADS = 8
    MAX_THREADS = 32
    MIN_THREADS = 1
    CHUNK_SIZE = 8192  # File reading chunk size (8KB)
    
    # Hash Configuration
    HASH_ALGORITHMS = ["md5", "sha1", "sha256"]
    DEFAULT_HASH = "sha256"
    
    # Heuristic Configuration
    ENTROPY_THRESHOLD_HIGH = 7.5    # High entropy threshold (packed/encrypted)
    ENTROPY_THRESHOLD_LOW = 3.0     # Low entropy threshold (simple payload)
    
    # Suspicious File Extensions
    SUSPICIOUS_EXTENSIONS = {
        "windows": [
            ".exe", ".dll", ".sys", ".bat", ".cmd", ".ps1", ".vbs", ".js",
            ".jar", ".scr", ".pif", ".com", ".msi", ".cpl"
        ],
        "linux": [
            ".elf", ".sh", ".bash", ".py", ".pl", ".rb", ".so", ".deb", ".rpm"
        ]
    }
    
    # File Size Limits (bytes)
    MAX_SCAN_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
    MIN_EXECUTABLE_SIZE = 1024              # 1 KB
    MAX_EXECUTABLE_SIZE = 100 * 1024 * 1024 # 100 MB
    
    # Quick Scan Extensions to Skip
    QUICK_SCAN_SKIP_EXTENSIONS = [
        ".zip", ".tar", ".gz", ".rar", ".7z", ".iso", ".img",
        ".mp3", ".mp4", ".avi", ".mkv", ".mov", ".wmv",
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"
    ]
    
    # Quarantine Configuration
    QUARANTINE_ENCRYPTION_KEY = None  # Will be generated if None
    QUARANTINE_MAX_SIZE = 10 * 1024 * 1024 * 1024  # 10 GB
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = LOGS_DIR / "hex_avg.log"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT = 5
    
    # Report Configuration
    REPORT_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
    DEFAULT_REPORT_FORMAT = "json"
    
    # Update Configuration
    SIGNATURE_UPDATE_URL = "https://api.hex-avg.org/signatures/latest"
    UPDATE_CHECK_INTERVAL = 24  # hours
    AUTO_UPDATE_ENABLED = False
    
    # Performance Configuration
    ENABLE_CACHING = True
    CACHE_DIR = BASE_DIR / ".cache"
    CACHE_MAX_SIZE = 100 * 1024 * 1024  # 100 MB
    CACHE_TTL = 3600  # seconds (1 hour)
    
    # Safety Configuration
    DRY_RUN_DEFAULT = False
    SAFE_MODE_DEFAULT = True
    REQUIRE_CONFIRMATION = True
    MAX_SCAN_DURATION = 3600  # seconds (1 hour)
    
    # Memory Limits
    MAX_MEMORY_USAGE = 512 * 1024 * 1024  # 512 MB
    MEMORY_WARNING_THRESHOLD = 400 * 1024 * 1024  # 400 MB
    
    # Colors (Rich console)
    COLORS = {
        "success": "green",
        "warning": "yellow",
        "error": "red",
        "info": "blue",
        "debug": "dim",
        "highlight": "cyan"
    }
    
    # Scan Statistics
    STATISTICS_FIELDS = [
        "files_scanned",
        "files_skipped",
        "threats_found",
        "scan_duration",
        "start_time",
        "end_time"
    ]
    
    # Exit Codes
    EXIT_SUCCESS = 0
    EXIT_ERROR = 1
    EXIT_THREATS_FOUND = 2
    EXIT_INTERRUPTED = 130
    
    # EICAR Test String
    EICAR_STRING = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize configuration and create necessary directories"""
        # Create directories
        cls.SIGNATURES_DIR.mkdir(parents=True, exist_ok=True)
        cls.QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        cls.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.YARA_RULES_DIR.mkdir(parents=True, exist_ok=True)
        
        # Create cache directory if caching is enabled
        if cls.ENABLE_CACHING:
            cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_platform_extensions(cls) -> list:
        """Get suspicious extensions for current platform"""
        if cls.IS_WINDOWS:
            return cls.SUSPICIOUS_EXTENSIONS["windows"]
        elif cls.IS_LINUX:
            return cls.SUSPICIOUS_EXTENSIONS["linux"]
        return []
    
    @classmethod
    def get_system_paths(cls) -> list:
        """Get system paths to scan based on platform"""
        if cls.IS_WINDOWS:
            return [
                "C:\\Windows",
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                "C:\\Users"
            ]
        elif cls.IS_LINUX:
            return [
                "/bin",
                "/usr/bin",
                "/etc",
                "/home",
                "/tmp",
                "/var"
            ]
        return []
    
    @classmethod
    def validate(cls) -> Dict[str, bool]:
        """Validate configuration"""
        validation = {
            "directories_exist": all([
                cls.BASE_DIR.exists(),
                cls.SIGNATURES_DIR.exists(),
                cls.QUARANTINE_DIR.exists(),
                cls.LOGS_DIR.exists(),
                cls.REPORTS_DIR.exists()
            ]),
            "threads_valid": cls.MIN_THREADS <= cls.DEFAULT_THREADS <= cls.MAX_THREADS,
            "file_size_valid": cls.MIN_EXECUTABLE_SIZE < cls.MAX_EXECUTABLE_SIZE < cls.MAX_SCAN_FILE_SIZE,
            "entropy_valid": cls.ENTROPY_THRESHOLD_LOW < cls.ENTROPY_THRESHOLD_HIGH <= 8.0,
            "hash_algorithms_valid": all(h in ["md5", "sha1", "sha256"] for h in cls.HASH_ALGORITHMS)
        }
        return validation
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "version": cls.VERSION,
            "version_name": cls.VERSION_NAME,
            "platform": cls.PLATFORM,
            "base_dir": str(cls.BASE_DIR),
            "signature_db": str(cls.SIGNATURE_DB),
            "default_threads": cls.DEFAULT_THREADS,
            "max_threads": cls.MAX_THREADS,
            "hash_algorithms": cls.HASH_ALGORITHMS,
            "entropy_threshold_high": cls.ENTROPY_THRESHOLD_HIGH,
            "entropy_threshold_low": cls.ENTROPY_THRESHOLD_LOW,
            "max_scan_file_size": cls.MAX_SCAN_FILE_SIZE,
            "enable_caching": cls.ENABLE_CACHING,
            "safe_mode_default": cls.SAFE_MODE_DEFAULT
        }

# Initialize configuration when module is loaded
HEXAVGConfig.initialize()