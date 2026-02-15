#!/bin/bash
# Installation script for Thunar SEND-TO Python extension

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Installing Thunar SEND-TO Extension (Python)${NC}"
echo "==============================================="
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Error: Do not run this script as root/sudo${NC}"
    echo "The extension should be installed in your user directory."
    exit 1
fi

# Check for required packages
echo "Checking dependencies..."
MISSING_PACKAGES=()

if ! dpkg -l | grep -q thunarx-python; then
    MISSING_PACKAGES+=("thunarx-python")
fi

if ! dpkg -l | grep -q python3-gi; then
    MISSING_PACKAGES+=("python3-gi")
fi

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}Warning: Missing required packages:${NC}"
    for pkg in "${MISSING_PACKAGES[@]}"; do
        echo "  - $pkg"
    done
    echo
    echo "Install them with:"
    echo -e "${GREEN}sudo apt install thunarx-python python3-gi${NC}"
    echo
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create extension directory if it doesn't exist
EXTENSION_DIR="$HOME/.local/share/thunarx-python/extensions"
echo "Creating extension directory: $EXTENSION_DIR"
mkdir -p "$EXTENSION_DIR"

# Copy extension file
echo "Copying extension file..."
cp sendto_thunar_extension.py "$EXTENSION_DIR/"
chmod +x "$EXTENSION_DIR/sendto_thunar_extension.py"

echo -e "${GREEN}✓ Extension installed successfully${NC}"
echo

# Restart Thunar
echo "Restarting Thunar..."
if pgrep -x "thunar" > /dev/null; then
    killall thunar 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✓ Thunar restarted${NC}"
else
    echo -e "${YELLOW}Thunar is not running${NC}"
fi

echo
echo -e "${GREEN}Installation complete!${NC}"
echo
echo "To use the extension:"
echo "  1. Open Thunar file manager"
echo "  2. Right-click on any file or folder"
echo "  3. Look for the 'SEND-TO' option with cascading submenus"
echo
echo "Note: Make sure you have bookmarks in Thunar (press Ctrl+D to bookmark a folder)"
echo
echo "If the menu doesn't appear, try:"
echo "  - Closing all Thunar windows and reopening"
echo "  - Running: killall thunar && thunar &"
echo "  - Checking for errors: THUNARX_PYTHON_DEBUG=all thunar 2>&1 | grep -i send"
echo "  - Verifying the extension is in: $EXTENSION_DIR"
echo
