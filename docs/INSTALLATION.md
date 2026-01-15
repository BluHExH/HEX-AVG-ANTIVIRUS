# HEX-AVG Installation Guide

Complete installation instructions for HEX-AVG Antivirus on Kali Linux and Windows.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation on Kali Linux](#installation-on-kali-linux)
3. [Installation on Windows](#installation-on-windows)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

- **Operating System**:
  - Kali Linux 2023+ or similar Debian-based distributions
  - Windows 10/11 (64-bit)
  
- **Python**: 3.11 or higher
  
- **RAM**: 2GB minimum (4GB recommended)
  
- **Disk Space**: 500MB for installation, additional space for quarantine and logs

### Recommended Requirements

- **RAM**: 8GB or more
- **CPU**: Multi-core processor (4+ cores recommended)
- **Disk Space**: 2GB or more
- **Internet Connection**: For signature updates

---

## Installation on Kali Linux

### Method 1: Automated Installation (Recommended)

1. **Download HEX-AVG**:
   ```bash
   cd ~/Downloads
   git clone https://github.com/yourusername/hex-avg.git
   cd hex-avg
   ```

2. **Run the installation script**:
   ```bash
   chmod +x scripts/install_linux.sh
   sudo ./scripts/install_linux.sh
   ```

3. **Verify installation**:
   ```bash
   hex-avg --version
   ```

### Method 2: Manual Installation

#### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

#### Step 2: Install Dependencies

```bash
# Install Python and development tools
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install security analysis tools
sudo apt install -y yara clamav binutils gdb
```

#### Step 3: Create Project Directory

```bash
mkdir -p ~/hex-avg
cd ~/hex-avg
```

#### Step 4: Download HEX-AVG

```bash
# If you have the source code
cp -r /path/to/hex-avg/source/* ~/hex-avg/

# Or clone from repository
git clone https://github.com/yourusername/hex-avg.git ~/hex-avg
cd ~/hex-avg
```

#### Step 5: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 6: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 7: Initialize HEX-AVG

```bash
python hex_avg.py setup init
```

#### Step 8: Create System-Wide Command (Optional)

```bash
sudo ln -s $(pwd)/hex_avg.py /usr/local/bin/hex-avg
sudo chmod +x /usr/local/bin/hex-avg
```

#### Step 9: Verify Installation

```bash
hex-avg --version
hex-avg setup check
```

---

## Installation on Windows

### Method 1: Automated Installation (Recommended)

1. **Download HEX-AVG**:
   - Download the ZIP file from GitHub
   - Extract to `C:\hex-avg`

2. **Run PowerShell as Administrator**:
   - Right-click on PowerShell
   - Select "Run as Administrator"

3. **Navigate to installation directory**:
   ```powershell
   cd C:\hex-avg
   ```

4. **Run the installation script**:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\scripts\install_windows.ps1
   ```

5. **Verify installation**:
   ```powershell
   python hex_avg.py --version
   ```

### Method 2: Manual Installation

#### Step 1: Install Python

1. Download Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. Run the installer with the following options:
   - ✅ Add Python to PATH
   - ✅ Install for all users
3. Verify installation:
   ```powershell
   python --version
   ```

#### Step 2: Create Installation Directory

```powershell
New-Item -ItemType Directory -Path "C:\hex-avg" -Force
cd C:\hex-avg
```

#### Step 3: Download HEX-AVG

- Extract the HEX-AVG source code to `C:\hex-avg`
- Ensure `hex_avg.py` and `requirements.txt` are in the root directory

#### Step 4: Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

*Note: If you see an error about execution policy, run:*
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Step 5: Install Python Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 6: Initialize HEX-AVG

```powershell
python hex_avg.py setup init
```

#### Step 7: Add to PATH (Optional)

1. Search for "Environment Variables" in Windows
2. Click "Edit the system environment variables"
3. Click "Environment Variables"
4. Under "User variables", find "Path" and click "Edit"
5. Click "New" and add: `C:\hex-avg`
6. Click "OK" to save

#### Step 8: Create Desktop Shortcut (Optional)

1. Right-click on desktop → New → Shortcut
2. Location: `C:\hex-avg\hex_avg.py --help`
3. Name: HEX-AVG Antivirus
4. Click "Finish"

#### Step 9: Verify Installation

```powershell
cd C:\hex-avg
python hex_avg.py --version
python hex_avg.py setup check
```

---

## Verification

### Linux Verification

```bash
# Check version
hex-avg --version

# Run setup check
hex-avg setup check

# Test with EICAR
hex-avg benchmark --test-eicar
```

Expected output:
```
HEX-AVG v1.0.0
All checks passed
✓ EICAR test virus detected successfully!
```

### Windows Verification

```powershell
# Check version
python hex_avg.py --version

# Run setup check
python hex_avg.py setup check

# Test with EICAR
python hex_avg.py benchmark --test-eicar
```

Expected output:
```
HEX-AVG v1.0.0
All checks passed
✓ EICAR test virus detected successfully!
```

---

## Troubleshooting

### Linux Issues

#### Issue: Permission Denied

**Error**: `bash: ./hex_avg.py: Permission denied`

**Solution**:
```bash
chmod +x hex_avg.py
```

#### Issue: Python Not Found

**Error**: `python3: command not found`

**Solution**:
```bash
sudo apt install python3 python3-pip
```

#### Issue: YARA Installation Fails

**Error**: `yara-python installation failed`

**Solution**:
```bash
sudo apt install libyara-dev
pip install yara-python
```

#### Issue: Virtual Environment Activation Fails

**Error**: `source: venv/bin/activate: No such file`

**Solution**:
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Windows Issues

#### Issue: Execution Policy Error

**Error**: `cannot be loaded because running scripts is disabled`

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Issue: Python Not in PATH

**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Reinstall Python with "Add to PATH" checked
2. Or add Python manually to PATH environment variable

#### Issue: Virtual Environment Activation Fails

**Error**: `cannot be loaded because running scripts is disabled`

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Issue: YARA Installation Fails

**Error**: `yara-python installation failed`

**Solution**:
```powershell
pip install yara-python --no-binary yara-python
```

### General Issues

#### Issue: Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'click'`

**Solution**:
```bash
# Linux
source venv/bin/activate
pip install -r requirements.txt

# Windows
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Issue: Disk Space

**Error**: `No space left on device`

**Solution**:
```bash
# Check disk space
df -h

# Clean package cache (Linux)
sudo apt clean

# Clean temporary files
hex-avg clean
```

#### Issue: Performance Issues

**Symptoms**: Slow scanning, high memory usage

**Solutions**:
```bash
# Reduce thread count
hex-avg scan --threads 4 /path

# Enable quick scan
hex-avg scan --quick /path

# Check system resources
htop  # Linux
Task Manager  # Windows
```

---

## Uninstallation

### Linux Uninstallation

```bash
# Remove system-wide command
sudo rm /usr/local/bin/hex-avg

# Remove installation directory
sudo rm -rf ~/hex-avg

# Remove virtual environment
rm -rf ~/hex-avg/venv
```

### Windows Uninstallation

```powershell
# Remove installation directory
Remove-Item -Recurse -Force "C:\hex-avg"

# Remove from PATH (manually through System Properties)
# Remove desktop shortcut
Remove-Item "$env:USERPROFILE\Desktop\HEX-AVG.lnk" -Force
```

---

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the logs**: `hex-avg logs --tail`
2. **Run diagnostics**: `hex-avg setup check`
3. **Visit GitHub Issues**: [github.com/yourusername/hex-avg/issues](https://github.com/yourusername/hex-avg/issues)
4. **Documentation**: See [USAGE.md](USAGE.md) for usage instructions

---

## Next Steps

After successful installation:

1. Read the [USAGE.md](USAGE.md) guide
2. Run your first scan: `hex-avg scan /path`
3. Update signatures: `hex-avg update`
4. Test with EICAR: `hex-avg benchmark --test-eicar`

---

**Last Updated**: 2024-01-01  
**Version**: 1.0.0