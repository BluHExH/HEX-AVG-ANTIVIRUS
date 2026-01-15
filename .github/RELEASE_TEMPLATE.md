## HEX-AVG v{VERSION} Release Notes

### 🎉 What's New

#### New Features
- **{Feature Name}**: {Description}
- **{Feature Name}**: {Description}
- **{Feature Name}**: {Description}

#### Improvements
- **{Improvement Name}**: {Description}
- **{Improvement Name}**: {Description}
- **{Improvement Name}**: {Description}

#### Bug Fixes
- **{Bug Name}**: {Description}
- **{Bug Name}**: {Description}
- **{Bug Name}**: {Description}

### 📦 Installation

#### Windows
1. Download `hex-avg-windows-portable.zip` or `HEX-AVG-Setup.exe`
2. For portable: Extract and run `hex-avg.exe`
3. For installer: Double-click and follow the wizard

```powershell
# Quick scan
hex-avg scan --quick

# Scan specific folder
hex-avg scan C:\Users\YourName\Downloads
```

#### Linux (Debian/Ubuntu/Kali)
```bash
# Download and install .deb package
wget https://github.com/yourusername/hex-avg/releases/download/v{VERSION}/hex-avg_{VERSION}_amd64.deb
sudo dpkg -i hex-avg_{VERSION}_amd64.deb
sudo apt-get install -f  # Fix dependencies if needed

# Run HEX-AVG
hex-avg scan --quick
```

#### Linux (AppImage - Portable)
```bash
# Download and make executable
wget https://github.com/yourusername/hex-avg/releases/download/v{VERSION}/HEX-AVG-{VERSION}-x86_64.AppImage
chmod +x HEX-AVG-{VERSION}-x86_64.AppImage

# Run HEX-AVG
./HEX-AVG-{VERSION}-x86_64.AppImage scan --quick
```

### 🔄 Upgrading

#### Windows
- **Portable**: Extract new version over old one
- **Installer**: Run new installer, it will update automatically

#### Linux
```bash
# Update .deb package
sudo dpkg -i hex-avg_{VERSION}_amd64.deb

# Or use apt if added to repository
sudo apt-get update
sudo apt-get install hex-avg
```

### 📋 System Requirements

#### Windows
- Windows 10 or later
- 2 GB RAM minimum (4 GB recommended)
- 500 MB free disk space

#### Linux
- Any modern Linux distribution (kernel 3.10+)
- 2 GB RAM minimum (4 GB recommended)
- 500 MB free disk space

### 🐛 Known Issues

- **{Issue 1}**: {Description and workaround}
- **{Issue 2}**: {Description and workaround}

### 📚 Documentation

- [Installation Guide](INSTALLATION.md)
- [User Documentation](docs/)
- [Build System Documentation](BUILD_SYSTEM.md)
- [GitHub Repository](https://github.com/yourusername/hex-avg)

### 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for a complete list of changes.

### ⚠️ Security Notes

- This release includes signature database updates
- YARA rules updated to version {YARA_VERSION}
- Security patches applied for known vulnerabilities

### 🙏 Acknowledgments

Thanks to all contributors who made this release possible:
- @{Contributor1} - {Contribution}
- @{Contributor2} - {Contribution}
- @{Contributor3} - {Contribution}

---

**Download from [GitHub Releases](https://github.com/yourusername/hex-avg/releases/tag/v{VERSION})**

**Release Date**: {DATE}
**Checksums**:
```
MD5:
SHA256:
```

---

## Need Help?

- 📖 [Documentation](docs/)
- 💬 [GitHub Discussions](https://github.com/yourusername/hex-avg/discussions)
- 🐛 [Report Issues](https://github.com/yourusername/hex-avg/issues)
- 📧 Email: support@hex-avg.org