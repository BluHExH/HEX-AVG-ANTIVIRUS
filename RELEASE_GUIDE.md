# HEX-AVG Release Guide - Quick Start

## 🚀 How to Create a Release

### Step 1: Test Locally First

```bash
# Install dependencies
pip install -r requirements.txt

# Build with PyInstaller
pyinstaller hex_avg.spec --clean --noconfirm

# Test the executable
./dist/hex-avg --version
./dist/hex-avg scan --quick
```

### Step 2: Push Code to GitHub

```bash
# Add your changes
git add .
git commit -m "Add new features"

# Push to main branch
git push origin main
```

### Step 3: Create Version Tag

```bash
# Tag the commit (replace X.Y.Z with your version)
git tag v3.0.1

# Push the tag (this triggers GitHub Actions)
git push origin v3.0.1
```

### Step 4: Verify Build

1. Go to: https://github.com/YOUR_USERNAME/hex-avg/actions
2. Click on the "Release - Build and Distribute" workflow
3. Watch the build progress
4. Wait for both Windows and Linux builds to complete

### Step 5: Download Binaries

1. Go to: https://github.com/YOUR_USERNAME/hex-avg/releases
2. Find the release (e.g., "v3.0.1")
3. Download:
   - **Windows:** `hex-avg.exe`
   - **Linux:** `hex-avg`

## 📋 What Gets Built

When you push a version tag, GitHub Actions automatically:

✅ **Builds Windows executable** (`hex-avg.exe`)
- Single executable file
- All dependencies bundled
- Works on Windows 10/11

✅ **Builds Linux binary** (`hex-avg`)
- Single executable file
- All dependencies bundled
- Works on modern Linux distributions

✅ **Creates GitHub Release**
- Attachs binaries to release page
- Generates release notes automatically
- Links to source archive

## 🎯 What Users Should Download

Users should download:

- **Windows users:** `hex-avg.exe` (NOT the .zip or .tar.gz)
- **Linux users:** `hex-avg` (NOT the .zip or .tar.gz)

The `.zip` and `.tar.gz` files are source archives that GitHub creates automatically. They are NOT the installable binaries.

## 🔍 Troubleshooting

### Build Fails on GitHub Actions

1. Check the Actions logs for error messages
2. Verify all dependencies are in `requirements.txt`
3. Ensure `hex_avg.spec` file exists
4. Test build locally first

### Executable Crashes on Launch

1. Check if all data files are included in spec file
2. Verify hidden imports are declared
3. Test the executable locally before releasing
4. Check for missing dependencies

### Wrong Version Number

1. Update `VERSION` in `config.py`
2. Update `VERSION` in `hex_avg.spec`
3. Commit changes
4. Create new tag with correct version

## 📦 Version Numbering

Follow semantic versioning: `vX.Y.Z`

- **X** = Major version (breaking changes)
- **Y** = Minor version (new features)
- **Z** = Patch version (bug fixes)

Examples:
- `v3.0.0` - Initial v3.0.0 release
- `v3.0.1` - Bug fix release
- `v3.1.0` - New features
- `v4.0.0` - Major changes

## 🎉 Success!

After following these steps, you'll have:

✅ Working Windows `.exe` executable
✅ Working Linux binary
✅ Professional GitHub Release
✅ Users can download and install easily

**HEX-AVG is now production-ready!**