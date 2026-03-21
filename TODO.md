# TODO

- [x] **IPC integration with nsd daemon**: `NsdClient` class monitors mount/unmount events and manages drive icons on desktop with configurable file-manager opener.

- [ ] Validate multi-monitor support in a real setup (currently untested).
	- Test scenario: second physical monitor connected (different make/model, mixed resolution).
	- Test scenario: monitor hotplug (connect/disconnect while `ldicons.py` is running).
	- Test scenario: different Wayland display/socket (e.g. non-default `WAYLAND_DISPLAY`).
	- Test scenario: drag icons across monitor boundaries and verify redraw/input regions.
	- Test scenario: per-monitor scale differences (HiDPI + non-HiDPI combination).

- [ ] Add optional swap behavior for grid snapping: if a target cell is already occupied during drag-and-drop, swap the two icons instead of moving to the next free cell.
- [ ] Add real locale-based hyphenation for icon labels (e.g. `pyphen` with `de_DE`) instead of purely character-based splitting for long words.
- [ ] Introduce proper UI localization with gettext (`.po`/`.mo`) instead of hardcoded strings: includes context-menu labels, tooltip fallbacks (e.g. trash), and other visible UI text.
- [ ] Extend status-emblem system to support additional configurable emblem types (without code changes), including per-type priority and icon-name mapping.
- [ ] Change CLI defaults for `--conf` and `--pos` to `~/.config/deskicons/` instead of workspace paths.
- [ ] Deployment: convert dependencies from the current `.venv` into a reproducible package list (`requirements.txt`/lockfile).
	- Current snapshot (venv):
		- cairocffi==1.7.1
		- CairoSVG==2.8.2
		- cffi==2.0.0
		- configparser==7.2.0
		- cssselect2==0.9.0
		- defusedxml==0.7.1
		- packaging==26.0
		- pillow==12.1.1
		- pip==26.0.1
		- pycparser==3.0
		- pywayland==0.4.18
		- pyxdg==0.28
		- setuptools==82.0.0
		- tinycss2==1.5.1
		- webencodings==0.5.1
		- wheel==0.46.3
		- xdg==6.0.0
