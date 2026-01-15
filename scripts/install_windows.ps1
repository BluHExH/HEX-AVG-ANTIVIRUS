# HEX-AVG Antivirus - Windows Installation Script
# For Windows 10/11 with PowerShell 5.1+

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                              ║" -ForegroundColor Cyan
Write-Host "║          HEX-AVG Antivirus - Windows Installation           ║" -ForegroundColor Cyan
Write-Host "║                                                              ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Error: This script requires Administrator privileges." -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Check PowerShell version
$psVersion = $PSVersionTable.PSVersion
Write-Host "PowerShell Version: $psVersion" -ForegroundColor Green
Write-Host ""

# Installation directory
$installDir = "C:\hex-avg"

# Step 1: Create installation directory
Write-Host "Step 1: Creating installation directory at $installDir..." -ForegroundColor Yellow
if (!(Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    Write-Host "✓ Installation directory created" -ForegroundColor Green
} else {
    Write-Host "✓ Installation directory already exists" -ForegroundColor Green
}
Write-Host ""

# Step 2: Check Python installation
Write-Host "Step 2: Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Step 3: Create virtual environment
Write-Host "Step 3: Creating Python virtual environment..." -ForegroundColor Yellow
Set-Location $installDir
python -m venv venv
Write-Host "✓ Virtual environment created" -ForegroundColor Green
Write-Host ""

# Step 4: Activate virtual environment
Write-Host "Step 4: Activating virtual environment..." -ForegroundColor Yellow
& $installDir\venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Step 5: Install dependencies
Write-Host "Step 5: Installing Python dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install --upgrade pip
    pip install -r requirements.txt
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ requirements.txt not found" -ForegroundColor Red
    Write-Host "Please run this script from the HEX-AVG project directory" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Step 6: Copy files (if not already in install directory)
$currentDir = Get-Location
if ($currentDir.Path -ne $installDir) {
    Write-Host "Step 6: Copying HEX-AVG files..." -ForegroundColor Yellow
    Copy-Item -Path ".\*" -Destination $installDir -Recurse -Force
    Write-Host "✓ Files copied" -ForegroundColor Green
    Write-Host ""
}

# Step 7: Initialize HEX-AVG
Write-Host "Step 7: Initializing HEX-AVG..." -ForegroundColor Yellow
python hex_avg.py setup init
Write-Host "✓ HEX-AVG initialized" -ForegroundColor Green
Write-Host ""

# Step 8: Add to PATH (optional)
Write-Host "Step 8: Adding HEX-AVG to system PATH..." -ForegroundColor Yellow
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$installDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$installDir", "User")
    Write-Host "✓ Added to PATH (may require terminal restart)" -ForegroundColor Green
} else {
    Write-Host "✓ Already in PATH" -ForegroundColor Green
}
Write-Host ""

# Step 9: Create shortcut (optional)
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = "$desktopPath\HEX-AVG.lnk"
Write-Host "Step 9: Creating desktop shortcut..." -ForegroundColor Yellow
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = "$installDir\hex_avg.py"
$Shortcut.Arguments = "--help"
$Shortcut.WorkingDirectory = $installDir
$Shortcut.Description = "HEX-AVG Antivirus"
$Shortcut.Save()
Write-Host "✓ Desktop shortcut created" -ForegroundColor Green
Write-Host ""

# Installation complete
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  Installation Complete!                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "To use HEX-AVG, run:" -ForegroundColor White
Write-Host "  cd $installDir" -ForegroundColor Gray
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "  python hex_avg.py --help" -ForegroundColor Gray
Write-Host ""
Write-Host "Or after restarting terminal:" -ForegroundColor White
Write-Host "  hex-avg --help" -ForegroundColor Gray
Write-Host ""
Write-Host "Common commands:" -ForegroundColor White
Write-Host "  hex-avg scan C:\Path\To\Scan" -ForegroundColor Gray
Write-Host "  hex-avg scan --full" -ForegroundColor Gray
Write-Host "  hex-avg setup check" -ForegroundColor Gray
Write-Host ""
Write-Host "Installation directory: $installDir" -ForegroundColor Gray
Write-Host "Log files: $installDir\logs" -ForegroundColor Gray
Write-Host "Quarantine: $installDir\quarantine" -ForegroundColor Gray
Write-Host ""
Write-Host "Thank you for using HEX-AVG!" -ForegroundColor Green