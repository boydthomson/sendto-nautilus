#!/bin/bash
# Installation script for Nautilus SEND-TO extension

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing Nautilus SEND-TO Extension${NC}"
echo "======================================="
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Error: Do not run this script as root/sudo${NC}"
    echo "The extension should be installed in your user directory."
    exit 1
fi

# Check for required system packages
echo "Checking system dependencies..."
MISSING_PACKAGES=()

if ! dpkg -l | grep -q python3-nautilus; then
    MISSING_PACKAGES+=("python3-nautilus")
fi

if ! dpkg -l | grep -q python3-gi; then
    MISSING_PACKAGES+=("python3-gi")
fi

# Check for Nautilus 4.x or 3.0
if ! dpkg -l | grep -q "gir1.2-nautilus-4"; then
    if ! dpkg -l | grep -q "gir1.2-nautilus-3.0"; then
        MISSING_PACKAGES+=("gir1.2-nautilus-4.1 (or gir1.2-nautilus-3.0)")
    fi
fi

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}Warning: Missing required packages:${NC}"
    for pkg in "${MISSING_PACKAGES[@]}"; do
        echo "  - $pkg"
    done
    echo
    echo "Install them with:"
    echo -e "${GREEN}sudo apt install python3-nautilus python3-gi gir1.2-nautilus-4.1${NC}"
    echo
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create extension directory if it doesn't exist
EXTENSION_DIR="$HOME/.local/share/nautilus-python/extensions"
echo "Creating extension directory: $EXTENSION_DIR"
mkdir -p "$EXTENSION_DIR"

# Copy extension file
echo "Copying extension file..."
cp sendto_extension.py "$EXTENSION_DIR/"
chmod +x "$EXTENSION_DIR/sendto_extension.py"

echo -e "${GREEN}✓ Extension installed successfully${NC}"
echo

# Restart Nautilus
echo "Restarting Nautilus..."
if pgrep -x "nautilus" > /dev/null; then
    nautilus -q 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✓ Nautilus restarted${NC}"
else
    echo -e "${YELLOW}Nautilus is not running${NC}"
fi

echo
echo -e "${GREEN}Installation complete!${NC}"
echo
echo "To use the extension:"
echo "  1. Open Nautilus file manager"
echo "  2. Right-click on any file or folder"
echo "  3. Look for the 'SEND-TO' option in the context menu"
echo
echo "Note: Make sure you have bookmarks in Nautilus (press Ctrl+D to bookmark a folder)"
echo
echo "If the menu doesn't appear, try:"
echo "  - Closing all Nautilus windows and reopening"
echo "  - Running: nautilus -q && nautilus &"
echo "  - Checking the extension is in: $EXTENSION_DIR"
echo
