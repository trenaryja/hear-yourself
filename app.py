#!/usr/bin/env -S uv run python
"""
Menu bar app to hear your microphone through your speakers with minimal latency.

Made with ♥ by gabrycina & Claude Opus
Continued by trenaryja
"""

import rumps
import sounddevice as sd
import argparse
import json
import os
import sys
import fcntl
from pathlib import Path

try:
    from ServiceManagement import SMAppService
    _SM_AVAILABLE = True
except ImportError:
    _SM_AVAILABLE = False

from config import (
    APP_NAME, APP_NAME_SLUG,
    DEFAULT_BLOCKSIZE, DEFAULT_VOLUME, DEFAULT_HOTKEY, HOTKEY_DISPLAY,
    SAMPLERATE, LATENCY_PRESETS, VOLUME_PRESETS,
)

_BASE = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else Path(__file__).parent



# Single instance lock file
LOCK_FILE = os.path.expanduser(f"~/.{APP_NAME_SLUG}.lock")

# Preferences
PREFS_DIR = os.path.expanduser(f"~/Library/Application Support/{APP_NAME}")
PREFS_FILE = os.path.join(PREFS_DIR, "prefs.json")


def load_prefs():
    """Load preferences from disk. Returns defaults if file doesn't exist."""
    defaults = {"auto_start": True, "volume": DEFAULT_VOLUME}
    try:
        with open(PREFS_FILE) as f:
            prefs = json.load(f)
            return {**defaults, **prefs}
    except (FileNotFoundError, json.JSONDecodeError):
        return defaults


def save_prefs(prefs):
    """Save preferences to disk."""
    os.makedirs(PREFS_DIR, exist_ok=True)
    with open(PREFS_FILE, 'w') as f:
        json.dump(prefs, f)


def ensure_single_instance():
    """Ensure only one instance of the app is running."""
    global lock_file_handle
    lock_file_handle = open(LOCK_FILE, 'w')
    try:
        fcntl.flock(lock_file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Write PID to lock file
        lock_file_handle.write(str(os.getpid()))
        lock_file_handle.flush()
        return True
    except IOError:
        # Another instance is running
        return False


class App(rumps.App):
    def __init__(self):
        super().__init__("", quit_button=None)

        self.stream = None
        self.is_running = False
        self.input_device = sd.default.device[0]
        self.output_device = sd.default.device[1]
        self.blocksize = DEFAULT_BLOCKSIZE
        self.volume = DEFAULT_VOLUME
        self.prefs = load_prefs()

        # Track device names for hotplug recovery
        self._input_name = None
        self._output_name = None
        self._waiting_for_reconnect = False

        self.build_menu()
        self.update_title()
        rumps.Timer(self._check_devices, 2).start()
        self._start_hotkey_listener()

        if self.prefs["auto_start"]:
            rumps.Timer(self._auto_start, 0.5).start()
        else:
            rumps.Timer(self.show_welcome, 1).start()

    def build_menu(self):
        """Build the menu with current devices."""
        self.menu.clear()

        # Status / Toggle
        if self.is_running:
            self.menu.add(rumps.MenuItem("● Monitoring Active", callback=None))
            self.menu.add(rumps.MenuItem(f"Stop Monitoring  {HOTKEY_DISPLAY}", callback=self.toggle_monitoring))
        else:
            self.menu.add(rumps.MenuItem("○ Monitoring Stopped", callback=None))
            self.menu.add(rumps.MenuItem(f"Start Monitoring  {HOTKEY_DISPLAY}", callback=self.toggle_monitoring))

        self.menu.add(rumps.separator)

        # Device submenus
        for label, kind, attr in [("Input Device", "input", "input_device"),
                                   ("Output Device", "output", "output_device")]:
            menu = rumps.MenuItem(label)
            current = getattr(self, attr)
            for idx, name in self._get_devices(kind):
                item = rumps.MenuItem(
                    f"{'✓ ' if idx == current else '   '}{name}",
                    callback=lambda _, i=idx, a=attr: self._change_setting(a, i)
                )
                menu.add(item)
            self.menu.add(menu)

        self.menu.add(rumps.separator)

        # Latency settings
        latency_menu = rumps.MenuItem("Latency")
        for blocksize, label in LATENCY_PRESETS:
            item = rumps.MenuItem(
                f"{'✓ ' if blocksize == self.blocksize else '   '}{label}",
                callback=lambda _, b=blocksize: self._change_setting('blocksize', b)
            )
            latency_menu.add(item)
        self.menu.add(latency_menu)

        # Volume
        volume_menu = rumps.MenuItem("Volume")
        for vol, label in VOLUME_PRESETS:
            item = rumps.MenuItem(
                f"{'✓ ' if vol == self.volume else '   '}{label}",
                callback=lambda _, v=vol: self._change_volume(v)
            )
            volume_menu.add(item)
        self.menu.add(volume_menu)

        self.menu.add(rumps.separator)

        # Settings
        auto_label = f"{'✓ ' if self.prefs['auto_start'] else '   '}Start Monitoring on Launch"
        self.menu.add(rumps.MenuItem(auto_label, callback=self._toggle_auto_start))

        if _SM_AVAILABLE:
            login_label = f"{'✓ ' if self._login_item_enabled() else '   '}Launch at Login"
            self.menu.add(rumps.MenuItem(login_label, callback=self._toggle_login_item))

        self.menu.add(rumps.separator)

        self.menu.add(rumps.MenuItem("Quit", callback=self.quit_app))

    def _passthrough(self, indata, outdata, _frames, _time, _status):
        """Audio callback: copies input buffer directly to output (mic → speakers)."""
        try:
            outdata[:] = indata if self.volume == 1.0 else indata * self.volume
        except ValueError:
            outdata.fill(0)  # Shape mismatch (e.g. driver negotiated different channel count)

    def _change_volume(self, value):
        self.volume = value
        self.prefs["volume"] = value
        save_prefs(self.prefs)
        self.build_menu()

    def _start_hotkey_listener(self):
        try:
            from pynput import keyboard
            hotkey = self.prefs.get("hotkey", DEFAULT_HOTKEY)
            listener = keyboard.GlobalHotKeys({hotkey: lambda: self.toggle_monitoring(None)})
            listener.daemon = True
            listener.start()
        except Exception:
            pass  # Accessibility permission not granted or pynput unavailable

    def _get_devices(self, kind):
        key = f'max_{kind}_channels'
        return [(i, d['name']) for i, d in enumerate(sd.query_devices()) if d[key] > 0]

    def _device_name(self, idx):
        """Get device name by index, or None if invalid."""
        try:
            return sd.query_devices(idx)['name']
        except Exception:
            return None

    def _find_device_by_name(self, name, kind):
        """Find a device index by name. Returns None if not found."""
        for idx, dev_name in self._get_devices(kind):
            if dev_name == name:
                return idx
        return None

    def _check_devices(self, _=None):
        """Polling watchdog — detects device loss and reconnection.
        IMPORTANT: Never call sd.query_devices() while a stream is active.
        It disrupts the real-time audio thread and causes progressive glitches."""
        if self.is_running:
            # Check stream health without querying devices
            try:
                if not self.stream or not self.stream.active:
                    self.stop_stream()
                    self._waiting_for_reconnect = True
                    rumps.notification(
                        title=APP_NAME,
                        subtitle="Audio device disconnected",
                        message="Monitoring paused. Will resume when the device reconnects.",
                        sound=False
                    )
            except Exception:
                self.stop_stream()
                self._waiting_for_reconnect = True
        elif self._waiting_for_reconnect:
            # Check if remembered devices are back
            in_idx = self._find_device_by_name(self._input_name, "input")
            out_idx = self._find_device_by_name(self._output_name, "output")
            if in_idx is not None and out_idx is not None:
                self._waiting_for_reconnect = False
                self.input_device = in_idx
                self.output_device = out_idx
                self.start_stream()
                rumps.notification(
                    title=APP_NAME,
                    subtitle="Audio device reconnected",
                    message="Monitoring resumed.",
                    sound=False
                )

    def _auto_start(self, timer):
        """Start monitoring automatically on launch (fires once)."""
        timer.stop()
        self.start_stream()

    def _toggle_auto_start(self, _):
        """Toggle the auto-start preference."""
        self.prefs["auto_start"] = not self.prefs["auto_start"]
        save_prefs(self.prefs)
        self.build_menu()

    def _login_item_enabled(self):
        return SMAppService.mainAppService().status() == 1  # SMAppServiceStatusEnabled

    def _toggle_login_item(self, _):
        svc = SMAppService.mainAppService()
        try:
            if self._login_item_enabled():
                svc.unregisterAndReturnError_(None)
            else:
                svc.registerAndReturnError_(None)
        except Exception as e:
            rumps.alert("Error", f"Could not update login item:\n{e}")
        self.build_menu()

    def update_title(self):
        if self.is_running:
            self.template = None
            self.icon = str(_BASE / "icons" / "on.svg")
        else:
            self.template = True
            self.icon = str(_BASE / "icons" / "off.svg")

    def start_stream(self):
        """Start the audio stream."""
        try:
            self.stream = sd.Stream(
                device=(self.input_device, self.output_device),
                samplerate=SAMPLERATE,
                blocksize=self.blocksize,
                dtype='float32',
                latency='low',
                channels=1,
                callback=self._passthrough
            )
            self.stream.start()
            self.is_running = True
            self._input_name = self._device_name(self.input_device)
            self._output_name = self._device_name(self.output_device)
            self.update_title()
            self.build_menu()
        except Exception as e:
            rumps.alert("Error", f"Could not start audio stream:\n{e}")

    def stop_stream(self):
        """Stop the audio stream."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.is_running = False
        self.update_title()
        self.build_menu()

    def toggle_monitoring(self, _):
        """Toggle monitoring on/off."""
        if self.is_running:
            self.stop_stream()
            self._waiting_for_reconnect = False
        else:
            self.start_stream()

    def _change_setting(self, attr, value):
        was_running = self.is_running
        if was_running:
            self.stop_stream()
        setattr(self, attr, value)
        if was_running:
            self.start_stream()
        else:
            self.build_menu()

    def show_welcome(self, timer):
        """Show welcome notification pointing to menu bar (fires once on launch)."""
        timer.stop()
        try:
            rumps.notification(
                title=f"{APP_NAME} is running!",
                subtitle="Look for 🎙 in your menu bar",
                message="Click the microphone icon to start monitoring and change settings.",
                sound=False
            )
        except Exception:
            pass  # Notification may fail in some environments, that's ok


    def quit_app(self, _):
        """Quit the application."""
        self.stop_stream()
        # Release lock file
        try:
            fcntl.flock(lock_file_handle, fcntl.LOCK_UN)
            lock_file_handle.close()
            os.remove(LOCK_FILE)
        except Exception:
            pass
        rumps.quit_application()


def run_cli(args):
    """Run in headless CLI mode — stream audio in the terminal."""
    if args.list:
        print(sd.query_devices())
        return

    print(f"Block size: {args.blocksize}")
    print(f"Estimated latency: ~{(args.blocksize / SAMPLERATE) * 1000 * 2:.1f} ms")

    for kind, idx in [("Input", args.input), ("Output", args.output)]:
        if idx is not None:
            print(f"{kind}: {sd.query_devices(idx)['name']}")
        else:
            print(f"{kind}: {sd.query_devices(kind=kind.lower())['name']} (default)")

    print("\nPress Ctrl+C to stop...\n")

    def _cli_passthrough(indata, outdata, _frames, _time, _status):
        try:
            outdata[:] = indata
        except ValueError:
            outdata.fill(0)

    try:
        with sd.Stream(
            device=(args.input, args.output),
            samplerate=SAMPLERATE,
            blocksize=args.blocksize,
            dtype='float32',
            latency='low',
            channels=1,
            callback=_cli_passthrough
        ):
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument('--cli', action='store_true', help='Run in headless CLI mode')
    parser.add_argument('-l', '--list', action='store_true', help='List audio devices')
    parser.add_argument('-i', '--input', type=int, help='Input device index')
    parser.add_argument('-o', '--output', type=int, help='Output device index')
    parser.add_argument('-b', '--blocksize', type=int, default=DEFAULT_BLOCKSIZE)

    args = parser.parse_args()

    if args.cli or args.list:
        run_cli(args)
    else:
        if not ensure_single_instance():
            try:
                rumps.alert(
                    title=f"{APP_NAME} Already Running",
                    message="Look for 🎙 in your menu bar!\n\nThe app is already running. Click the microphone icon to access settings.",
                    ok="Got it!"
                )
            except Exception:
                import subprocess
                subprocess.run(
                    ["osascript", "-e",
                     f'display dialog "{APP_NAME} is already running." buttons {{"OK"}} default button "OK"'],
                    check=False
                )
            sys.exit(0)
        App().run()
