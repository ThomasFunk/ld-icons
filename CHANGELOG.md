# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog.

## Release Notes

- Version sections follow semantic versioning (`MAJOR.MINOR.PATCH`).
- Suggested tag names: `v0.2.0`, `v0.3.0`, etc.
- Keep `[Unreleased]` at the top for upcoming, not-yet-tagged changes.

## [Unreleased]

## [0.5.1] - 2026-03-06

### Added
- Sort submenu now supports `Sort by Type` with fixed category order (folders, images, videos, audio, documents, archives, others).

### Fixed
- Desktop layer surface no longer requests keyboard focus; this prevents focus loss in regular apps (e.g. Alacritty).

## [0.5.0] - 2026-03-05

### Added
- Icon context menu now includes a hover-open `Sort` submenu (`Sort ▶`) with `Sort by Name`, `Sort by Date`, and `Clean up Grid`.
- Icon context menu now includes `Show hidden Files` as a checkbox toggle.

### Changed
- Grid helper actions now persist updated icon positions immediately.
- Hidden file visibility is now persisted via `show_hidden_files` in `ldicons.conf`.

## [0.4.2] - 2026-03-05

### Added
- Configurable custom status emblem directory via `status_emblems_path` in `ldicons.conf`.
- Custom emblem lookup support for read-only/symlink overlays (`.svg`, `.png`, `.xpm`, plus direct filenames).

### Changed
- Status overlay resolution order is now: custom emblem path → active icon theme → internal drawn fallback.
- Runtime status overlay behavior now renders exactly one badge at icon bottom-right.
- Single-badge priority is now `readonly` before `symlink`.
- `README.md` updated with custom-emblem configuration and runtime overlay behavior.

### Fixed
- Overlay rendering path is now guarded and resilient, avoiding icon draw interruptions on badge load failures.

## [0.4.0] - 2026-03-05

### Added
- Rubber-band multi-selection for desktop icons (drag selection rectangle on empty area).
- Group drag-and-drop for selected icons, including grid snap and persisted position updates.
- Multi-item context-menu actions for selected icons (`Open`, `Delete`).
- Configurable rubber-band trigger options in `ldicons.conf`:
  - `rubber_band_modifier` (`none|ctrl|alt|shift|super`)
  - `rubber_band_button` (`left|middle|right`)
  - `rubber_band_grace_ms` (temporary reliability window after interaction)

### Changed
- Selection rendering now supports persistent multi-selection highlight.
- Keyboard interactivity for layer surfaces is now mode-dependent when a modifier-based rubber-band trigger is used.
- Input-region handling now supports a short grace window to make post-menu/post-click rubber-band start reproducible.
- Selection reset behavior is now explicit (`Esc`) instead of aggressive auto-clear on pointer leave.

### Fixed
- Rubber-band startup reliability improved for labwc-style interaction timing.
- Multi-monitor drag/drop now updates selected icon groups consistently.
- Rubber-band overlay rendering now uses proper BGRA alpha blending, so transparent fill no longer obscures icon pixels underneath.

## [0.3.0] - 2026-03-04

### Added
- Monitor-aware drag debug logs for surface transitions (`from -> to`) and drop target diagnostics.
- Additional VS Code debug profile with explicit `WAYLAND_DISPLAY=wayland-1` next to auto-display mode.

### Changed
- Multi-monitor rendering path now uses per-output layer-shell surfaces and per-monitor input regions.
- Persistent position format now stores monitor-aware grid coordinates (`monitor`, `grid_x`, `grid_y`) with `x/y` fallback compatibility.
- Pointer motion/drag handling now keeps global desktop coordinates across monitor boundaries.
- Workspace Python setup now pins VS Code debugging to `${workspaceFolder}/.venv/bin/python`.

### Fixed
- `wl_output.done` callback compatibility issue (varying callback arity) in multi-monitor mode.
- Drag continuity during cross-surface monitor transitions (`leave` no longer clears hover state while dragging).
- Runtime issues caused by copied virtual environments with stale absolute paths by standardizing local `.venv` usage.

## [0.2.0] - 2026-03-04

### Added
- Configurable layer selection for `ldicons.py` via `ldicons.conf` (`background|bottom|top|overlay`).
- Configurable `double_click_timeout` in `ldicons.conf` for single-click select / double-click open behavior.
- Configurable drag-and-drop grid snapping (`snap_to_grid`, `snap_grid_x/y`, `snap_origin_x/y`).
- Configurable grid collision avoidance during snap (`snap_avoid_overlap`).
- Configurable grid fill direction (`grid_direction = vertical|horizontal`).
- Configurable forced wrap count for icon layout blocks (`grid_wrap_count`).
- Persistent icon positions via JSON file (`positions_file`) with restore on startup.
- Optional input event debug mode via environment variable aliases (`LDICONS_INPUT_DEBUG`, `PYDICONS_INPUT_DEBUG`, `DICONS_INPUT_DEBUG`).
- Structured function docstrings in `ldicons.py`.
- Context menu rendering in the PIL/mmap render path.
- `execute_icon()` compatibility alias to preserve click-path behavior.
- This `CHANGELOG.md` for release-ready project history.

### Changed
- Method layout in `ldicons.py` reorganized into feature groups for better navigation.
- Class-level attribute annotations added in `LDIcons` to improve VS Code outline readability.
- Pointer button handling made robust across multiple button code variants (left/right/middle).
- Input-region behavior refined:
  - normal mode: only icon + label hit regions are active,
  - menu-open mode: full-surface region is temporarily active to allow outside-click menu close.
- Icon move via drag-and-drop now snaps to configurable grid on drop.
- `ldicons.conf` comments improved for maintainability (layer behavior + debug usage).
- `README.md` extended with Python script usage and input-debug instructions.

### Fixed
- Wayland event-loop bug where `dispatch(block=False)` did not read new events.
- Seat capability handling: pointer initialization now follows `wl_seat.capabilities`.
- Missing pointer handlers (`enter`/`leave`) causing stale hover/menu state.
- Repeated configure/re-layout churn by processing layer-surface configure events only when needed.
- Right-click menu visibility issue (menu state changed but was not drawn).
- Outside-click close behavior for context menu.
- Middle-click behavior now distinct from left-click.
