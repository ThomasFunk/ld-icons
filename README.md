# ld-icons

> Show Files from a Directory on the Desktop

`ld-icons` stands for Layer-Desktop-Icons and is a lightweight Wayland desktop-icons service for wlroots-based compositors.

It renders files from your Desktop folder directly onto a layer-shell surface, keeps icon
positions persistent across restarts, and supports practical desktop interactions like
multi-select, drag-and-drop grid placement, context-menu actions, sorting, and status overlays.

Why ld-icons? Aren't there enough options already? The short answer is: yes and no. Major desktop environments have desktop icons, but they often bring too many dependencies.

For compositors like labwc, sway, etc., there are a few options:

pcmanfm-qt - The file manager from the LXQt project is the spiritual successor to the classic pcmanfm and works well under Wayland for managing the desktop.

dicons - https://github.com/Geronymos/desktop-icons - a C/C++ tool showing files from a directory on the desktop. Basic functionality is available.

nwg-drawer/nwg-wrapper - https://github.com/nwg-piotr/nwg-drawer - From the nwg-shell family. With nwg-wrapper, you can display scripts or icons in fixed positions on the desktop.

Since my project (labwc DE) is intended to be lean, based on GTK, and free of additional compiled tools, pcmanfm-qt was ruled out because of its Qt dependency. nwg-drawer/nwg-wrapper was ruled out because it mixes several languages and is missing from some major distributions.

The only remaining option was dicons by Geronymos, which unfortunately is not available in distributions, is not feature-complete, and requires compilation.

For this reason, I decided to write an alternative in Python. I used Google's Gemini for the basics (connecting to the Wayland server, rendering files, and collecting features), and GitHub Copilot for debugging and improvements.

The result is a tool that has all the features of dicons plus extensions like sorting, multi-file moves, a configuration file with numerous settings, and command-line options.

So far, it has only been tested in a wlroots-based environment and within the project setup. Even with full debug output, performance was quite acceptable.

## Features

- [X] Show content from the Desktop folder as Icons on the Desktop
- [X] Use xdg_user_dir to use the default desktop directory
- [X] Start default application for the active file
- [X] Update the Icons on changes to the directory (added/removed files)
- [X] Drag and Drop (reposition icons on desktop grid)
- [X] Launching Apps from the Desktop
- [X] Multi-Monitor Support
- [X] Rubber-band multi-select with group move
- [X] Context menu: Open / Edit / Rename / Delete / Properties
- [X] Sort submenu (Name / Type / Date / Clean up Grid)
- [X] Show hidden files toggle (persistent)
- [X] Status overlays (read-only / symlink, custom theme fallback)
- [X] Thumbnails for Images
- [ ] Thumbnails for Documents
- [X] Sort Rows of List Store based on Name/Type/Date
- [ ] Context-Menu for creating files (real create action pending)
- [ ] File drag-and-drop between desktop and other applications (Wayland data-device DnD)

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

- Python 3.10+
- `pip` (to install Python packages)
- A Wayland compositor that supports `zwlr_layer_shell_v1` (layer-shell)
- Python packages listed in `requirements.txt`
- `gettext` tools (`msgfmt`) for compiling localization files

### Installation

Clone repository:

```sh
git clone https://github.com/ThomasFunk/ld-icons
cd ld-icons
```

Install Python dependencies:

```sh
python3 -m pip install -r requirements.txt
```

System-wide installation (default: `/usr/local`):

```sh
make
sudo make install
```

User-local installation (without `sudo`):

```sh
make PREFIX="$HOME/.local" install
```

Uninstall:

```sh
sudo make uninstall
# or for user-local install:
make PREFIX="$HOME/.local" uninstall
```


### Usage

```sh
ldicons
```

It's recommended to start this automatically with your Wayland compositor.
For Sway, append the following to your config file `.config/sway/config`:
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
- `Sort by Type` (folders → images → videos → audio → documents → archives → others)
- `Sort by Date` (newest first)
- `Clean up Grid` (re-snaps all icons to consecutive grid slots)

Hovering `Sort` opens the submenu automatically to the right.
These actions are available from the icon context menu.

The icon context menu also provides `Show hidden files` as a checkbox toggle.
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

This tool is not fully tested yet. Everyone who wants to help is very welcome. ^^

## License

This project is licensed under the GPL-3 License - see the `LICENSE` file for details

