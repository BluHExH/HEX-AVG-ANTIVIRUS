# HEX-AVG Build System Documentation

## Overview

HEX-AVG uses GitHub Actions for continuous integration and automated package creation. The build system automatically creates installable packages for both Windows and Linux platforms when code is pushed with version tags.

## Architecture

```
GitHub Repository
    ↓
Push with tag (e.g., v1.0.0)
    ↓
GitHub Actions Triggered
    ↓
┌─────────────────┬─────────────────┐
│  Windows Build  │  Linux Build    │
│  (Windows-2019) │  (Ubuntu-22.04) │
└────────┬────────┴────────┬────────┘
         ↓                 ↓
    PyInstaller      PyInstaller
         ↓                 ↓
  Portable .exe    Portable binary
         ↓                 ↓
    ZIP Package    .deb + AppImage
         └────────┬────────┘
                  ↓
         GitHub Release
                  ↓
         User Downloads
```

## Workflows

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Actions:**
- Runs on Ubuntu and Windows
- Python 3.11 setup
- Dependency installation
- Code linting (flake8)
- Type checking (mypy)
- Unit tests (pytest)
- Security scanning (Bandit)
- Coverage reporting (Codecov)

### 2. Build Workflow (`.github/workflows/build.yml`)

**Triggers:**
- Git tags matching `v*` (e.g., v1.0.0)
- Manual workflow dispatch

**Actions:**
- Builds Windows portable package
- Builds Linux .deb package
- Builds Linux AppImage
- Creates GitHub Release
- Attaches artifacts to release

## Build Artifacts

### Windows

1. **Portable ZIP** (`hex-avg-windows-portable.zip`)
   - Contains: `hex-avg.exe` + dependencies
   - No installation required
   - Extract and run

2. **NSIS Installer** (optional)
   - `HEX-AVG-Setup.exe`
   - Wizard-based installation
   - Creates Start Menu shortcuts
   - Adds to PATH (optional)

### Linux

1. **Debian Package** (`hex-avg_VERSION_amd64.deb`)
   - System package installation
   - Installs to `/usr/share/hex-avg/`
   - Creates `/usr/bin/hex-avg` symlink
   - Manages dependencies automatically

2. **AppImage** (`HEX-AVG-VERSION-x86_64.AppImage`)
   - Portable Linux executable
   - Works on any Linux distribution
   - No installation required
   - Single file bundle

## Local Building

### Prerequisites

**Windows:**
- Python 3.11+
- Visual Studio Build Tools (optional for some packages)
- NSIS (optional, for installer)

**Linux:**
- Python 3.11+
- Build essentials: `build-essential`, `python3-dev`
- YARA development: `libyara-dev`
- Packaging tools: `patchelf`, `dpkg-dev`

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/hex-avg.git
cd hex-avg

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller
```

### Windows Build

```bash
# Using PyInstaller spec file
pyinstaller build/windows/hex_avg.spec --clean --noconfirm

# Using NSIS for installer (optional)
makensis build/windows/installer.nsi
```

### Linux Build

```bash
# Using PyInstaller spec file
pyinstaller build/linux/hex_avg.spec --clean --noconfirm

# Create Debian package
chmod +x build/linux/create_deb.sh
build/linux/create_deb.sh

# Create AppImage
chmod +x build/linux/create_appimage.sh
build/linux/create_appimage.sh
```

## Release Process

### Automated Release (Recommended)

1. **Update version** in `config.py`:
   ```python
   VERSION = "1.0.1"  # Increment version
   ```

2. **Commit changes**:
   ```bash
   git add config.py
   git commit -m "Bump version to 1.0.1"
   ```

3. **Create and push tag**:
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```

4. **GitHub Actions** automatically:
   - Runs CI checks
   - Builds packages
   - Creates GitHub Release
   - Attaches artifacts

### Manual Release

1. Go to GitHub repository
2. Click "Releases" → "Create a new release"
3. Choose tag (must match format `v*`)
4. Add release notes
5. Click "Publish release"
6. GitHub Actions will attach build artifacts

## Release Notes Template

```markdown
## HEX-AVG vVERSION Release

### What's New
- Feature 1
- Feature 2
- Feature 3

### Bug Fixes
- Fixed issue 1
- Fixed issue 2

### Improvements
- Performance improvement 1
- Performance improvement 2

### Installation

#### Windows
- Download `hex-avg-windows-portable.zip`
- Extract and run `hex-avg.exe`

#### Linux (Debian/Ubuntu/Kali)
```bash
sudo dpkg -i hex-avg_VERSION_amd64.deb
```

#### Linux (Portable)
```bash
chmod +x HEX-AVG-VERSION-x86_64.AppImage
./HEX-AVG-VERSION-x86_64.AppImage
```

### Known Issues
- Issue 1
- Issue 2

### Upgrade Instructions
- Windows: Extract new version over old one
- Linux: `sudo dpkg -i hex-avg_VERSION_amd64.deb`
```

## Troubleshooting

### Build Failures

**Windows:**
- Ensure Visual Studio Build Tools are installed
- Check PyInstaller version compatibility
- Verify all dependencies in `requirements.txt`

**Linux:**
- Install system dependencies: `sudo apt-get install build-essential libyara-dev`
- Check Python version is 3.11+
- Verify `patchelf` is installed for AppImage

### Package Issues

**Windows:**
- Antivirus may flag PyInstaller binaries (add to exclusions)
- Disable real-time protection during build
- Use `--noconfirm` flag for PyInstaller

**Linux:**
- Debian package dependencies must be satisfied
- AppImage requires `fuse` on some systems
- Check file permissions: `chmod +x hex-avg`

### CI/CD Issues

**GitHub Actions:**
- Check workflow logs in Actions tab
- Verify secrets are configured
- Ensure runner has required permissions
- Check disk space on runner

**Artifacts:**
- Artifacts expire after 90 days (free tier)
- Download artifacts before expiration
- Use GitHub Releases for permanent storage

## Configuration

### Version Management

Version is managed in `config.py`:

```python
class HEXAVGConfig:
    VERSION = "1.0.0"
    VERSION_NAME = "Phoenix"
```

**Semantic Versioning:**
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Build Configuration

**PyInstaller Spec Files:**
- Windows: `build/windows/hex_avg.spec`
- Linux: `build/linux/hex_avg.spec`

**Key Settings:**
```python
# Included modules
hiddenimports=['src.core.scanner', 'src.detection.signature', ...]

# Excluded modules (reduce size)
excludes=['tkinter', 'matplotlib', 'numpy', ...]

# Data files
datas=[('signatures', 'signatures'), ('config.py', '.'), ...]
```

## Security

### Code Signing (Future Enhancement)

```yaml
# In build.yml
- name: Sign Windows executable
  run: |
    signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist/hex-avg.exe
```

### Virus Scanning

Build artifacts may be flagged by antivirus software. This is normal for:
- PyInstaller executables
- Security tools
- Packaged binaries

**Solutions:**
- Add to antivirus exclusions
- Sign executables with code signing certificate
- Submit to VirusTotal for verification

## Performance

### Build Times

- Windows: ~5-10 minutes
- Linux: ~3-5 minutes
- Total CI/CD: ~15-20 minutes

### Package Sizes

- Windows Portable: ~50-80 MB
- Windows Installer: ~50-80 MB
- Linux .deb: ~40-60 MB
- Linux AppImage: ~60-90 MB

## Maintenance

### Regular Tasks

1. **Update dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Test builds locally**:
   ```bash
   # Windows
   pyinstaller build/windows/hex_avg.spec
   
   # Linux
   pyinstaller build/linux/hex_avg.spec
   ```

3. **Update documentation**:
   - Keep BUILD_SYSTEM.md current
   - Update release notes
   - Document breaking changes

4. **Monitor CI/CD**:
   - Check workflow runs
   - Review build logs
   - Fix failing tests

## Support

### Issues

Report build system issues:
- GitHub Issues: `https://github.com/yourusername/hex-avg/issues`
- Label: `build-system`

### Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Test builds locally
5. Submit pull request

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [Debian Packaging Guide](https://www.debian.org/doc/manuals/debian-handbook/)
- [AppImage Documentation](https://docs.appimage.org/)
- [NSIS Documentation](https://nsis.sourceforge.io/Docs/)

## License

MIT License - See LICENSE file for details