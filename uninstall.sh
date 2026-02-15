#!/bin/bash
# Uninstallation script for Nautilus SEND-TO extension

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Uninstalling Nautilus SEND-TO Extension${NC}"
echo "========================================="
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Error: Do not run this script as root/sudo${NC}"
    exit 1
fi

EXTENSION_DIR="$HOME/.local/share/nautilus-python/extensions"
EXTENSION_FILE="$EXTENSION_DIR/sendto_extension.py"

# Check if extension exists
if [ ! -f "$EXTENSION_FILE" ]; then
    echo -e "${YELLOW}Extension not found at: $EXTENSION_FILE${NC}"
    echo "It may already be uninstalled."
    exit 0
fi

# Remove extension file
echo "Removing extension file..."
rm -f "$EXTENSION_FILE"

# Also remove .pyc files if they exist
rm -f "$EXTENSION_DIR/sendto_extension.pyc"
rm -f "$EXTENSION_DIR/__pycache__/sendto_extension."*.pyc

echo -e "${GREEN}✓ Extension removed${NC}"
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
echo -e "${GREEN}Uninstallation complete!${NC}"
echo "The SEND-TO menu should no longer appear in Nautilus."
echo
