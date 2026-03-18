# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-03-18
### Added
- Device hotplug recovery, auto-start on launch, extract config.py, merge CLI
- Replace emoji icons with SVGs, consolidate build pipeline
- Add Launch at Login, --deploy build flag, remove About menu item
- Add volume control and global hotkey (⌃⇧M)
### Changed
- Derive latency labels dynamically, remove unused CLI audio args
### Fixed
- Prevent watchdog notification spam, teardown inconsistency, single-instance crash on cold start
- Increase DMG intermediate size to 300m
### Internal
- Switch to PyInstaller + uv, replace Makefile with build.py
- Publish as fork, update attribution, bundle ID, version, add release pipeline
## [1.0.0] - 2025-12-30

