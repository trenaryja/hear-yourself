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

## Attribution

Originally created by [gabrycina](https://github.com/gabrycina/hear-yourself) with Claude Opus. This fork adds volume control, a global hotkey, device hotplug recovery, auto-start, Launch at Login, SVG menu bar icons, and a modernized build system using [uv](https://docs.astral.sh/uv/) and PyInstaller.

---

Made with ♥ by [gabrycina](https://github.com/gabrycina) & Claude Opus · Continued by [trenaryja](https://github.com/trenaryja)
