#!/usr/bin/env python3
"""
SEND-TO Dialog for Thunar/File Managers
Shows a dialog to select destination from bookmarks and move files.
"""

import sys
import os
from pathlib import Path
from urllib.parse import unquote, urlparse
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, Gio, GLib


class SendToDialog(Gtk.Dialog):
    """Dialog to select destination folder from bookmarks."""

    MAX_DEPTH = 5

    def __init__(self, files):
        super().__init__(title="Send To", flags=0)
        self.files = files
        self.selected_path = None

        # Set up dialog
        self.set_default_size(500, 600)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Move Here", Gtk.ResponseType.OK
        )
        self.set_default_response(Gtk.ResponseType.OK)

        # Create main layout
        box = self.get_content_area()
        box.set_spacing(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)

        # Add label
        file_count = len(files)
        label_text = f"Move {file_count} item{'s' if file_count != 1 else ''} to:"
        label = Gtk.Label(label=label_text)
        label.set_halign(Gtk.Align.START)
        box.pack_start(label, False, False, 0)

        # Create scrolled window with tree view
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        box.pack_start(scrolled, True, True, 0)

        # Create tree store and tree view
        self.tree_store = Gtk.TreeStore(str, str)  # Display name, full path
        self.tree_view = Gtk.TreeView(model=self.tree_store)
        self.tree_view.set_headers_visible(False)

        # Add text column
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Location", renderer, text=0)
        self.tree_view.append_column(column)

        # Connect selection handler
        selection = self.tree_view.get_selection()
        selection.connect("changed", self.on_selection_changed)

        scrolled.add(self.tree_view)

        # Populate tree with bookmarks
        self.populate_bookmarks()

        # Show selected path
        self.path_label = Gtk.Label(label="Select a destination")
        self.path_label.set_halign(Gtk.Align.START)
        self.path_label.set_ellipsize(3)  # Ellipsize at end
        box.pack_start(self.path_label, False, False, 0)

        self.show_all()

    def parse_bookmarks(self):
        """Parse GTK bookmarks file."""
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

                    parts = line.split(None, 1)
                    uri = parts[0]
                    label = parts[1] if len(parts) > 1 else None

                    if not uri.startswith('file://'):
                        continue

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

    def populate_bookmarks(self):
        """Populate tree view with bookmarks and subdirectories."""
        bookmarks = self.parse_bookmarks()

        if not bookmarks:
            iter = self.tree_store.append(None, ["(No bookmarks found)", ""])
            return

        for bookmark in bookmarks:
            bookmark_path = Path(bookmark['path'])

            if not bookmark_path.exists() or not bookmark_path.is_dir():
                continue

            label = bookmark['label'] or bookmark_path.name
            parent_iter = self.tree_store.append(None, [f"📁 {label}", str(bookmark_path)])

            # Recursively add subdirectories
            self.add_subdirectories(parent_iter, bookmark_path, 0)

    def add_subdirectories(self, parent_iter, directory, depth):
        """Recursively add subdirectories to tree."""
        if depth >= self.MAX_DEPTH:
            return

        try:
            subdirs = []
            for item in directory.iterdir():
                if item.is_dir():
                    subdirs.append(item)

            subdirs.sort(key=lambda p: p.name.lower())

            for subdir in subdirs:
                child_iter = self.tree_store.append(
                    parent_iter,
                    [f"  {'  ' * depth}📁 {subdir.name}", str(subdir)]
                )
                self.add_subdirectories(child_iter, subdir, depth + 1)

        except (PermissionError, OSError):
            pass

    def on_selection_changed(self, selection):
        """Handle tree view selection change."""
        model, iter = selection.get_selected()
        if iter:
            path = model[iter][1]
            if path:
                self.selected_path = path
                self.path_label.set_text(f"Destination: {path}")
            else:
                self.selected_path = None
                self.path_label.set_text("Select a destination")

    def get_selected_path(self):
        """Get the selected destination path."""
        return self.selected_path


def move_files(files, destination):
    """Move files to destination using Gio."""
    destination_path = Path(destination)
    errors = []

    for file_path in files:
        try:
            source_path = Path(file_path)
            source = Gio.File.new_for_path(str(source_path))

            target_path = destination_path / source_path.name
            target = Gio.File.new_for_path(str(target_path))

            # Move file - will prompt on conflicts
            source.move(
                target,
                Gio.FileCopyFlags.NONE,
                None,
                None,
                None
            )
            print(f"Moved: {source_path} → {target_path}")

        except GLib.Error as e:
            error_msg = f"{source_path.name}: {e.message}"
            errors.append(error_msg)
            print(f"Error: {error_msg}")
        except Exception as e:
            error_msg = f"{source_path.name}: {str(e)}"
            errors.append(error_msg)
            print(f"Error: {error_msg}")

    return errors


def show_error_dialog(errors):
    """Show error dialog with list of errors."""
    dialog = Gtk.MessageDialog(
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text="Some files could not be moved"
    )
    dialog.format_secondary_text("\n".join(errors))
    dialog.run()
    dialog.destroy()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: sendto-dialog.py <file1> [file2] ...")
        sys.exit(1)

    files = sys.argv[1:]

    # Verify files exist
    valid_files = []
    for f in files:
        if os.path.exists(f):
            valid_files.append(os.path.abspath(f))
        else:
            print(f"Warning: File not found: {f}")

    if not valid_files:
        print("Error: No valid files provided")
        sys.exit(1)

    # Show dialog
    dialog = SendToDialog(valid_files)
    response = dialog.run()
    destination = dialog.get_selected_path()
    dialog.destroy()

    # Move files if OK was clicked and destination selected
    if response == Gtk.ResponseType.OK and destination:
        errors = move_files(valid_files, destination)

        if errors:
            show_error_dialog(errors)
            sys.exit(1)
        else:
            print(f"Successfully moved {len(valid_files)} file(s)")
            sys.exit(0)
    else:
        print("Cancelled")
        sys.exit(0)


if __name__ == "__main__":
    main()
