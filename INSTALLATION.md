# HEX-AVG Installation Guide

## 🚀 Quick Start - Download Pre-built Packages

We provide pre-built installable packages for both Windows and Linux. Download the latest release from:

[📦 Download HEX-AVG Releases](https://github.com/yourusername/hex-avg/releases/latest)

### Windows Installation

#### Option 1: Portable ZIP (Quick Testing)

**Best for:** Quick testing, portable use, no installation required

```powershell
# 1. Download hex-avg-windows-portable.zip from GitHub Releases
# 2. Extract to any folder (e.g., C:\hex-avg)
# 3. Open Command Prompt or PowerShell in that folder
# 4. Run:
hex-avg.exe scan --quick

# Or scan specific folder:
hex-avg.exe scan C:\Users\YourName\Downloads
```

**Advantages:**
- No installation required
- No admin privileges needed
- Portable - can run from USB drive
- Can be removed by simply deleting the folder

#### Option 2: NSIS Installer (Permanent Installation)

**Best for:** Regular use, system integration, PATH access

```powershell
# 1. Download HEX-AVG-Setup.exe from GitHub Releases
# 2. Double-click to run installer
# 3. Follow the installation wizard:
#    - Choose installation directory (default: C:\Program Files\HEX-AVG)
#    - Select components:
#      ✓ HEX-AVG Core (required)
#      ✓ Start Menu Shortcuts (recommended)
#      ✓ Desktop Shortcut (optional)
#      ✓ Add to PATH (recommended)
# 4. Click Install
# 5. Open Command Prompt and run:
hex-avg scan --quick
```

**Advantages:**
- Properly installed application
- Start Menu shortcuts
- Desktop shortcut (optional)
- Added to system PATH (run from anywhere)
- Easy uninstall via Control Panel

### Linux Installation

#### Option 1: Debian Package (Debian/Ubuntu/Kali)

**Best for:** System integration, automatic updates, dependency management

```bash
# 1. Download hex-avg_VERSION_amd64.deb from GitHub Releases
# 2. Install the package:
sudo dpkg -i hex-avg_VERSION_amd64.deb

# 3. Fix any missing dependencies (if needed):
sudo apt-get install -f

# 4. Run HEX-AVG:
hex-avg scan --quick

# Or scan system:
sudo hex-avg scan /
```

**What gets installed:**
- Binary: `/usr/bin/hex-avg`
- Files: `/usr/share/hex-avg/`
- Config: `/etc/hex-avg/config.yml`
- Documentation: `/usr/share/doc/hex-avg/`

**Advantages:**
- Proper system integration
- Automatic dependency management
- Easy updates via apt
- Easy removal: `sudo apt-get remove hex-avg`

#### Option 2: AppImage (Portable)

**Best for:** Testing, other distributions, no installation required

```bash
# 1. Download HEX-AVG-VERSION-x86_64.AppImage from GitHub Releases
# 2. Make it executable:
chmod +x HEX-AVG-VERSION-x86_64.AppImage

# 3. Run it:
./HEX-AVG-VERSION-x86_64.AppImage scan --quick

# Or scan specific directory:
./HEX-AVG-VERSION-x86_64.AppImage scan ~/Downloads
```

**Advantages:**
- Works on any Linux distribution
- No installation required
- No root privileges needed (for user directories)
- Portable - can run from USB drive

**Requirements:**
- FUSE kernel module (usually installed)
- Run with `--appimage-extract` if FUSE is not available

---

## 📦 Install from Source

For developers or those who want the latest development version.

### Prerequisites

- **Python 3.11 or higher**
- **Operating System:** Kali Linux, Ubuntu, Debian, or Windows 10/11

### Linux Installation (Source)

```bash
# 1. Clone the repository:
git clone https://github.com/yourusername/hex-avg.git
cd hex-avg

# 2. Install system dependencies:
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-dev python3-yara libyara-dev

# 3. Create virtual environment (recommended):
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies:
pip install --upgrade pip
pip install -r requirements.txt

# 5. Run HEX-AVG:
python hex_avg.py scan --quick

# 6. (Optional) Create system-wide symlink:
sudo ln -s $(pwd)/hex_avg.py /usr/local/bin/hex-avg
sudo chmod +x /usr/local/bin/hex-avg
```

### Windows Installation (Source)

```powershell
# 1. Clone the repository:
git clone https://github.com/yourusername/hex-avg.git
cd hex-avg

# 2. Install Python 3.11+ if not already installed
# Download from: https://www.python.org/downloads/

# 3. Create virtual environment (recommended):
python -m venv venv
.\venv\Scripts\Activate.ps1

# 4. Install Python dependencies:
pip install --upgrade pip
pip install -r requirements.txt

# 5. Run HEX-AVG:
python hex_avg.py scan --quick

# 6. (Optional) Add to PATH permanently:
# Add C:\path\to\hex-avg to your PATH environment variable
```

---

## 🤖 Automated Installation Scripts

We provide automated installation scripts for your convenience.

### Linux

```bash
# Download and run the automated installer:
chmod +x scripts/install_linux.sh
sudo ./scripts/install_linux.sh
```

This script will:
- Install system dependencies
- Create virtual environment
- Install Python packages
- Create system-wide symlink
- Run initial setup

### Windows

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the automated installer:
.\scripts\install_windows.ps1
```

This script will:
- Check Python installation
- Create virtual environment
- Install Python packages
- Create desktop shortcut (optional)
- Add to PATH (optional)

---

## 🔧 Post-Installation Setup

### Initial Configuration

```bash
# Initialize HEX-AVG (creates necessary directories):
hex-avg setup --init

# Check configuration:
hex-avg config --show

# Update virus signatures:
hex-avg update --signatures
```

### Test Installation

```bash
# Run a quick scan of common locations:
hex-avg scan --quick

# Test with EICAR test file (safe antivirus test):
hex-avg scan --test-eicar

# Verify version:
hex-avg --version
```

---

## 📋 System Requirements

### Minimum Requirements

**Windows:**
- Windows 10 or later
- 2 GB RAM
- 500 MB free disk space
- Python 3.11+ (source install only)

**Linux:**
- Any modern Linux distribution (kernel 3.10+)
- 2 GB RAM
- 500 MB free disk space
- Python 3.11+ (source install only)

### Recommended Requirements

- 4 GB RAM or more
- 1 GB free disk space
- Multi-core CPU for faster scanning
- SSD for better performance

---

## 🐛 Troubleshooting

### Windows Issues

**Issue: "Windows protected your PC" warning**
- Solution: Click "More info" → "Run anyway"
- This is a false positive from SmartScreen for unsigned executables

**Issue: Antivirus blocks HEX-AVG**
- Solution: Add HEX-AVG to antivirus exclusions
- This is common for security tools and PyInstaller executables

**Issue: PowerShell execution policy**
```powershell
# Fix execution policy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux Issues

**Issue: Permission denied when running**
```bash
# Fix permissions:
chmod +x hex-avg
# Or run with sudo (for system directories):
sudo hex-avg scan /
```

**Issue: Missing dependencies**
```bash
# For Debian package:
sudo apt-get install -f

# For source install:
sudo apt-get install python3-yara libyara-dev
```

**Issue: AppImage won't run**
```bash
# Make sure FUSE is installed:
sudo apt-get install fuse

# Or extract and run directly:
./HEX-AVG-VERSION-x86_64.AppImage --appimage-extract
./squashfs-root/AppRun scan --quick
```

### General Issues

**Issue: "Module not found" errors**
```bash
# Reinstall dependencies:
pip install --upgrade -r requirements.txt
```

**Issue: Scan is very slow**
- Reduce thread count: `hex-avg scan / --threads 4`
- Use quick scan: `hex-avg scan --quick`
- Exclude large directories: `hex-avg scan / --exclude /tmp`

---

## 🔄 Updating HEX-AVG

### Windows

**Portable Version:**
```powershell
# Download new version
# Extract over existing installation (or to new folder)
```

**Installer Version:**
```powershell
# Download and run new HEX-AVG-Setup.exe
# It will overwrite the old version
```

### Linux

**Debian Package:**
```bash
# Download new .deb package
sudo dpkg -i hex-avg_VERSION_amd64.deb
```

**AppImage:**
```bash
# Download new AppImage
chmod +x HEX-AVG-NEWVERSION-x86_64.AppImage
# Replace old file or keep both versions
```

**Source Installation:**
```bash
cd hex-avg
git pull origin main
pip install --upgrade -r requirements.txt
```

---

## 🗑️ Uninstallation

### Windows

**Portable Version:**
```powershell
# Simply delete the HEX-AVG folder
# No registry entries or system files to remove
```

**Installer Version:**
```powershell
# Use Control Panel → Programs and Features
# Select HEX-AVG → Uninstall
# Or run:
C:\Program Files\HEX-AVG\uninstall.exe
```

### Linux

**Debian Package:**
```bash
sudo apt-get remove hex-avg
# Or to remove configuration files too:
sudo apt-get purge hex-avg
# Remove unused dependencies:
sudo apt-get autoremove
```

**AppImage:**
```bash
# Simply delete the AppImage file
rm HEX-AVG-VERSION-x86_64.AppImage
```

**Source Installation:**
```bash
# Remove symlink:
sudo rm /usr/local/bin/hex-avg

# Delete the folder:
rm -rf /path/to/hex-avg
```

---

## 📚 Additional Resources

- [Documentation](docs/)
- [BUILD_SYSTEM.md](BUILD_SYSTEM.md) - Build and release information
- [GitHub Issues](https://github.com/yourusername/hex-avg/issues) - Report bugs
- [GitHub Discussions](https://github.com/yourusername/hex-avg/discussions) - Ask questions

---

## 🆘 Getting Help

If you encounter issues not covered in this guide:

1. Check the [troubleshooting section](#-troubleshooting) above
2. Search [GitHub Issues](https://github.com/yourusername/hex-avg/issues)
3. Create a new issue with:
   - Your operating system and version
   - HEX-AVG version (`hex-avg --version`)
   - Error messages or screenshots
   - Steps to reproduce the issue

---

**Happy scanning! 🛡️**