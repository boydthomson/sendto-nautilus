#!/usr/bin/env python3
"""
SEND-TO Dialog for File Managers
Enhanced version with search, keyboard shortcuts, and improved UX.
"""

import sys
import os
import json
from pathlib import Path
from urllib.parse import unquote, urlparse
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, Gio, GLib, Gdk


class SendToDialog(Gtk.Dialog):
    """Enhanced dialog to select destination folder from bookmarks."""

    MAX_DEPTH = 5
    CONFIG_FILE = Path.home() / '.config' / 'sendto-dialog.json'

    def __init__(self, files):
        super().__init__(title="Send To", flags=0)
        self.files = files
        self.selected_path = None
        self.all_paths = []  # For search functionality

        # Load config
        self.config = self.load_config()

        # Set up dialog
        width = self.config.get('window_width', 600)
        height = self.config.get('window_height', 700)
        self.set_default_size(width, height)

        # Set position
        self.set_position(Gtk.WindowPosition.CENTER)

        self.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Move Here", Gtk.ResponseType.OK
        )
        self.set_default_response(Gtk.ResponseType.OK)

        # Connect window state tracking
        self.connect('configure-event', self.on_configure)
        self.connect('key-press-event', self.on_key_press)

        # Create main layout
        box = self.get_content_area()
        box.set_spacing(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)

        # Add header with file count
        file_count = len(files)
        label_text = f"Move {file_count} item{'s' if file_count != 1 else ''} to:"
        label = Gtk.Label(label=label_text)
        label.set_halign(Gtk.Align.START)
        label.set_markup(f"<b>{label_text}</b>")
        box.pack_start(label, False, False, 0)

        # Add search box
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        search_label = Gtk.Label(label="Search:")
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Type to filter folders...")
        self.search_entry.connect('search-changed', self.on_search_changed)
        search_box.pack_start(search_label, False, False, 0)
        search_box.pack_start(self.search_entry, True, True, 0)
        box.pack_start(search_box, False, False, 5)

        # Create scrolled window with tree view
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        box.pack_start(scrolled, True, True, 0)

        # Create tree store and tree view
        # Columns: Display name, full path, visible (for search)
        self.tree_store = Gtk.TreeStore(str, str, bool)
        self.tree_filter = self.tree_store.filter_new()
        self.tree_filter.set_visible_column(2)

        self.tree_view = Gtk.TreeView(model=self.tree_filter)
        self.tree_view.set_headers_visible(False)
        self.tree_view.set_enable_search(True)
        self.tree_view.set_search_column(0)

        # Add text column
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Location", renderer, text=0)
        self.tree_view.append_column(column)

        # Connect selection and activation handlers
        selection = self.tree_view.get_selection()
        selection.connect("changed", self.on_selection_changed)
        self.tree_view.connect("row-activated", self.on_row_activated)

        scrolled.add(self.tree_view)

        # Add keyboard hints
        hints = Gtk.Label()
        hints.set_markup("<small><i>💡 Tip: Use ↑↓ arrows, type to search, Enter to move, Esc to cancel</i></small>")
        hints.set_halign(Gtk.Align.START)
        box.pack_start(hints, False, False, 0)

        # Show selected path
        self.path_label = Gtk.Label(label="Select a destination")
        self.path_label.set_halign(Gtk.Align.START)
        self.path_label.set_ellipsize(3)  # Ellipsize at end
        self.path_label.set_selectable(True)
        box.pack_start(self.path_label, False, False, 0)

        # Populate tree with bookmarks
        self.populate_bookmarks()

        # Expand first bookmark by default
        first_iter = self.tree_filter.get_iter_first()
        if first_iter:
            path = self.tree_filter.get_path(first_iter)
            self.tree_view.expand_row(path, False)
            selection.select_iter(first_iter)

        self.show_all()

    def load_config(self):
        """Load saved configuration."""
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_config(self):
        """Save configuration."""
        try:
            self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def on_configure(self, widget, event):
        """Track window size changes."""
        self.config['window_width'] = event.width
        self.config['window_height'] = event.height
        return False

    def on_key_press(self, widget, event):
        """Handle keyboard shortcuts."""
        # Ctrl+F to focus search
        if event.state & Gdk.ModifierType.CONTROL_MASK and event.keyval == Gdk.KEY_f:
            self.search_entry.grab_focus()
            return True

        # Escape clears search if it has focus
        if event.keyval == Gdk.KEY_Escape and self.search_entry.has_focus():
            self.search_entry.set_text("")
            return True

        return False

    def on_search_changed(self, entry):
        """Handle search text changes."""
        search_text = entry.get_text().lower()

        def set_visibility(store, path, iter, search_text):
            """Set visibility based on search."""
            display_name = store.get_value(iter, 0).lower()
            full_path = store.get_value(iter, 1).lower()

            if not search_text:
                # Show all if no search
                store.set_value(iter, 2, True)
            else:
                # Show if matches name or path
                visible = search_text in display_name or search_text in full_path
                store.set_value(iter, 2, visible)

        self.tree_store.foreach(set_visibility, search_text)

        # Expand all if searching
        if search_text:
            self.tree_view.expand_all()
        else:
            self.tree_view.collapse_all()
            # Re-expand first item
            first_iter = self.tree_filter.get_iter_first()
            if first_iter:
                path = self.tree_filter.get_path(first_iter)
                self.tree_view.expand_row(path, False)

    def on_row_activated(self, tree_view, path, column):
        """Handle double-click or Enter key."""
        model = tree_view.get_model()
        iter = model.get_iter(path)
        selected_path = model[iter][1]

        if selected_path:
            self.selected_path = selected_path
            self.response(Gtk.ResponseType.OK)

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
            iter = self.tree_store.append(None, ["(No bookmarks found - press Ctrl+D in Thunar to add)", "", True])
            return

        for bookmark in bookmarks:
            bookmark_path = Path(bookmark['path'])

            if not bookmark_path.exists() or not bookmark_path.is_dir():
                continue

            label = bookmark['label'] or bookmark_path.name
            parent_iter = self.tree_store.append(None, [f"📁 {label}", str(bookmark_path), True])
            self.all_paths.append(str(bookmark_path))

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
                display_name = f"  {'  ' * depth}📁 {subdir.name}"
                child_iter = self.tree_store.append(
                    parent_iter,
                    [display_name, str(subdir), True]
                )
                self.all_paths.append(str(subdir))
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
                self.path_label.set_markup(f"<b>Destination:</b> {path}")
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
            print(f"✓ Moved: {source_path.name} → {target_path.parent}")

        except GLib.Error as e:
            error_msg = f"{source_path.name}: {e.message}"
            errors.append(error_msg)
            print(f"✗ Error: {error_msg}")
        except Exception as e:
            error_msg = f"{source_path.name}: {str(e)}"
            errors.append(error_msg)
            print(f"✗ Error: {error_msg}")

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


def show_success_notification(count, destination):
    """Show success notification."""
    try:
        # Try to use notify-send if available
        import subprocess
        subprocess.run([
            'notify-send',
            'Files Moved',
            f'Successfully moved {count} file{"s" if count != 1 else ""} to {Path(destination).name}',
            '-i', 'folder',
            '-t', '3000'
        ], check=False)
    except:
        pass


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: sendto-dialog <file1> [file2] ...")
        print("\nSEND-TO Dialog - Move files to bookmarked locations")
        print("Add bookmarks in your file manager (Ctrl+D) to use this tool.")
        sys.exit(1)

    files = sys.argv[1:]

    # Verify files exist
    valid_files = []
    for f in files:
        if os.path.exists(f):
            valid_files.append(os.path.abspath(f))
        else:
            print(f"⚠ Warning: File not found: {f}")

    if not valid_files:
        print("✗ Error: No valid files provided")
        sys.exit(1)

    # Show dialog
    dialog = SendToDialog(valid_files)
    response = dialog.run()
    destination = dialog.get_selected_path()

    # Save config before destroying
    dialog.save_config()
    dialog.destroy()

    # Move files if OK was clicked and destination selected
    if response == Gtk.ResponseType.OK and destination:
        errors = move_files(valid_files, destination)

        if errors:
            show_error_dialog(errors)
            sys.exit(1)
        else:
            print(f"\n✓ Successfully moved {len(valid_files)} file(s) to {destination}")
            show_success_notification(len(valid_files), destination)
            sys.exit(0)
    else:
        print("✗ Cancelled")
        sys.exit(0)


if __name__ == "__main__":
    main()
