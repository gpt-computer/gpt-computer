#!/bin/bash
# Debian package build script for gptc

set -e

PACKAGE_NAME="gptc"
VERSION="${GPTC_VERSION:-0.0.0-dev}"
ARCHITECTURE="${ARCH:-amd64}"
MAINTAINER="hlohaus"
DESCRIPTION="The official gpt-computer repository"
LONG_DESCRIPTION="Various collection of powerful language models"

# Clean up any previous builds
rm -rf debian/

# Create package directory structure
mkdir -p debian/${PACKAGE_NAME}/DEBIAN
mkdir -p debian/${PACKAGE_NAME}/usr/bin
mkdir -p debian/${PACKAGE_NAME}/usr/lib/python3/dist-packages
mkdir -p debian/${PACKAGE_NAME}/usr/share/doc/${PACKAGE_NAME}
mkdir -p debian/${PACKAGE_NAME}/usr/share/applications

# Create control file
cat > debian/${PACKAGE_NAME}/DEBIAN/control << EOF
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: python
Priority: optional
Architecture: ${ARCHITECTURE}
Essential: no
Maintainer: ${MAINTAINER}
Description: ${DESCRIPTION}
  ${LONG_DESCRIPTION}
Depends: python3 (>= 3.9), python3-pip, python3-aiohttp, python3-requests
Homepage: https://gptc.dev/community
EOF

# Create postinst script
cat > debian/${PACKAGE_NAME}/DEBIAN/postinst << 'EOF'
#!/bin/bash
set -e

# Install Python dependencies
pip3 install --break-system-packages aiohttp requests brotli pycryptodome nest-asyncio2

# Make gptc command available
if [ ! -L /usr/local/bin/gptc ]; then
    ln -s /usr/bin/gptc /usr/local/bin/gptc
fi

echo "gptc installed successfully"
echo "Usage: gptc --help"
EOF

# Create prerm script
cat > debian/${PACKAGE_NAME}/DEBIAN/prerm << 'EOF'
#!/bin/bash
set -e

# Remove symlink if it exists
if [ -L /usr/local/bin/gptc ]; then
    rm -f /usr/local/bin/gptc
fi
EOF

# Make scripts executable
chmod 755 debian/${PACKAGE_NAME}/DEBIAN/postinst
chmod 755 debian/${PACKAGE_NAME}/DEBIAN/prerm

# Install the package files using pip
export PYTHONPATH=""
pip install . --root=debian/${PACKAGE_NAME} --prefix=/usr --no-deps --no-build-isolation

# Fix Python path: pip installs to python3.X/site-packages, Debian expects python3/dist-packages
PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [ -d "debian/${PACKAGE_NAME}/usr/lib/python${PYTHON_VER}" ]; then
    rm -rf debian/${PACKAGE_NAME}/usr/lib/python3
    mkdir -p debian/${PACKAGE_NAME}/usr/lib/python3/dist-packages
    cp -r debian/${PACKAGE_NAME}/usr/lib/python${PYTHON_VER}/site-packages/* debian/${PACKAGE_NAME}/usr/lib/python3/dist-packages/
fi

# Create documentation
cp README.md debian/${PACKAGE_NAME}/usr/share/doc/${PACKAGE_NAME}/
cp LICENSE debian/${PACKAGE_NAME}/usr/share/doc/${PACKAGE_NAME}/copyright
gzip -9 debian/${PACKAGE_NAME}/usr/share/doc/${PACKAGE_NAME}/README.md

# Create desktop file
cat > debian/${PACKAGE_NAME}/usr/share/applications/${PACKAGE_NAME}.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=gptc
Comment=${DESCRIPTION}
Exec=/usr/bin/gptc
Icon=application-x-executable
Terminal=false
Categories=Development;Network;
EOF

# Fix permissions
find debian/${PACKAGE_NAME} -type d -exec chmod 755 {} \;
find debian/${PACKAGE_NAME} -type f -exec chmod 644 {} \;
chmod 755 debian/${PACKAGE_NAME}/usr/bin/gptc
chmod 755 debian/${PACKAGE_NAME}/DEBIAN/postinst
chmod 755 debian/${PACKAGE_NAME}/DEBIAN/prerm

# Calculate installed size
INSTALLED_SIZE=$(du -sk debian/${PACKAGE_NAME}/usr | cut -f1)

# Add installed size to control file
echo "Installed-Size: ${INSTALLED_SIZE}" >> debian/${PACKAGE_NAME}/DEBIAN/control

# Build the package
dpkg-deb --build debian/${PACKAGE_NAME} ${PACKAGE_NAME}-${VERSION}-${ARCHITECTURE}.deb

echo "Debian package created: ${PACKAGE_NAME}-${VERSION}-${ARCHITECTURE}.deb"