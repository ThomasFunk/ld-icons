# ld-icons

> Show Files from a Directory on the Desktop

## Features

- [X] Show content from a folder as Icons on the Desktop
- [X] Use xdg_user_dir to use the default desktop directory
- [X] Start default application for the active file
- [X] Update the Icons on changes to the directory (added/removed files)
- [X] Drag and Drop Files from/to the Desktop
- [X] Launching Apps from the Desktop
- [X] Multi-Monitor Support
- [ ] Thumbnails for Images/Documents
- [X] Sort Rows of List Store based on Name/Type/Date
- [X] Context-Menu for creating files

## Supported Desktops

> Quoted from [gtk-layer-shell](https://github.com/wmww/gtk-layer-shell)

This application only works on Wayland, and only on Wayland compositors that
support the Layer Shell protocol. Layer shell **is supported** on:
- wlroots based compositors (such as **Sway**)
- Mir-based compositors (some may not enable the protocol by default and require
  `--add-wayland-extension zwlr_layer_shell_v1`)

Layer shell **is not supported** on:
- Gnome-on-Wayland
- Any X11 desktop

## Getting Started

### Dependencies

- gtk+-3.0
- gtk-layer-shell

Arch
```sh
sudo pacman -S gtk3 gtk-layer-shell
```

### Installation

```sh
git clone https://github.com/Geronymos/ld-icons
cd ld-icons
make
sudo make install
```

Uninstall
```sh
sudo make uninstall
```

### Usage

```sh
ldicons
```

It's recommended to have this automatically start with your Wayland compositor.
For Sway append the following to your config file `.config/sway/config `:
```
exec ldicons
```

### Python script mode (`ldicons.py` / `ldicons`)

For the Python implementation you can run:

```sh
python3 -u ldicons.py
```

CLI options:

```sh
python3 -u ldicons.py \
  -c ~/.config/ldicons/ldicons.conf \
  -p ~/.config/ldicons/icon_positions.json \
  -l ~/.config/ldicons/ldicons.log \
  --verbose
```

- `-c, --conf`: config path
- `-p, --pos`: icon positions JSON path
- `-l, --log`: log file path (default: `~/.config/ldicons/ldicons.log`)
- `--verbose`: enables debug output
- `-v, --version`: prints version

Input event debugging can be enabled with:

```sh
LDICONS_INPUT_DEBUG=1 python3 -u ldicons.py
```

This prints `enter/motion/button` pointer events to help diagnose hover/click issues.

The double-click opening behavior can be tuned in `ldicons.conf`:

```ini
[Behavior]
double_click_timeout = 0.3
```

Drag-and-drop snapping can be configured as well:

```ini
[Layout]
grid_direction = vertical
# 0 = wrap only at desktop/monitor boundary
grid_wrap_count = 0
snap_grid_x = 140
snap_grid_y = 180
snap_origin_x = 50
snap_origin_y = 50

[Behavior]
snap_to_grid = true
snap_avoid_overlap = true
```

Rubber-band multi-select (especially on `labwc`) can be tuned with:

```ini
[Behavior]
# Trigger key for rubber-band start on empty desktop
rubber_band_modifier = shift

# Trigger mouse button: left | middle | right
rubber_band_button = left

# Reliability grace window in milliseconds after interactions
# (helps with compositor timing/order quirks)
rubber_band_grace_ms = 700

# Layer-shell level for ldicons: background | bottom | top | overlay
layer = bottom
```

Context-menu actions now also include a `Sort ▶` submenu:

- `Sort by Name` (alphabetical)
- `Sort by Date` (newest first)
- `Clean up Grid` (re-snaps all icons to consecutive grid slots)

Hovering `Sort` opens the submenu automatically to the right.
These actions are available from the icon context menu.

The icon context menu also provides `Show hidden Files` as a checkbox toggle.
When enabled, dotfiles are included in the desktop icon list and persisted to config (`show_hidden_files = true`).

Custom status overlays (read-only / symlink) can be configured with a custom emblem directory:

```ini
[Appearance]
# Optional: custom emblem directory
status_emblems_path = ~/.config/ldicons/emblems
```

Lookup order for status overlays:

1. Custom emblems from `status_emblems_path` (if set and directory exists)
2. Current icon theme
3. Internal drawn fallback badge

Runtime behavior:

- Only one status overlay badge is rendered.
- Badge position is always bottom-right of the icon graphic.
- Priority is `readonly` first, then `symlink`.

Recognized custom emblem base names:

- Read-only: `emblem-readonly`, `changes-prevent`, `object-locked`, `emblem-locked`, `readonly`, `lock`
- Symlink: `emblem-symbolic-link`, `emblem-symlink`, `emblem-symlink-symbolic`, `insert-link`, `symlink`, `link`

Supported file extensions in custom directory: `.svg`, `.png`, `.xpm` (or file without extension if provided exactly).

### Localization (gettext)

Menu labels and related dialog texts use gettext catalogs.

- Domain: `ldicons`
- Locale directory: `locale/<lang>/LC_MESSAGES/`
- Source catalog example: `locale/de/LC_MESSAGES/ldicons.po`

Compile `.po` to `.mo`:

```sh
msgfmt -o locale/de/LC_MESSAGES/ldicons.mo locale/de/LC_MESSAGES/ldicons.po
```

Notes:
- If modifier handling is unreliable in your compositor, try `rubber_band_modifier = none` and a dedicated button (for example `middle`).
- A short post-interaction defocus effect on empty-desktop click can happen while grace is active; reduce `rubber_band_grace_ms` if this feels too long.

Icon positions are persisted to a JSON file and restored on startup:

```ini
[Behavior]
positions_file = ./icon_positions.json
```

### Development

Dependencies
- bear

To have warnings and autocompletion with clangd in Vim you can generate the
`compile-commands.json` with
```sh
make clangd
```

## License

This project is licensed under the GPL-3 License - see the `LICENSE` file for details

