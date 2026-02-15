#!/bin/bash
# Installation script for Thunar SEND-TO custom action

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Installing SEND-TO for Thunar${NC}"
echo "================================="
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Error: Do not run this script as root/sudo${NC}"
    exit 1
fi

# Check for Thunar
if ! command -v thunar &> /dev/null; then
    echo -e "${YELLOW}Warning: Thunar is not installed${NC}"
    echo "Install it with: sudo apt install thunar"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for Python3 and GTK
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check for required Python packages
echo "Checking Python dependencies..."
if ! python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk" 2>/dev/null; then
    echo -e "${YELLOW}Warning: python3-gi and GTK3 are required${NC}"
    echo "Install with: sudo apt install python3-gi gir1.2-gtk-3.0"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install the Python script
INSTALL_DIR="$HOME/.local/bin"
echo "Installing script to $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp sendto-dialog.py "$INSTALL_DIR/sendto-dialog"
chmod +x "$INSTALL_DIR/sendto-dialog"

echo -e "${GREEN}✓ Script installed${NC}"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${YELLOW}Note: $HOME/.local/bin is not in your PATH${NC}"
    echo "Add this to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo
echo -e "${GREEN}Installation complete!${NC}"
echo
echo "To add SEND-TO to Thunar:"
echo "  1. Open Thunar"
echo "  2. Go to: Edit → Configure custom actions"
echo "  3. Click the '+' button to add a new action"
echo "  4. Fill in:"
echo "     - Name: SEND-TO"
echo "     - Description: Move files to bookmarked locations"
echo "     - Command: $INSTALL_DIR/sendto-dialog %F"
echo "  5. Click 'Appearance Conditions' tab"
echo "  6. Select: 'Directories' and 'Other Files'"
echo "  7. Click OK"
echo
echo "Or use the automatic installation:"
echo "  ./install-thunar-action.sh"
echo
echo "You can also test the script from command line:"
echo "  sendto-dialog /path/to/file1 /path/to/file2"
echo
