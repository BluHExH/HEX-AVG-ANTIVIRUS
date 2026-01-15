#!/bin/bash

# HEX-AVG Antivirus - Linux Installation Script
# For Kali Linux and other Debian-based systems

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║          HEX-AVG Antivirus - Linux Installation              ║"
║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect operating system"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Update system
echo "Step 1: Updating system..."
apt update && apt upgrade -y
echo "✓ System updated"
echo ""

# Install Python and development tools
echo "Step 2: Installing Python and development tools..."
apt install -y python3 python3-pip python3-venv python3-dev
echo "✓ Python installed"
echo ""

# Install security analysis tools
echo "Step 3: Installing security analysis tools..."
apt install -y yara clamav binutils gdb
echo "✓ Security tools installed"
echo ""

# Create installation directory
INSTALL_DIR="/opt/hex-avg"
echo "Step 4: Creating installation directory at $INSTALL_DIR..."
mkdir -p $INSTALL_DIR
echo "✓ Installation directory created"
echo ""

# Copy files (assuming script is run from project root)
if [ -f "hex_avg.py" ]; then
    echo "Step 5: Copying HEX-AVG files..."
    cp -r . $INSTALL_DIR/
    echo "✓ Files copied"
else
    echo "Error: hex_avg.py not found. Please run this script from the project root."
    exit 1
fi

# Create virtual environment
echo "Step 6: Creating Python virtual environment..."
cd $INSTALL_DIR
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Install dependencies
echo "Step 7: Installing Python dependencies..."
$INSTALL_DIR/venv/bin/pip install --upgrade pip
$INSTALL_DIR/venv/bin/pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Initialize HEX-AVG
echo "Step 8: Initializing HEX-AVG..."
$INSTALL_DIR/venv/bin/python hex_avg.py setup init
echo "✓ HEX-AVG initialized"
echo ""

# Create symlink for system-wide access
echo "Step 9: Creating system-wide command..."
ln -sf $INSTALL_DIR/hex_avg.py /usr/local/bin/hex-avg
chmod +x /usr/local/bin/hex-avg
echo "✓ Command 'hex-avg' available system-wide"
echo ""

# Create desktop entry (optional)
if command -v gnome-terminal &> /dev/null || command -v xfce4-terminal &> /dev/null; then
    echo "Step 10: Creating desktop entry..."
    cat > /usr/share/applications/hex-avg.desktop <<EOF
[Desktop Entry]
Name=HEX-AVG Antivirus
Comment=Professional Cross-Platform Antivirus
Exec=/usr/local/bin/hex-avg
Icon=security-high
Terminal=true
Type=Application
Categories=System;Security;Antivirus;
EOF
    echo "✓ Desktop entry created"
    echo ""
fi

# Setup complete
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  Installation Complete!                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "To use HEX-AVG, run:"
echo "  hex-avg --help"
echo "  hex-avg scan <path>"
echo "  hex-avg setup check"
echo ""
echo "Installation directory: $INSTALL_DIR"
echo "Log files: $INSTALL_DIR/logs"
echo "Quarantine: $INSTALL_DIR/quarantine"
echo ""
echo "Thank you for using HEX-AVG!"