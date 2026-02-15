#!/bin/bash
# Automatically install Thunar custom action for SEND-TO

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Installing Thunar Custom Action${NC}"
echo "================================="
echo

THUNAR_DIR="$HOME/.config/Thunar"
UCA_FILE="$THUNAR_DIR/uca.xml"
SCRIPT_PATH="$HOME/.local/bin/sendto-dialog"

# Check if script is installed
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}Error: sendto-dialog not found at $SCRIPT_PATH${NC}"
    echo "Run ./install-thunar.sh first"
    exit 1
fi

# Create Thunar config directory if it doesn't exist
mkdir -p "$THUNAR_DIR"

# Create or update uca.xml
if [ ! -f "$UCA_FILE" ]; then
    # Create new uca.xml
    cat > "$UCA_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<actions>
<action>
	<icon>gtk-save-as</icon>
	<name>SEND-TO</name>
	<submenu></submenu>
	<unique-id>1739560000000000-1</unique-id>
	<command>sendto-dialog %F</command>
	<description>Move files to bookmarked locations</description>
	<range></range>
	<patterns>*</patterns>
	<startup-notify/>
	<directories/>
	<audio-files/>
	<image-files/>
	<other-files/>
	<text-files/>
	<video-files/>
</action>
</actions>
EOF
    echo -e "${GREEN}✓ Created new Thunar custom actions file${NC}"
else
    # Check if SEND-TO action already exists
    if grep -q "<name>SEND-TO</name>" "$UCA_FILE"; then
        echo -e "${YELLOW}SEND-TO action already exists in uca.xml${NC}"
        read -p "Replace it? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Remove old SEND-TO action
            python3 << 'PYEOF'
import sys
import xml.etree.ElementTree as ET

uca_file = sys.argv[1]
tree = ET.parse(uca_file)
root = tree.getroot()

# Remove existing SEND-TO actions
for action in root.findall('action'):
    name = action.find('name')
    if name is not None and name.text == 'SEND-TO':
        root.remove(action)

# Save
tree.write(uca_file, encoding='UTF-8', xml_declaration=True)
PYEOF
            python3 -c "import sys; sys.argv = ['', '$UCA_FILE']" << 'PYEOF'
import sys
import xml.etree.ElementTree as ET

uca_file = sys.argv[1]
tree = ET.parse(uca_file)
root = tree.getroot()

# Remove existing SEND-TO actions
for action in root.findall('action'):
    name = action.find('name')
    if name is not None and name.text == 'SEND-TO':
        root.remove(action)

# Save
tree.write(uca_file, encoding='UTF-8', xml_declaration=True)
PYEOF
        else
            exit 0
        fi
    fi

    # Add new action to existing file
    python3 << PYEOF
import sys
import xml.etree.ElementTree as ET

uca_file = "$UCA_FILE"
script_path = "$SCRIPT_PATH"

# Parse existing file
try:
    tree = ET.parse(uca_file)
    root = tree.getroot()
except:
    # Create new root if parse fails
    root = ET.Element('actions')
    tree = ET.ElementTree(root)

# Create new action
action = ET.SubElement(root, 'action')
ET.SubElement(action, 'icon').text = 'gtk-save-as'
ET.SubElement(action, 'name').text = 'SEND-TO'
ET.SubElement(action, 'submenu').text = ''
ET.SubElement(action, 'unique-id').text = '1739560000000000-1'
ET.SubElement(action, 'command').text = 'sendto-dialog %F'
ET.SubElement(action, 'description').text = 'Move files to bookmarked locations'
ET.SubElement(action, 'range').text = ''
ET.SubElement(action, 'patterns').text = '*'
ET.SubElement(action, 'startup-notify')
ET.SubElement(action, 'directories')
ET.SubElement(action, 'audio-files')
ET.SubElement(action, 'image-files')
ET.SubElement(action, 'other-files')
ET.SubElement(action, 'text-files')
ET.SubElement(action, 'video-files')

# Save
tree.write(uca_file, encoding='UTF-8', xml_declaration=True)
print("✓ Added SEND-TO action to Thunar")
PYEOF
fi

echo
echo -e "${GREEN}Installation complete!${NC}"
echo
echo "The SEND-TO action has been added to Thunar."
echo
echo "To use it:"
echo "  1. Open Thunar"
echo "  2. Right-click on any file(s) or folder(s)"
echo "  3. Select 'SEND-TO' from the context menu"
echo "  4. Choose destination from your bookmarks"
echo
echo "If you don't see it, try restarting Thunar:"
echo "  killall thunar && thunar &"
echo
