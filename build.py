#!/usr/bin/env python3
"""
HEX-AVG Build Script
Automated build system for creating installable packages
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

# Add build directory to path
sys.path.insert(0, str(Path(__file__).parent / "build"))
from build_config import BuildConfig


class HexAvgBuilder:
    """HEX-AVG Build System"""
    
    def __init__(self):
        self.config = BuildConfig()
        self.version = self.config.load_version()
        self.platform = self.config.PLATFORM
        
    def print_banner(self):
        """Print build banner"""
        print("=" * 70)
        print("HEX-AVG Build System")
        print("=" * 70)
        print(f"Version: {self.version}")
        print(f"Platform: {self.platform}")
        print(f"Python: {sys.version.split()[0]}")
        print("=" * 70)
    
    def validate_environment(self):
        """Validate build environment"""
        print("\n🔍 Validating build environment...")
        
        errors = self.config.validate_environment()
        if errors:
            print("❌ Validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        print("✅ Environment validated successfully")
        
        # Check PyInstaller
        try:
            import PyInstaller
            print(f"✅ PyInstaller {PyInstaller.__version__} found")
        except ImportError:
            print("❌ PyInstaller not found. Install with: pip install pyinstaller")
            return False
        
        return True
    
    def clean_build(self):
        """Clean build directories"""
        print("\n🧹 Cleaning build directories...")
        
        dirs_to_clean = [
            self.config.BUILD_DIR / "build",
            self.config.DIST_DIR,
        ]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   Removed: {dir_path}")
        
        print("✅ Clean complete")
    
    def build_binary(self):
        """Build binary with PyInstaller"""
        print(f"\n🔨 Building binary with PyInstaller...")
        print(f"   Spec file: {self.config.SPEC_FILE}")
        
        if not self.config.SPEC_FILE.exists():
            print(f"❌ Spec file not found: {self.config.SPEC_FILE}")
            return False
        
        try:
            cmd = [
                "pyinstaller",
                str(self.config.SPEC_FILE),
                "--clean",
                "--noconfirm"
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Binary build completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed:")
            print(f"   Error: {e.stderr}")
            return False
    
    def build_windows_package(self):
        """Build Windows package"""
        print("\n📦 Building Windows package...")
        
        # Create portable ZIP
        print("   Creating portable ZIP...")
        if not self.config.OUTPUT_DIR.exists():
            print(f"❌ Output directory not found: {self.config.OUTPUT_DIR}")
            return False
        
        try:
            import zipfile
            zip_path = self.config.DIST_DIR / self.config.PORTABLE_ZIP
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.config.OUTPUT_DIR):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.config.OUTPUT_DIR)
                        zipf.write(file_path, arcname)
            
            print(f"✅ Portable ZIP created: {zip_path}")
            
            # Create NSIS installer (optional)
            if self.config.INSTALLER_SCRIPT.exists():
                print("   Creating NSIS installer...")
                try:
                    result = subprocess.run(
                        ["makensis", str(self.config.INSTALLER_SCRIPT)],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    print(f"✅ NSIS installer created: {self.config.INSTALLER_NAME}")
                except FileNotFoundError:
                    print("⚠️  NSIS not found, skipping installer creation")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️  NSIS build failed: {e.stderr}")
            
            return True
            
        except Exception as e:
            print(f"❌ Windows package build failed: {e}")
            return False
    
    def build_linux_package(self):
        """Build Linux package"""
        print("\n📦 Building Linux package...")
        
        # Create Debian package
        if self.config.DEB_SCRIPT.exists():
            print("   Creating Debian package...")
            try:
                result = subprocess.run(
                    ["bash", str(self.config.DEB_SCRIPT)],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=self.config.BUILD_DIR / "linux"
                )
                print("✅ Debian package created successfully")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Debian package build failed: {e.stderr}")
        
        # Create AppImage
        if self.config.APPIMAGE_SCRIPT.exists():
            print("   Creating AppImage...")
            try:
                result = subprocess.run(
                    ["bash", str(self.config.APPIMAGE_SCRIPT)],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=self.config.BUILD_DIR / "linux"
                )
                print("✅ AppImage created successfully")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  AppImage build failed: {e.stderr}")
        
        return True
    
    def generate_checksums(self):
        """Generate checksums for artifacts"""
        print("\n🔐 Generating checksums...")
        
        checksums = self.config.get_checksums()
        
        if checksums:
            checksum_file = self.config.DIST_DIR / "CHECKSUMS.txt"
            with open(checksum_file, 'w') as f:
                for artifact, hashes in checksums.items():
                    f.write(f"{artifact}\n")
                    f.write(f"  MD5:    {hashes['md5']}\n")
                    f.write(f"  SHA256: {hashes['sha256']}\n\n")
            
            print(f"✅ Checksums generated: {checksum_file}")
            print("\nChecksums:")
            for artifact, hashes in checksums.items():
                print(f"\n{artifact}:")
                print(f"  MD5:    {hashes['md5']}")
                print(f"  SHA256: {hashes['sha256']}")
        else:
            print("⚠️  No artifacts found for checksum generation")
    
    def print_summary(self):
        """Print build summary"""
        print("\n" + "=" * 70)
        print("Build Summary")
        print("=" * 70)
        
        # List created files
        print("\n📁 Created files:")
        if self.config.DIST_DIR.exists():
            for file_path in sorted(self.config.DIST_DIR.rglob("*")):
                if file_path.is_file():
                    size = file_path.stat().st_size / (1024 * 1024)  # MB
                    print(f"   {file_path.relative_to(self.config.DIST_DIR):<50} {size:>8.2f} MB")
        
        print("\n📦 Installable packages:")
        for artifact in self.config.get_output_files():
            artifact_path = self.config.DIST_DIR / artifact
            if artifact_path.exists():
                size = artifact_path.stat().st_size / (1024 * 1024)  # MB
                print(f"   ✅ {artifact:<50} {size:>8.2f} MB")
            else:
                print(f"   ❌ {artifact:<50} (not found)")
        
        print("\n" + "=" * 70)
    
    def build(self, clean=False):
        """Run complete build process"""
        self.print_banner()
        
        if not self.validate_environment():
            print("\n❌ Build aborted due to validation errors")
            return False
        
        if clean:
            self.clean_build()
        
        if not self.build_binary():
            print("\n❌ Build aborted due to binary build failure")
            return False
        
        # Build platform-specific packages
        if self.config.IS_WINDOWS:
            if not self.build_windows_package():
                print("\n⚠️  Windows package build had issues, but binary was created")
        elif self.config.IS_LINUX:
            self.build_linux_package()
        
        self.generate_checksums()
        self.print_summary()
        
        print("\n✅ Build completed successfully!")
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="HEX-AVG Build System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py              # Build all packages
  python build.py --clean      # Clean and build
  python build.py --config     # Show build configuration
  python build.py --validate   # Validate environment only
        """
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build directories before building"
    )
    
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show build configuration and exit"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate environment and exit"
    )
    
    args = parser.parse_args()
    
    # Show configuration
    if args.config:
        BuildConfig.print_config()
        return 0
    
    # Validate only
    builder = HexAvgBuilder()
    if args.validate:
        builder.print_banner()
        success = builder.validate_environment()
        return 0 if success else 1
    
    # Run build
    success = builder.build(clean=args.clean)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())