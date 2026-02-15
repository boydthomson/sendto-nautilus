"""
Thunar SEND-TO Extension
Adds a context menu to move files/folders to bookmarked locations with full subdirectory traversal.
"""

import os
from pathlib import Path
from urllib.parse import unquote, urlparse
from gi.repository import GObject, Thunarx, Gio, GLib


class SendToMenuProvider(GObject.GObject, Thunarx.MenuProvider):
    """Provides SEND-TO context menu for Thunar."""

    MAX_DEPTH = 5  # Safety limit for directory recursion

    def __init__(self):
        super().__init__()

    def get_file_menu_items(self, window, files):
        """
        Called by Thunar when building context menu.

        Args:
            window: Thunar window
            files: List of selected Thunarx.FileInfo objects

        Returns:
            Tuple containing the SEND-TO menu item
        """
        if not files:
            return ()

        # Create top-level SEND-TO menu item
        top_item = Thunarx.MenuItem(
            name="SendToMenuProvider::SendTo",
            label="SEND-TO",
            tooltip="Move selected items to bookmarked locations"
        )

        # Create submenu for bookmarks
        submenu = Thunarx.Menu()
        top_item.set_menu(submenu)

        # Parse bookmarks and build menu
        bookmarks = self.parse_bookmarks()

        if not bookmarks:
            # No bookmarks available
            no_bookmarks_item = Thunarx.MenuItem(
                name="SendToMenuProvider::NoBookmarks",
                label="(No bookmarks found)",
                tooltip="Add bookmarks in Thunar to use this feature"
            )
            submenu.append_item(no_bookmarks_item)
            return (top_item,)

        # Add each bookmark with its subdirectories
        for bookmark in bookmarks:
            bookmark_path = Path(bookmark['path'])

            # Skip if bookmark path doesn't exist
            if not bookmark_path.exists() or not bookmark_path.is_dir():
                continue

            # Create menu item for the bookmark
            bookmark_label = bookmark['label'] or bookmark_path.name
            bookmark_item = Thunarx.MenuItem(
                name=f"SendToMenuProvider::Bookmark::{bookmark_path}",
                label=f"{bookmark_label}/",
                tooltip=f"Move to {bookmark_path}"
            )

            # Create submenu for this bookmark
            bookmark_submenu = Thunarx.Menu()
            bookmark_item.set_menu(bookmark_submenu)

            # Add "→ Move here" option for the bookmark root
            move_here_item = Thunarx.MenuItem(
                name=f"SendToMenuProvider::MoveHere::{bookmark_path}",
                label="→ (move here)",
                tooltip=f"Move to {bookmark_path}"
            )
            move_here_item.connect(
                'activate',
                self.on_move_files,
                window,
                files,
                str(bookmark_path)
            )
            bookmark_submenu.append_item(move_here_item)

            # Recursively build directory tree
            self.build_directory_menu(
                bookmark_submenu,
                bookmark_path,
                window,
                files,
                current_depth=0
            )

            submenu.append_item(bookmark_item)

        return (top_item,)

    def parse_bookmarks(self):
        """
        Parse GTK bookmarks file.

        Returns:
            List of dicts with keys: path, label, uri
        """
        bookmarks = []
        bookmarks_file = Path.home() / '.config' / 'gtk-3.0' / 'bookmarks'

        if not bookmarks_file.exists():
            return bookmarks

        try:
            with open(bookmarks_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # Split on first whitespace: URI [label]
                    parts = line.split(None, 1)
                    uri = parts[0]
                    label = parts[1] if len(parts) > 1 else None

                    # Only handle file:// URIs
                    if not uri.startswith('file://'):
                        continue

                    # Parse and decode URI
                    parsed = urlparse(uri)
                    path = unquote(parsed.path)

                    bookmarks.append({
                        'path': path,
                        'label': label,
                        'uri': uri
                    })

        except Exception as e:
            print(f"Error parsing bookmarks: {e}")
            return []

        return bookmarks

    def build_directory_menu(self, parent_menu, directory, window, files, current_depth=0):
        """
        Recursively build menu with subdirectories.

        Args:
            parent_menu: Thunarx.Menu to add items to
            directory: Path object of directory to traverse
            window: Thunar window
            files: List of selected files (for move callback)
            current_depth: Current recursion depth
        """
        # Stop at max depth to prevent excessive menus
        if current_depth >= self.MAX_DEPTH:
            return

        try:
            # Get all subdirectories (including hidden ones)
            subdirs = []
            for item in directory.iterdir():
                if item.is_dir():
                    subdirs.append(item)

            # Sort subdirectories by name
            subdirs.sort(key=lambda p: p.name.lower())

            # Add menu item for each subdirectory
            for subdir in subdirs:
                # Create menu item for this directory
                subdir_item = Thunarx.MenuItem(
                    name=f"SendToMenuProvider::Dir::{subdir}",
                    label=f"{subdir.name}/",
                    tooltip=f"Move to {subdir}"
                )

                # Create submenu
                subdir_submenu = Thunarx.Menu()
                subdir_item.set_menu(subdir_submenu)

                # Add "→ Move here" option
                move_here_item = Thunarx.MenuItem(
                    name=f"SendToMenuProvider::MoveHere::{subdir}",
                    label="→ (move here)",
                    tooltip=f"Move to {subdir}"
                )
                move_here_item.connect(
                    'activate',
                    self.on_move_files,
                    window,
                    files,
                    str(subdir)
                )
                subdir_submenu.append_item(move_here_item)

                # Check if this directory has subdirectories
                try:
                    has_subdirs = any(item.is_dir() for item in subdir.iterdir())

                    if has_subdirs:
                        # Recursively add subdirectories
                        self.build_directory_menu(
                            subdir_submenu,
                            subdir,
                            window,
                            files,
                            current_depth + 1
                        )

                except (PermissionError, OSError):
                    # Skip inaccessible directories
                    pass

                parent_menu.append_item(subdir_item)

        except (PermissionError, OSError) as e:
            # Skip directories we can't read
            print(f"Cannot read directory {directory}: {e}")

    def on_move_files(self, menu_item, window, files, destination_path):
        """
        Move selected files to destination.

        Args:
            menu_item: The menu item that was clicked
            window: Thunar window
            files: List of Thunarx.FileInfo objects to move
            destination_path: String path to destination directory
        """
        destination = Path(destination_path)

        for file_info in files:
            try:
                # Get source file URI and create Gio.File
                source_uri = file_info.get_uri()
                source = Gio.File.new_for_uri(source_uri)

                # Get filename
                source_path = Path(unquote(urlparse(source_uri).path))
                filename = source_path.name

                # Create destination Gio.File
                target_path = destination / filename
                target = Gio.File.new_for_path(str(target_path))

                # Move file - Thunar will handle conflict resolution
                # Using NONE flag means Thunar will prompt on conflicts
                source.move(
                    target,
                    Gio.FileCopyFlags.NONE,
                    None,  # No cancellable
                    None,  # No progress callback
                    None   # No user data
                )

                print(f"Moved {source_path} to {target_path}")

            except GLib.Error as e:
                print(f"Error moving {file_info.get_name()}: {e.message}")
            except Exception as e:
                print(f"Unexpected error moving {file_info.get_name()}: {e}")
