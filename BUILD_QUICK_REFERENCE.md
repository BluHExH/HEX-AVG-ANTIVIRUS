# HEX-AVG Build System - Quick Reference

## 🚀 Quick Start

### For Users - Download & Install

#### Windows
```powershell
# Option 1: Portable
# Download hex-avg-windows-portable.zip
# Extract and run:
hex-avg.exe scan --quick

# Option 2: Installer
# Download HEX-AVG-Setup.exe
# Double-click to install
hex-avg scan --quick
```

#### Linux
```bash
# Option 1: Debian Package
sudo dpkg -i hex-avg_1.0.0_amd64.deb
hex-avg scan --quick

# Option 2: AppImage
chmod +x HEX-AVG-1.0.0-x86_64.AppImage
./HEX-AVG-1.0.0-x86_64.AppImage scan --quick
```

---

### For Developers - Build & Release

#### Local Build
```bash
# Build all packages
python build.py

# Clean build
python build.py --clean

# Check configuration
python build.py --config

# Validate environment
python build.py --validate
```

#### GitHub Release
```bash
# 1. Update version in config.py
VERSION = "1.0.1"

# 2. Commit and tag
git add config.py
git commit -m "Bump version to 1.0.1"
git tag v1.0.1
git push origin v1.0.1

# 3. GitHub Actions automatically builds and releases
```

---

## 📁 File Structure

```
.github/workflows/
├── ci.yml              # Continuous Integration
└── build.yml           # Automated Build & Release

build/
├── windows/
│   ├── hex_avg.spec    # Windows PyInstaller config
│   └── installer.nsi   # NSIS installer
├── linux/
│   ├── hex_avg.spec    # Linux PyInstaller config
│   ├── create_deb.sh   # Debian builder
│   └── create_appimage.sh  # AppImage builder
└── build_config.py     # Central config

build.py                # Local build script
BUILD_SYSTEM.md         # Complete docs
INSTALLATION.md         # User guide
```

---

## 🔧 Commands Reference

### PyInstaller
```bash
# Windows
pyinstaller build/windows/hex_avg.spec --clean --noconfirm

# Linux
pyinstaller build/linux/hex_avg.spec --clean --noconfirm
```

### Debian Package
```bash
cd build/linux
./create_deb.sh
```

### AppImage
```bash
cd build/linux
./create_appimage.sh
```

### NSIS Installer (Windows)
```bash
makensis build/windows/installer.nsi
```

---

## 📦 Build Artifacts

### Windows
- `hex-avg-windows-portable.zip` (~50-80 MB)
- `HEX-AVG-Setup.exe` (~50-80 MB)

### Linux
- `hex-avg_VERSION_amd64.deb` (~40-60 MB)
- `HEX-AVG-VERSION-x86_64.AppImage` (~60-90 MB)

---

## 🔐 Checksums

Generated automatically in `dist/CHECKSUMS.txt`:
```bash
# Verify download
sha256sum -c CHECKSUMS.txt
```

---

## 🐛 Troubleshooting

### Windows
```powershell
# Execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# SmartScreen warning
# Click "More info" → "Run anyway"
```

### Linux
```bash
# Permission denied
chmod +x hex-avg

# Missing dependencies
sudo apt-get install -f

# AppImage won't run
sudo apt-get install fuse
# Or extract: ./AppImage --appimage-extract
```

---

## 📚 Documentation Links

- [BUILD_SYSTEM.md](BUILD_SYSTEM.md) - Complete build documentation
- [INSTALLATION.md](INSTALLATION.md) - User installation guide
- [BUILD_SYSTEM_SUMMARY.md](BUILD_SYSTEM_SUMMARY.md) - Implementation details
- [README.md](README.md) - Project overview

---

## 🔄 Update Process

### Windows
```powershell
# Download new version
# Extract over old one (portable)
# Run new installer (installer)
```

### Linux
```bash
# Update .deb
sudo dpkg -i hex-avg_1.0.1_amd64.deb

# Update AppImage
chmod +x HEX-AVG-1.0.1-x86_64.AppImage
```

---

## 🗑️ Uninstall

### Windows
```powershell
# Portable: Delete folder
# Installer: Control Panel → Programs → Uninstall
```

### Linux
```bash
# .deb package
sudo apt-get remove hex-avg

# AppImage
rm HEX-AVG-1.0.0-x86_64.AppImage
```

---

## 📞 Help

- GitHub Issues: https://github.com/yourusername/hex-avg/issues
- GitHub Discussions: https://github.com/yourusername/hex-avg/discussions
- Email: support@hex-avg.org

---

**Version: 1.0.0** | **Last Updated: 2024**