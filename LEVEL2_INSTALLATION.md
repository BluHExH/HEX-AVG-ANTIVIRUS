# HEX-AVG LEVEL-2 Installation Guide
## Background Security Protector

Complete installation instructions for HEX-AVG LEVEL-2 with background protection.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [New Dependencies](#new-dependencies)
3. [Installation on Windows](#installation-on-windows)
4. [Installation on Kali Linux](#installation-on-kali-linux)
5. [Service Setup](#service-setup)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

- **Operating System**:
  - Kali Linux 2023+ or similar Debian-based distributions
  - Windows 10/11 (64-bit)
  
- **Python**: 3.11 or higher
  
- **RAM**: 2GB minimum (4GB recommended)
  
- **Disk Space**: 1GB for installation, additional space for logs and quarantine

### New Requirements for LEVEL-2

- **Background Service**: Ability to run background services
- **File Monitoring**: File system monitoring capabilities
- **Scheduling**: Task scheduling support
- **PowerShell 5.1+** (Windows)

---

## New Dependencies

### Additional Python Packages (LEVEL-2)

```bash
# File system monitoring
pip install watchdog

# Task scheduling
pip install schedule

# Windows-specific (Windows only)
pip install pywin32 pywin32system

# Linux-specific (Linux only)
pip install pyinotify
```

### Update requirements.txt

Add these to your `requirements.txt`:

```txt
# Existing LEVEL-1 dependencies
click>=8.1.0
rich>=13.0.0
tqdm>=4.65.0
psutil>=5.9.0
tabulate>=0.9.0
yara-python>=4.3.0
pefile>=2023.2.7
pyelftools>=0.29
sqlite3
cryptography>=40.0.0
hashlib
python-dateutil>=2.8.0
pyyaml>=6.0
colorama>=0.4.6
chardet>=5.0.0

# LEVEL-2 dependencies
watchdog>=3.0.0          # File system monitoring
schedule>=1.2.0          # Task scheduling
pywin32>=306            # Windows service support (Windows only)
pyinotify>=0.9.6        # Linux file monitoring (Linux only)
```

---

## Installation on Windows

### Method 1: Automated Installation (Recommended)

1. **Download HEX-AVG LEVEL-2**:
   - Download the ZIP file from GitHub
   - Extract to `C:\hex-avg`

2. **Run PowerShell as Administrator**:
   - Right-click on PowerShell
   - Select "Run as Administrator"

3. **Navigate to installation directory**:
   ```powershell
   cd C:\hex-avg
   ```

4. **Run the LEVEL-2 installation script**:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\scripts\install_level2_windows.ps1
   ```

5. **Install dependencies**:
   ```powershell
   cd C:\hex-avg
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. **Initialize LEVEL-2**:
   ```powershell
   python hex_avg_level2.py setup init
   ```

### Method 2: Manual Installation

#### Step 1: Install Python

Download Python 3.11+ from [python.org](https://www.python.org/downloads/) and install with:
- ✅ Add Python to PATH
- ✅ Install for all users

#### Step 2: Create Installation Directory

```powershell
New-Item -ItemType Directory -Path "C:\hex-avg" -Force
cd C:\hex-avg
```

#### Step 3: Download HEX-AVG LEVEL-2

Extract the HEX-AVG LEVEL-2 source code to `C:\hex-avg`

#### Step 4: Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

*Note: If you see an error about execution policy:*
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Step 5: Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 6: Initialize Configuration

```powershell
python hex_avg_level2.py setup init
```

#### Step 7: Add to PATH (Optional)

1. Search for "Environment Variables"
2. Click "Edit the system environment variables"
3. Click "Environment Variables"
4. Under "User variables", find "Path" and click "Edit"
5. Click "New" and add: `C:\hex-avg`

---

## Installation on Kali Linux

### Method 1: Automated Installation (Recommended)

1. **Download HEX-AVG LEVEL-2**:
   ```bash
   cd ~/Downloads
   git clone https://github.com/yourusername/hex-avg.git
   cd hex-avg
   ```

2. **Run the installation script**:
   ```bash
   chmod +x scripts/install_level2_linux.sh
   sudo ./scripts/install_level2_linux.sh
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

#### Step 2: Install Python and Tools

```bash
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y yara inotify-tools
```

#### Step 3: Create Installation Directory

```bash
mkdir -p ~/hex-avg
cd ~/hex-avg
```

#### Step 4: Download HEX-AVG LEVEL-2

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

#### Step 6: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 7: Initialize Configuration

```bash
python hex_avg_level2.py setup init
```

#### Step 8: Create Systemd Service

```bash
# Create systemd service file
sudo nano /etc/systemd/user/hex-avg.service
```

Add the following content:

```ini
[Unit]
Description=HEX-AVG Background Protector
After=network.target

[Service]
Type=simple
ExecStart=/home/yourusername/hex-avg/venv/bin/python /home/yourusername/hex-avg/hex_avg_level2.py start
ExecStop=/home/yourusername/hex-avg/venv/bin/python /home/yourusername/hex-avg/hex_avg_level2.py stop
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

Save and exit (Ctrl+X, Y, Enter).

#### Step 9: Enable Service

```bash
# Enable user service
systemctl --user enable hex-avg.service

# Start service
systemctl --user start hex-avg.service

# Check status
systemctl --user status hex-avg.service
```

---

## Service Setup

### Windows Service Setup

#### Option 1: PowerShell Background Task

Create a scheduled task to run on startup:

```powershell
# Create task action
$action = New-ScheduledTaskAction -Execute "C:\hex-avg\venv\Scripts\python.exe" -Argument "C:\hex-avg\hex_avg_level2.py start"

# Create trigger (at startup)
$trigger = New-ScheduledTaskTrigger -AtStartup

# Create principal (run as user)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# Register scheduled task
Register-ScheduledTask -TaskName "HEX-AVG Background Protector" -Action $action -Trigger $trigger -Principal $principal -Description "HEX-AVG Real-time Protection"
```

#### Option 2: Windows Service (Advanced)

Use NSSM (Non-Sucking Service Manager):

1. Download NSSM from https://nssm.cc/download
2. Install NSSM
3. Create service:

```cmd
nssm install HEXAVG "C:\hex-avg\venv\Scripts\python.exe"
nssm set HEXAVG AppParameters "C:\hex-avg\hex_avg_level2.py start"
nssm set HEXAVG AppDirectory "C:\hex-avg"
nssm set HEXAVG DisplayName "HEX-AVG Background Protector"
nssm set HEXAVG Description "HEX-AVG Real-time Protection Service"
nssm start HEXAVG
```

### Linux Systemd Service

The service file was created in Step 8 of the Linux installation.

#### Enable Auto-Start

```bash
# Enable service to start on user login
systemctl --user enable hex-avg.service

# Check if enabled
systemctl --user is-enabled hex-avg.service
```

#### Manual Service Control

```bash
# Start service
systemctl --user start hex-avg.service

# Stop service
systemctl --user stop hex-avg.service

# Restart service
systemctl --user restart hex-avg.service

# Check status
systemctl --user status hex-avg.service

# View logs
journalctl --user -u hex-avg.service -f
```

---

## Verification

### Windows Verification

```powershell
# Check version
python hex_avg_level2.py --version

# Check background service status
python hex_avg_level2.py status

# Test file monitoring
# Create a test file in Downloads folder
echo "X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*" > "$env:USERPROFILE\Downloads\eicar.txt"

# Check if file was scanned
python hex_avg_level2.py logs --type alerts --tail 5
```

Expected output:
```
HEX-AVG LEVEL-2 v2.0.0
Status: Running
Uptime: 60 seconds
```

### Linux Verification

```bash
# Check version
python hex_avg_level2.py --version

# Check daemon status
python hex_avg_level2.py status

# Check systemd service
systemctl --user status hex-avg.service

# Test file monitoring
# Create a test file in Downloads
echo "X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*" > ~/Downloads/eicar.txt

# Check if file was scanned
python hex_avg_level2.py logs --type alerts --tail 5
```

Expected output:
```
HEX-AVG LEVEL-2 v2.0.0
Status: Running
Uptime: 60 seconds
```

---

## Troubleshooting

### Windows Issues

#### Issue: Service won't start

**Solution**:
```powershell
# Check if Python is in PATH
python --version

# Check dependencies
pip list | Select-String watchdog

# Run in console mode for debugging
cd C:\hex-avg
.\venv\Scripts\Activate.ps1
python src/services/windows_service.py
```

#### Issue: File monitoring not working

**Solution**:
```powershell
# Check if watchdog is installed
pip list | Select-String watchdog

# Reinstall watchdog
pip install --upgrade watchdog

# Check Windows Event Viewer for errors
eventvwr.msc
```

#### Issue: Scheduled scans not running

**Solution**:
```powershell
# Check scheduled task
Get-ScheduledTask -TaskName "HEX-AVG Background Protector"

# View task history
Get-ScheduledTaskInfo -TaskName "HEX-AVG Background Protector"

# Run task manually
Start-ScheduledTask -TaskName "HEX-AVG Background Protector"
```

### Linux Issues

#### Issue: systemd service won't start

**Solution**:
```bash
# Check service status
systemctl --user status hex-avg.service

# View logs
journalctl --user -u hex-avg.service -n 50

# Check if paths are correct
cat ~/.config/systemd/user/hex-avg.service

# Reload systemd daemon
systemctl --user daemon-reload
```

#### Issue: inotify monitoring not working

**Solution**:
```bash
# Check inotify limits
cat /proc/sys/fs/inotify/max_user_watches

# Increase inotify limits (temporary)
echo 8192 | sudo tee /proc/sys/fs/inotify/max_user_watches

# Increase inotify limits (permanent)
echo "fs.inotify.max_user_watches=8192" | sudo tee -a /etc/sysctl.conf
```

#### Issue: Permission denied

**Solution**:
```bash
# Check file permissions
ls -la ~/hex-avg

# Fix permissions
chmod +x hex_avg_level2.py
chmod -R 755 ~/hex-avg/
```

### General Issues

#### Issue: High CPU usage

**Solution**:
```bash
# Reduce thread count
python hex_avg_level2.py configure --threads 2

# Enable low-resource mode
python hex_avg_level2.py configure --low-resource true
```

#### Issue: Logs not being created

**Solution**:
```bash
# Check logs directory
ls -la ~/hex-avg/logs

# Create logs directory
mkdir -p ~/hex-avg/logs

# Check permissions
chmod 755 ~/hex-avg/logs
```

---

## Uninstallation

### Windows Uninstallation

```powershell
# Stop background service
python hex_avg_level2.py stop

# Remove scheduled task
Unregister-ScheduledTask -TaskName "HEX-AVG Background Protector" -Confirm:$false

# Remove installation directory
Remove-Item -Recurse -Force "C:\hex-avg"

# Remove from PATH (manually through System Properties)
```

### Linux Uninstallation

```bash
# Stop and disable service
systemctl --user stop hex-avg.service
systemctl --user disable hex-avg.service

# Remove service file
rm ~/.config/systemd/user/hex-avg.service

# Reload systemd
systemctl --user daemon-reload

# Remove installation directory
rm -rf ~/hex-avg
```

---

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the logs**: `python hex_avg_level2.py logs --tail 100`
2. **Run diagnostics**: `python hex_avg_level2.py setup check`
3. **Visit GitHub Issues**: [github.com/yourusername/hex-avg/issues](https://github.com/yourusername/hex-avg/issues)
4. **Documentation**: See [LEVEL2_ARCHITECTURE.md](LEVEL2_ARCHITECTURE.md)

---

## Next Steps

After successful installation:

1. Read [LEVEL2_ARCHITECTURE.md](LEVEL2_ARCHITECTURE.md) for architecture details
2. Read [LEVEL2_SECURITY.md](LEVEL2_SECURITY.md) for security explanation
3. Start background protection: `python hex_avg_level2.py start`
4. Configure scheduled scans: `python hex_avg_level2.py schedule set`
5. Monitor alerts: `python hex_avg_level2.py alerts`

---

**Last Updated**: 2024-01-01  
**Version**: 2.0.0 (LEVEL-2)