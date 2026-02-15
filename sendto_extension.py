"""
Nautilus SEND-TO Extension
Adds a context menu to move files/folders to bookmarked locations with full subdirectory traversal.
"""

import os
from pathlib import Path
from urllib.parse import unquote, urlparse
from gi.repository import GObject, Nautilus, Gio, GLib


class SendToMenuProvider(GObject.GObject, Nautilus.MenuProvider):
    """Provides SEND-TO context menu for Nautilus."""

    MAX_DEPTH = 5  # Safety limit for directory recursion

    def __init__(self):
        super().__init__()

    def get_file_items(self, files):
        """
        Called by Nautilus when building context menu.

        Args:
            files: List of selected Nautilus.FileInfo objects

        Returns:
            List containing the SEND-TO menu item
        """
        if not files:
            return []

        # Create top-level SEND-TO menu item
        top_menu = Nautilus.MenuItem(
            name="SendToMenuProvider::SendTo",
            label="SEND-TO",
            tip="Move selected items to bookmarked locations"
        )

        # Create submenu for bookmarks
        submenu = Nautilus.Menu()
        top_menu.set_submenu(submenu)

        # Parse bookmarks and build menu
        bookmarks = self.parse_bookmarks()

        if not bookmarks:
            # No bookmarks available
            no_bookmarks_item = Nautilus.MenuItem(
                name="SendToMenuProvider::NoBookmarks",
                label="(No bookmarks found)",
                tip="Add bookmarks in Nautilus to use this feature"
            )
            no_bookmarks_item.set_property('sensitive', False)
            submenu.append_item(no_bookmarks_item)
            return [top_menu]

        # Add each bookmark with its subdirectories
        for bookmark in bookmarks:
            bookmark_path = Path(bookmark['path'])

            # Skip if bookmark path doesn't exist
            if not bookmark_path.exists() or not bookmark_path.is_dir():
                continue

            # Create menu item for the bookmark
            bookmark_label = bookmark['label'] or bookmark_path.name
            bookmark_menu = Nautilus.MenuItem(
                name=f"SendToMenuProvider::Bookmark::{bookmark_path}",
                label=f"{bookmark_label}/",
                tip=f"Move to {bookmark_path}"
            )

            # Create submenu for this bookmark
            bookmark_submenu = Nautilus.Menu()
            bookmark_menu.set_submenu(bookmark_submenu)

            # Add "→ Move here" option for the bookmark root
            move_here_item = Nautilus.MenuItem(
                name=f"SendToMenuProvider::MoveHere::{bookmark_path}",
                label="→ (move here)",
                tip=f"Move to {bookmark_path}"
            )
            move_here_item.connect(
                'activate',
                self.on_move_files,
                files,
                str(bookmark_path)
            )
            bookmark_submenu.append_item(move_here_item)

            # Add separator
            separator = Nautilus.MenuItem(
                name=f"SendToMenuProvider::Separator::{bookmark_path}",
                label="────────────",
                tip=""
            )
            separator.set_property('sensitive', False)
            bookmark_submenu.append_item(separator)

            # Recursively build directory tree
            self.build_directory_menu(
                bookmark_submenu,
                bookmark_path,
                files,
                current_depth=0
            )

            submenu.append_item(bookmark_menu)

        return [top_menu]

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

    def build_directory_menu(self, parent_menu, directory, files, current_depth=0):
        """
        Recursively build menu with subdirectories.

        Args:
            parent_menu: Nautilus.Menu to add items to
            directory: Path object of directory to traverse
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
                subdir_menu = Nautilus.MenuItem(
                    name=f"SendToMenuProvider::Dir::{subdir}",
                    label=f"{subdir.name}/",
                    tip=f"Move to {subdir}"
                )

                # Create submenu
                subdir_submenu = Nautilus.Menu()
                subdir_menu.set_submenu(subdir_submenu)

                # Add "→ Move here" option
                move_here_item = Nautilus.MenuItem(
                    name=f"SendToMenuProvider::MoveHere::{subdir}",
                    label="→ (move here)",
                    tip=f"Move to {subdir}"
                )
                move_here_item.connect(
                    'activate',
                    self.on_move_files,
                    files,
                    str(subdir)
                )
                subdir_submenu.append_item(move_here_item)

                # Check if this directory has subdirectories
                try:
                    has_subdirs = any(item.is_dir() for item in subdir.iterdir())

                    if has_subdirs:
                        # Add separator
                        separator = Nautilus.MenuItem(
                            name=f"SendToMenuProvider::Separator::{subdir}",
                            label="────────────",
                            tip=""
                        )
                        separator.set_property('sensitive', False)
                        subdir_submenu.append_item(separator)

                        # Recursively add subdirectories
                        self.build_directory_menu(
                            subdir_submenu,
                            subdir,
                            files,
                            current_depth + 1
                        )

                except (PermissionError, OSError):
                    # Skip inaccessible directories
                    pass

                parent_menu.append_item(subdir_menu)

        except (PermissionError, OSError) as e:
            # Skip directories we can't read
            print(f"Cannot read directory {directory}: {e}")

    def on_move_files(self, menu_item, files, destination_path):
        """
        Move selected files to destination.

        Args:
            menu_item: The menu item that was clicked
            files: List of Nautilus.FileInfo objects to move
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

                # Move file - Nautilus will handle conflict resolution
                # Using NONE flag means Nautilus will prompt on conflicts
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
