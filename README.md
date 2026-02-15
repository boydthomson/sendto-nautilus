# SEND-TO for File Managers

A powerful "SEND-TO" extension for **Nautilus** and **Thunar** file managers that lets you quickly move files and folders to your bookmarked locations with full subdirectory navigation.

## 🚀 Features

- 📁 **Move files/folders** via right-click context menu
- 🔖 **Uses GTK bookmarks** as destinations (shared between apps)
- 🌳 **Full directory tree traversal** - navigate through all subdirectories
- 👁️ **Shows hidden folders** (those starting with `.`)
- ⚠️ **Smart conflict handling** - prompts for duplicate files (Skip/Replace/Rename)
- 🔒 **Safe recursion limit** - prevents excessive menu depth (max 5 levels)
- 🖥️ **Dual support** - Works with both Nautilus (GNOME) and Thunar (XFCE)

## 📦 Supported File Managers

### Thunar (XFCE) - ✅ RECOMMENDED
**Status:** Fully working, uses GTK dialog

Thunar uses a custom action system that's more reliable and works on all Linux distributions.

### Nautilus (GNOME Files)
**Status:** Requires Python extension support

Works on stable systems. May have issues on bleeding-edge distributions with Python 3.14+ due to `python3-nautilus` compatibility.

## 🎯 Installation

### For Thunar (Recommended)

**Quick Install:**
```bash
cd sendto-nautilus
chmod +x install-thunar.sh install-thunar-action.sh
./install-thunar.sh
./install-thunar-action.sh
```

**Manual Install:**
1. Install dependencies:
   ```bash
   sudo apt install python3-gi gir1.2-gtk-3.0
   ```

2. Install the script:
   ```bash
   mkdir -p ~/.local/bin
   cp sendto-dialog.py ~/.local/bin/sendto-dialog
   chmod +x ~/.local/bin/sendto-dialog
   ```

3. Add to Thunar:
   - Open Thunar
   - Go to: **Edit → Configure custom actions**
   - Click **+** to add new action
   - Fill in:
     - **Name:** SEND-TO
     - **Description:** Move files to bookmarked locations
     - **Command:** `sendto-dialog %F`
   - Go to **Appearance Conditions** tab
   - Check: **Directories** and **Other Files**
   - Click **OK**

### For Nautilus

**Prerequisites:**
```bash
sudo apt install python3-nautilus python3-gi gir1.2-nautilus-4.1
```

**Install:**
```bash
cd sendto-nautilus
chmod +x install.sh
./install.sh
```

**Note:** Nautilus extension may not work on development/rolling release distributions with Python 3.14+ due to `python3-nautilus` compatibility issues. Use the Thunar version instead.

## 🎨 Screenshots

### Thunar Dialog View
```
┌─────────────────────────────────┐
│ Send To                      [X]│
├─────────────────────────────────┤
│ Move 2 items to:                │
│                                 │
│ 📁 Documents                    │
│   📁 projects                   │
│     📁 work                     │
│     📁 personal                 │
│   📁 .config                    │
│ 📁 Music                        │
│ 📁 Pictures                     │
│                                 │
│ Destination: /home/user/Docs   │
│                                 │
│          [Cancel]  [Move Here]  │
└─────────────────────────────────┘
```

### Nautilus Context Menu
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
  │   │   │   └── → (move here)
  │   │   └── .config/ ►
  │   └── Music/ ►
  └── ...
```

## 💡 Usage

### Setting Up Bookmarks

Both Nautilus and Thunar use GTK bookmarks. Add bookmarks in either file manager:

**In Nautilus/Files:**
1. Navigate to a folder
2. Press `Ctrl+D` or use **Bookmarks → Add Bookmark**

**In Thunar:**
1. Navigate to a folder
2. Press `Ctrl+D` or drag folder to sidebar

**Manual editing:**
Edit `~/.config/gtk-3.0/bookmarks` directly:
```
file:///home/user/Documents Documents
file:///home/user/Music
file:///home/user/Projects Work Stuff
```

### Moving Files

**In Thunar:**
1. Select one or more files/folders
2. Right-click → **SEND-TO**
3. Dialog opens showing bookmarks and subdirectories
4. Select destination folder
5. Click **Move Here**

**In Nautilus:**
1. Select one or more files/folders
2. Right-click → **SEND-TO**
3. Navigate through submenu to destination
4. Click **→ (move here)**

### Command Line Usage

You can also use the dialog script from the command line:
```bash
sendto-dialog file1.txt file2.pdf /path/to/folder
```

## 🗂️ Project Structure

```
sendto-nautilus/
├── sendto_extension.py      # Nautilus Python extension
├── sendto-dialog.py          # GTK dialog script (for Thunar)
├── install.sh                # Nautilus installer
├── uninstall.sh              # Nautilus uninstaller
├── install-thunar.sh         # Thunar script installer
├── install-thunar-action.sh  # Thunar action auto-installer
├── requirements.txt          # System dependencies
└── README.md                 # This file
```

## 🔧 Troubleshooting

### Thunar Issues

**"SEND-TO doesn't appear in context menu"**
- Restart Thunar: `killall thunar && thunar &`
- Check custom actions: Edit → Configure custom actions
- Verify script is executable: `ls -la ~/.local/bin/sendto-dialog`

**"Dialog doesn't open"**
- Test from terminal: `sendto-dialog /tmp/testfile`
- Check dependencies: `python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk"`
- Install GTK3: `sudo apt install python3-gi gir1.2-gtk-3.0`

**"No bookmarks found"**
- Add bookmarks in Thunar or Nautilus (Ctrl+D)
- Check file exists: `cat ~/.config/gtk-3.0/bookmarks`

### Nautilus Issues

**"SEND-TO menu doesn't appear"**
1. Check extension is installed:
   ```bash
   ls -la ~/.local/share/nautilus-python/extensions/sendto_extension.py
   ```

2. Restart Nautilus completely:
   ```bash
   nautilus -q
   killall nautilus
   nautilus &
   ```

3. Check for errors:
   ```bash
   nautilus 2>&1 | grep -i python
   ```

**"pygobject initialization failed"**
- This is a known issue on development/bleeding-edge distributions with Python 3.14+
- **Solution:** Use the Thunar version instead, or wait for `python3-nautilus` package updates

### General Issues

**"Files aren't moving"**
- Check write permissions on destination folder
- Ensure source files aren't in use
- Check disk space

**"Some folders don't appear"**
- Permission issues - folders you can't read won't appear
- Depth limit - folders beyond 5 levels deep aren't shown
- Hidden system folders may be filtered

## 🛠️ Development

### Testing

**Test Thunar dialog:**
```bash
python3 sendto-dialog.py /tmp/testfile1 /tmp/testfile2
```

**Test Nautilus extension:**
```bash
python3 -c "import sendto_extension; print('OK')"
```

### Dependencies

**For Thunar:**
- Python 3.6+
- PyGObject (python3-gi)
- GTK 3.0 (gir1.2-gtk-3.0)

**For Nautilus:**
- Python 3.6+
- PyGObject (python3-gi)
- Nautilus Python (python3-nautilus)
- Nautilus 3.x or 4.x (gir1.2-nautilus-3.0 or gir1.2-nautilus-4.1)

## 🐛 Known Limitations

1. **Depth limit:** Subdirectories beyond 5 levels aren't shown (prevents performance issues)
2. **Remote bookmarks:** Only local `file://` URIs supported (no SFTP, SSH, etc.)
3. **Nautilus on Python 3.14+:** May not work on bleeding-edge distributions due to `python3-nautilus` compatibility
4. **Large directories:** Very large directory trees may cause slight lag when building menus

## 📝 License

This project is provided as-is for personal and educational use.

## 🙏 Credits

Created for efficient file management using GTK bookmark infrastructure. Works across GNOME, XFCE, and other GTK-based desktop environments.

## 📊 Compatibility

| File Manager | Status | Notes |
|-------------|--------|-------|
| Thunar      | ✅ Works | Recommended - uses custom actions |
| Nautilus 3.x | ✅ Works | On stable distributions |
| Nautilus 4.x | ⚠️ Limited | May fail on Python 3.14+ systems |
| Nemo        | ❓ Untested | May work with Nautilus extension |
| Caja        | ❓ Untested | May work with custom actions |

## 🔗 Links

- GitHub: https://github.com/boydthomson/sendto-nautilus
- Issues: https://github.com/boydthomson/sendto-nautilus/issues

## 📜 Changelog

### Version 1.1.0
- Added Thunar support with GTK dialog
- Created standalone dialog script
- Improved compatibility across distributions

### Version 1.0.0 (Initial Release)
- Nautilus Python extension
- GTK bookmark integration
- Recursive directory traversal (max depth 5)
- Hidden folder support
- Installation/uninstallation scripts
