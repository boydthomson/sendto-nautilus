# Nautilus SEND-TO Extension

A Nautilus (GNOME Files) extension that adds a powerful "SEND-TO" context menu option for quickly moving files and folders to your bookmarked locations with full subdirectory navigation.

## Features

- 📁 **Move files/folders** via right-click context menu
- 🔖 **Uses Nautilus bookmarks** as destinations
- 🌳 **Full directory tree traversal** - navigate through all subdirectories
- 👁️ **Shows hidden folders** (those starting with `.`)
- ⚠️ **Smart conflict handling** - Nautilus prompts you for duplicate files (Skip/Replace/Rename)
- 🔒 **Safe recursion limit** - prevents excessive menu depth (max 5 levels)

## Screenshots

```
Right-click menu:
  ├── Cut
  ├── Copy
  ├── Paste
  ├── SEND-TO ►
  │   ├── Documents/ ►
  │   │   ├── → (move here)
  │   │   ├── ────────────
  │   │   ├── projects/ ►
  │   │   │   ├── → (move here)
  │   │   │   ├── ────────────
  │   │   │   └── work/ ►
  │   │   └── .config/ ►
  │   └── Music/ ►
  │       └── → (move here)
  └── ...
```

## Installation

### Prerequisites

**Ubuntu/Debian:**
```bash
sudo apt install python3-nautilus python3-gi gir1.2-nautilus-4.0
```

**For older Nautilus 3.x:**
```bash
sudo apt install python3-nautilus python3-gi gir1.2-nautilus-3.0
```

**Fedora/RHEL:**
```bash
sudo dnf install nautilus-python python3-gobject
```

### Install Extension

1. Clone or download this repository:
```bash
cd /home/boyd/code/sendto-nautilus
```

2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

3. The script will:
   - Check for required dependencies
   - Copy the extension to `~/.local/share/nautilus-python/extensions/`
   - Restart Nautilus automatically

### Manual Installation

If you prefer manual installation:

1. Create the extension directory:
```bash
mkdir -p ~/.local/share/nautilus-python/extensions
```

2. Copy the extension file:
```bash
cp sendto_extension.py ~/.local/share/nautilus-python/extensions/
```

3. Restart Nautilus:
```bash
nautilus -q
```

## Usage

### Setting Up Bookmarks

Before using the extension, add some bookmarks in Nautilus:

1. Navigate to a folder you want to bookmark
2. Press `Ctrl+D` or use Bookmarks → Add Bookmark
3. Your bookmarks appear in the sidebar

### Moving Files

1. Right-click on any file or folder in Nautilus
2. Select **SEND-TO** from the context menu
3. Navigate through your bookmarked locations and subdirectories
4. Click **→ (move here)** on the desired destination folder
5. If a file with the same name exists, Nautilus will ask you to Skip/Replace/Rename

### Tips

- **Multiple files**: Select multiple files/folders and move them all at once
- **Hidden folders**: Folders starting with `.` are included in the menus
- **Deep nesting**: The extension traverses up to 5 levels deep to prevent overwhelming menus
- **Permissions**: If you can't access a folder, it won't appear in the menu

## Uninstallation

Run the uninstall script:
```bash
chmod +x uninstall.sh
./uninstall.sh
```

Or manually remove the extension:
```bash
rm ~/.local/share/nautilus-python/extensions/sendto_extension.py
nautilus -q
```

## Troubleshooting

### The SEND-TO menu doesn't appear

1. **Check dependencies are installed:**
```bash
dpkg -l | grep -E 'python3-nautilus|python3-gi|gir1.2-nautilus'
```

2. **Verify extension is installed:**
```bash
ls -la ~/.local/share/nautilus-python/extensions/sendto_extension.py
```

3. **Restart Nautilus completely:**
```bash
nautilus -q
killall nautilus
nautilus &
```

4. **Check for errors:**
```bash
# Run Nautilus from terminal to see error messages
nautilus --no-desktop 2>&1 | grep -i send
```

### Menu shows "(No bookmarks found)"

- Add bookmarks in Nautilus using `Ctrl+D`
- Check if `~/.config/gtk-3.0/bookmarks` exists and has entries
- Only `file://` URIs are supported (local folders only, not remote SFTP/SSH)

### Some folders don't appear in the menu

This can happen if:
- You don't have permission to read the folder
- The folder is more than 5 levels deep (recursion limit)
- The folder path contains special characters that can't be parsed

### Files aren't moving

- Check you have write permissions on the destination folder
- Check the source files aren't in use by another program
- Look for error messages in the terminal output

### Extension not loading after update

1. Remove cached Python bytecode:
```bash
rm -rf ~/.local/share/nautilus-python/extensions/__pycache__
```

2. Restart Nautilus:
```bash
nautilus -q
```

## Technical Details

### Architecture

- **Language**: Python 3
- **APIs**: GObject, Nautilus (FileInfo, MenuProvider), Gio (File operations)
- **Bookmark format**: GTK 3.0 bookmarks (`~/.config/gtk-3.0/bookmarks`)

### File Operations

The extension uses `Gio.File.move()` with no flags, which:
- Moves files (doesn't copy)
- Lets Nautilus handle conflict resolution
- Maintains file metadata and permissions

### Safety Features

- **Recursion limit**: Maximum 5 directory levels to prevent excessive menus
- **Permission handling**: Gracefully skips inaccessible directories
- **Error handling**: Catches and logs errors without crashing Nautilus
- **URL decoding**: Properly handles special characters in paths (`%20`, etc.)

### Compatibility

- **Nautilus 3.x**: Compatible
- **Nautilus 4.x**: Compatible (GNOME 43+)
- **Desktop**: GNOME, Ubuntu, other GTK-based environments

## Development

### Project Structure

```
sendto-nautilus/
├── sendto_extension.py  # Main extension code
├── install.sh           # Installation script
├── uninstall.sh         # Uninstallation script
├── requirements.txt     # System dependencies
└── README.md           # This file
```

### Testing

1. Add test bookmarks in Nautilus
2. Test with single and multiple files
3. Test with files that have name conflicts
4. Test with deeply nested directories
5. Test with hidden folders
6. Test with special characters in filenames

### Contributing

Feel free to submit issues or pull requests for:
- Bug fixes
- Performance improvements
- New features
- Better error handling
- Documentation improvements

## Known Limitations

1. **Remote bookmarks**: Only local `file://` URIs are supported (no SFTP, SSH, etc.)
2. **Performance**: Very large directory trees may cause slight lag when building menus
3. **Depth limit**: Subdirectories beyond 5 levels deep won't appear in menus
4. **Symlink loops**: Prevented by depth limit, but could be improved with inode tracking

## License

This extension is provided as-is for personal and educational use.

## Credits

Created for efficient file management in Nautilus. Inspired by the need for quick file organization using existing bookmark infrastructure.

## Changelog

### Version 1.0.0 (Initial Release)
- Basic SEND-TO context menu
- GTK bookmark integration
- Recursive directory traversal (max depth 5)
- Hidden folder support
- Move operation with conflict handling
- Installation/uninstallation scripts
