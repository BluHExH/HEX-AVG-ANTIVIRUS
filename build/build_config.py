"""
HEX-AVG Build Configuration
Central configuration for all build processes
"""

from pathlib import Path
import platform

class BuildConfig:
    """Build configuration for HEX-AVG packaging"""
    
    # Project Information
    PROJECT_NAME = "HEX-AVG"
    PACKAGE_NAME = "hex-avg"
    DESCRIPTION = "Professional Cross-Platform Antivirus"
    URL = "https://github.com/yourusername/hex-avg"
    AUTHOR = "HEX-AVG Team"
    EMAIL = "contact@hex-avg.org"
    LICENSE = "MIT"
    
    # Version (imported from main config)
    VERSION = None  # Will be loaded from config.py
    
    # Directories
    ROOT_DIR = Path(__file__).parent.parent
    SRC_DIR = ROOT_DIR / "src"
    BUILD_DIR = ROOT_DIR / "build"
    DIST_DIR = ROOT_DIR / "dist"
    SIGNATURES_DIR = ROOT_DIR / "signatures"
    
    # Platform-specific configurations
    PLATFORM = platform.system().lower()
    IS_WINDOWS = PLATFORM == "windows"
    IS_LINUX = PLATFORM == "linux"
    
    # PyInstaller Configuration
    PYINSTALLER_VERSION = "5.13.0"
    
    # Windows Configuration
    if IS_WINDOWS:
        SPEC_FILE = BUILD_DIR / "windows" / "hex_avg.spec"
        INSTALLER_SCRIPT = BUILD_DIR / "windows" / "installer.nsi"
        OUTPUT_NAME = "hex-avg"
        OUTPUT_DIR = DIST_DIR / "hex-avg-windows"
        PORTABLE_ZIP = f"hex-avg-windows-portable.zip"
        INSTALLER_NAME = "HEX-AVG-Setup.exe"
        
    # Linux Configuration
    elif IS_LINUX:
        SPEC_FILE = BUILD_DIR / "linux" / "hex_avg.spec"
        DEB_SCRIPT = BUILD_DIR / "linux" / "create_deb.sh"
        APPIMAGE_SCRIPT = BUILD_DIR / "linux" / "create_appimage.sh"
        OUTPUT_NAME = "hex-avg"
        OUTPUT_DIR = DIST_DIR / "hex-avg-linux"
        DEB_PACKAGE = "hex-avg_{VERSION}_amd64.deb"
        APPIMAGE_NAME = "HEX-AVG-{VERSION}-x86_64.AppImage"
    
    # Included Data Files
    DATA_FILES = [
        ('signatures', 'signatures'),
        ('config.py', '.'),
        ('src', 'src'),
    ]
    
    # Hidden Imports (modules to include in binary)
    HIDDEN_IMPORTS = [
        'src.core.scanner',
        'src.core.file_traversal',
        'src.core.hasher',
        'src.core.multithreading',
        'src.detection.signature',
        'src.detection.heuristic',
        'src.detection.yara_engine',
        'src.detection.persistence',
        'src.services.windows_service',
        'src.monitoring.windows_monitor',
        'src.scheduler.scan_scheduler',
        'click',
        'rich',
        'tqdm',
        'psutil',
        'yaml',
        'cryptography',
    ]
    
    # Platform-specific hidden imports
    if IS_WINDOWS:
        HIDDEN_IMPORTS.extend([
            'yara',
            'pefile',
            'pywin32',
            'win32service',
        ])
    elif IS_LINUX:
        HIDDEN_IMPORTS.extend([
            'yara',
            'pyelftools',
            'pyinotify',
        ])
    
    # Excluded Modules (reduce binary size)
    EXCLUDED_MODULES = [
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'IPython',
        'jupyter',
        'notebook',
    ]
    
    # UPX Compression (reduce binary size)
    UPX_ENABLED = True
    
    # One-file vs One-dir mode
    ONE_FILE = False  # One-dir is better for maintainability
    
    # Console Application
    CONSOLE_MODE = True
    
    # Icon files (optional)
    if IS_WINDOWS:
        ICON_FILE = BUILD_DIR / "windows" / "icon.ico"
    
    # Build Artifacts
    ARTIFACTS = {
        'windows': [
            'hex-avg-windows-portable.zip',
            'HEX-AVG-Setup.exe',
        ],
        'linux': [
            'hex-avg_{VERSION}_amd64.deb',
            'HEX-AVG-{VERSION}-x86_64.AppImage',
        ],
    }
    
    @classmethod
    def load_version(cls):
        """Load version from main config.py"""
        try:
            import sys
            sys.path.insert(0, str(cls.ROOT_DIR))
            from config import HEXAVGConfig
            cls.VERSION = HEXAVGConfig.VERSION
            return cls.VERSION
        except ImportError:
            return "1.0.0"
    
    @classmethod
    def get_output_files(cls):
        """Get list of output files for current platform"""
        version = cls.load_version()
        artifacts = []
        
        if cls.IS_WINDOWS:
            artifacts = [
                cls.PORTABLE_ZIP,
                cls.INSTALLER_NAME,
            ]
        elif cls.IS_LINUX:
            artifacts = [
                cls.DEB_PACKAGE.replace('{VERSION}', version),
                cls.APPIMAGE_NAME.replace('{VERSION}', version),
            ]
        
        return artifacts
    
    @classmethod
    def get_checksums(cls):
        """Generate checksums for build artifacts"""
        import hashlib
        
        checksums = {}
        for artifact in cls.get_output_files():
            artifact_path = cls.DIST_DIR / artifact
            if artifact_path.exists():
                with open(artifact_path, 'rb') as f:
                    content = f.read()
                    checksums[artifact] = {
                        'md5': hashlib.md5(content).hexdigest(),
                        'sha256': hashlib.sha256(content).hexdigest(),
                    }
        return checksums
    
    @classmethod
    def validate_environment(cls):
        """Validate build environment"""
        errors = []
        
        # Check Python version
        import sys
        if sys.version_info < (3, 11):
            errors.append(f"Python 3.11+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        
        # Check required directories
        if not cls.ROOT_DIR.exists():
            errors.append(f"Root directory not found: {cls.ROOT_DIR}")
        if not cls.SRC_DIR.exists():
            errors.append(f"Source directory not found: {cls.SRC_DIR}")
        if not cls.SIGNATURES_DIR.exists():
            errors.append(f"Signatures directory not found: {cls.SIGNATURES_DIR}")
        
        # Check spec file
        if not cls.SPEC_FILE.exists():
            errors.append(f"PyInstaller spec file not found: {cls.SPEC_FILE}")
        
        # Check main executable
        main_script = cls.ROOT_DIR / "hex_avg.py"
        if not main_script.exists():
            errors.append(f"Main script not found: {main_script}")
        
        return errors
    
    @classmethod
    def print_config(cls):
        """Print current build configuration"""
        print("=" * 60)
        print("HEX-AVG Build Configuration")
        print("=" * 60)
        print(f"Project: {cls.PROJECT_NAME}")
        print(f"Version: {cls.load_version()}")
        print(f"Platform: {cls.PLATFORM}")
        print(f"PyInstaller: {cls.PYINSTALLER_VERSION}")
        print(f"Root Directory: {cls.ROOT_DIR}")
        print(f"Build Directory: {cls.BUILD_DIR}")
        print(f"Output Directory: {cls.DIST_DIR}")
        print("\nOutput Files:")
        for artifact in cls.get_output_files():
            print(f"  - {artifact}")
        print("=" * 60)


if __name__ == "__main__":
    BuildConfig.print_config()
    
    # Validate environment
    errors = BuildConfig.validate_environment()
    if errors:
        print("\n❌ Environment Validation Failed:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ Environment Validation Passed")