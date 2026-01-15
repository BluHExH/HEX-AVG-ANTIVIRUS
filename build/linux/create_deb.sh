#!/bin/bash
# Script to create Debian package for HEX-AVG

set -e

VERSION=$(python -c "import sys; sys.path.insert(0, '..'); from config import HEXAVGConfig; print(HEXAVGConfig.VERSION)")
PACKAGE_NAME="hex-avg"
ARCHITECTURE="amd64"
BUILD_DIR="deb_build"
OUTPUT_DIR="../dist"

echo "Creating Debian package for HEX-AVG v${VERSION}"

# Clean previous builds
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

# Create Debian directory structure
mkdir -p "${BUILD_DIR}/DEBIAN"
mkdir -p "${BUILD_DIR}/usr/bin"
mkdir -p "${BUILD_DIR}/usr/share/hex-avg"
mkdir -p "${BUILD_DIR}/usr/share/doc/hex-avg"
mkdir -p "${BUILD_DIR}/usr/share/man/man1"
mkdir -p "${BUILD_DIR}/etc/hex-avg"

# Copy built files
cp -r ../dist/hex-avg-linux/* "${BUILD_DIR}/usr/share/hex-avg/"
ln -sf "/usr/share/hex-avg/hex-avg" "${BUILD_DIR}/usr/bin/hex-avg"

# Copy documentation
cp ../README.md "${BUILD_DIR}/usr/share/doc/hex-avg/"
cp ../LICENSE "${BUILD_DIR}/usr/share/doc/hex-avg/copyright" 2>/dev/null || echo "MIT License" > "${BUILD_DIR}/usr/share/doc/hex-avg/copyright"

# Create control file
cat > "${BUILD_DIR}/DEBIAN/control" << EOF
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Architecture: ${ARCHITECTURE}
Maintainer: HEX-AVG Team <contact@hex-avg.org>
Installed-Size: $(du -sk ${BUILD_DIR} | cut -f1)
Depends: python3, python3-yara, python3-cryptography
Section: security
Priority: optional
Homepage: https://github.com/yourusername/hex-avg
Description: Professional Cross-Platform Antivirus
 HEX-AVG is a professional antivirus tool designed for cybersecurity
 education, malware analysis labs, and defensive security operations.
 .
 Features:
  - Multi-threaded file scanning
  - Signature-based detection
  - Heuristic analysis
  - YARA rule support
  - Cross-platform support (Linux/Windows)
  - CLI interface with Rich output
EOF

# Create post-installation script
cat > "${BUILD_DIR}/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

echo "HEX-AVG has been installed successfully!"
echo ""
echo "Quick start:"
echo "  hex-avg scan --quick"
echo "  hex-avg scan /path/to/scan"
echo ""
echo "For more information:"
echo "  hex-avg --help"
echo "  hex-avg scan --help"
echo ""
echo "Full documentation: /usr/share/doc/hex-avg/README.md"

# Create default directories if they don't exist
mkdir -p /var/lib/hex-avg/quarantine
mkdir -p /var/lib/hex-avg/logs
mkdir -p /var/lib/hex-avg/reports

chmod 755 /var/lib/hex-avg/quarantine
chmod 755 /var/lib/hex-avg/logs
chmod 755 /var/lib/hex-avg/reports

exit 0
EOF

chmod 755 "${BUILD_DIR}/DEBIAN/postinst"

# Create pre-removal script
cat > "${BUILD_DIR}/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e

echo "Removing HEX-AVG..."
exit 0
EOF

chmod 755 "${BUILD_DIR}/DEBIAN/prerm"

# Create conffiles
cat > "${BUILD_DIR}/DEBIAN/conffiles" << EOF
/etc/hex-avg/config.yml
EOF

# Create default config
cat > "${BUILD_DIR}/etc/hex-avg/config.yml" << 'EOF'
# HEX-AVG Configuration File
# This file can be customized for your needs

scan:
  default_threads: 8
  max_file_size: 524288000  # 500 MB

quarantine:
  enabled: true
  encryption: false

logging:
  level: INFO
  max_size: 10485760  # 10 MB
  backup_count: 5
EOF

# Build the package
dpkg-deb --build "${BUILD_DIR}" "${OUTPUT_DIR}/hex-avg_${VERSION}_${ARCHITECTURE}.deb"

echo "Debian package created: ${OUTPUT_DIR}/hex-avg_${VERSION}_${ARCHITECTURE}.deb"

# Clean up
rm -rf "${BUILD_DIR}"

echo "Package size:"
ls -lh "${OUTPUT_DIR}/hex-avg_${VERSION}_${ARCHITECTURE}.deb"