# Hear Yourself

A free, low-latency audio monitor for macOS. Hear your microphone through your speakers or headphones in real-time.

**[Download for macOS →](https://github.com/trenaryja/hear-yourself/releases/latest)**

## Installation

1. Download `Hear.Yourself.dmg` from [Releases](https://github.com/trenaryja/hear-yourself/releases/latest)
2. Open the DMG and drag **Hear Yourself.app** to your Applications folder
3. Launch the app — look for the microphone icon in your menu bar
4. Run the following command once to clear the macOS quarantine flag:

```bash
xattr -d com.apple.quarantine "/Applications/Hear Yourself.app"
```

> **Why is this necessary?** macOS Gatekeeper quarantines apps downloaded from the internet that aren't notarized with an Apple Developer certificate ($99/yr). This one command clears the flag safely. See [Roadmap](#roadmap) for a planned Homebrew Cask that will handle this automatically.

## Features

- **Ultra-low latency** — Extreme (~1.3ms) and Low (~2.7ms) presets, tunable to your hardware
- **Volume control** — Adjustable from 50% to 150%
- **Global hotkey** — Toggle monitoring with ⌃⇧M from any app
- **Device selection** — Choose input/output devices from the menu bar
- **Hotplug recovery** — Automatically pauses and resumes when a device is disconnected and reconnected
- **Auto-start** — Optionally start monitoring as soon as the app launches
- **Launch at Login** — Register as a login item without the Dock
- **Menu bar only** — No Dock icon, stays out of your way

## Requirements

- macOS 13 (Ventura) or later
- Apple Silicon recommended for lowest latency
- Microphone access permission (prompted on first launch)

## Building from Source

```bash
git clone https://github.com/trenaryja/hear-yourself.git
cd hear-yourself
uv run build.py          # builds Hear Yourself.app
uv run build.py --dmg    # also creates a distributable DMG
uv run build.py --deploy # builds and copies to /Applications
```

Requires [uv](https://docs.astral.sh/uv/) and macOS (for the build toolchain).

## Why?

The popular tool [LineIn](https://rogueamoeba.com/legacy/) was discontinued in 2017 and no longer works on modern macOS. Paid alternatives cost $50–120. This is a free, open-source replacement.

## Roadmap

- **Homebrew Cask** — `brew install --cask trenaryja/tap/hear-yourself` will install the app with no quarantine step required (Homebrew handles it automatically). Planned for a future release.
- **Configurable hotkey** — The default ⌃⇧M is a reasonable choice but may conflict with other apps. A settings UI to bind any key combination and save it to preferences is planned.
- **Liquid glass icons** — Replace the current flat SVG icons with a macOS 26-style liquid glass aesthetic. The menu bar "on" icon already renders in full color; the "off" icon uses macOS template rendering, which limits what's possible there, but the app icon and active state can be redesigned.
- **Language rewrite exploration** — Evaluating Swift as a longer-term rewrite target. A native Swift app using `NSStatusBar` + `AVAudioEngine` would eliminate the PyInstaller bundle (~150MB → ~5MB), enable proper notarization (removing the `xattr` install step), and use first-party macOS APIs throughout.
- **Raycast extension** — A native Raycast extension to toggle monitoring, switch devices, and adjust volume without opening the menu bar. Raycast extensions are built with React + TypeScript and published to the [Raycast Store](https://www.raycast.com/store). Requires the app to expose a CLI or IPC interface that the extension can talk to (`app.py` already supports `--cli` mode as a starting point).

## Attribution

Originally created by [gabrycina](https://github.com/gabrycina/hear-yourself) with Claude Opus. This fork adds volume control, a global hotkey, device hotplug recovery, auto-start, Launch at Login, SVG menu bar icons, and a modernized build system using [uv](https://docs.astral.sh/uv/) and PyInstaller.

---

Made with ♥ by [gabrycina](https://github.com/gabrycina) & Claude Opus · Continued by [trenaryja](https://github.com/trenaryja)
