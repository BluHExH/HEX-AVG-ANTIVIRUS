#!/bin/bash
# Script to create AppImage for HEX-AVG

set -e

VERSION=$(python -c "import sys; sys.path.insert(0, '..'); from config import HEXAVGConfig; print(HEXAVGConfig.VERSION)")
APP_NAME="HEX-AVG"
BUILD_DIR="appimage_build"
OUTPUT_DIR="../dist"

echo "Creating AppImage for HEX-AVG v${VERSION}"

# Clean previous builds
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

# Download appimagetool if not present
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "Downloading appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# Create AppDir structure
mkdir -p "${BUILD_DIR}/AppDir"
mkdir -p "${BUILD_DIR}/AppDir/usr/bin"
mkdir -p "${BUILD_DIR}/AppDir/usr/share/applications"
mkdir -p "${BUILD_DIR}/AppDir/usr/share/icons/hicolor/256x256/apps"

# Copy built files
cp -r ../dist/hex-avg-linux/* "${BUILD_DIR}/AppDir/usr/bin/"
chmod +x "${BUILD_DIR}/AppDir/usr/bin/hex-avg"

# Create AppRun
cat > "${BUILD_DIR}/AppDir/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}

# Open terminal and run hex-avg
if [ -t 1 ]; then
    # Already in terminal
    exec "$HERE/usr/bin/hex-avg" "$@"
else
    # Not in terminal, open one
    if command -v x-terminal-emulator >/dev/null 2>&1; then
        exec x-terminal-emulator -e "$HERE/usr/bin/hex-avg" "$@"
    elif command -v gnome-terminal >/dev/null 2>&1; then
        exec gnome-terminal -- "$HERE/usr/bin/hex-avg" "$@"
    elif command -v xfce4-terminal >/dev/null 2>&1; then
        exec xfce4-terminal -e "$HERE/usr/bin/hex-avg" "$@"
    elif command -v konsole >/dev/null 2>&1; then
        exec konsole -e "$HERE/usr/bin/hex-avg" "$@"
    else
        exec "$HERE/usr/bin/hex-avg" "$@"
    fi
fi
EOF
chmod +x "${BUILD_DIR}/AppDir/AppRun"

# Create desktop file
cat > "${BUILD_DIR}/AppDir/usr/share/applications/hex-avg.desktop" << EOF
[Desktop Entry]
Name=HEX-AVG Antivirus
Comment=Professional Cross-Platform Antivirus
Exec=hex-avg
Icon=hex-avg
Terminal=true
Type=Application
Categories=Security;System;Antivirus;
Keywords=antivirus;security;scanner;virus;malware;
Version=${VERSION}
EOF

# Create a simple icon (SVG placeholder)
cat > "${BUILD_DIR}/AppDir/usr/share/icons/hicolor/256x256/apps/hex-avg.svg" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" rx="32" fill="#2E7D32"/>
  <text x="128" y="128" font-family="Arial, sans-serif" font-size="48" font-weight="bold" text-anchor="middle" dominant-baseline="middle" fill="white">HEX</text>
  <text x="128" y="170" font-family="Arial, sans-serif" font-size="32" font-weight="bold" text-anchor="middle" dominant-baseline="middle" fill="white">AVG</text>
  <circle cx="128" cy="128" r="110" stroke="white" stroke-width="4" fill="none"/>
  <path d="M 60 128 L 100 80 L 150 130 L 200 80" stroke="white" stroke-width="8" fill="none" opacity="0.5"/>
</svg>
EOF

# Create .desktop file in AppDir root
cp "${BUILD_DIR}/AppDir/usr/share/applications/hex-avg.desktop" "${BUILD_DIR}/AppDir/hex-avg.desktop"

# Create AppRun symlink in usr/bin
ln -sf ../../AppRun "${BUILD_DIR}/AppDir/usr/bin/hex-avg"

# Build AppImage
echo "Building AppImage..."
./appimagetool-x86_64.AppImage "${BUILD_DIR}/AppDir" "${OUTPUT_DIR}/HEX-AVG-${VERSION}-x86_64.AppImage" --no-appstream

echo "AppImage created: ${OUTPUT_DIR}/HEX-AVG-${VERSION}-x86_64.AppImage"

# Clean up
rm -rf "${BUILD_DIR}"

echo "Package size:"
ls -lh "${OUTPUT_DIR}/HEX-AVG-${VERSION}-x86_64.AppImage"