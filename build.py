#!/usr/bin/env -S uv run python
"""Build script — produces dist/<APP_NAME>.app and optionally a DMG."""

import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

from config import APP_NAME

APP  = Path(f"dist/{APP_NAME}.app")
DMG  = Path(f"dist/{APP_NAME}.dmg")
SPEC = Path("build.spec")
TMP_DMG  = Path(f"/tmp/{APP_NAME.lower().replace(' ', '-')}-tmp.dmg")
TMP_MNT  = Path(f"/tmp/{APP_NAME.replace(' ', '')}DMG")

# (pixel_size, iconset_filename) — @2x entries reuse the same rendered PNG
_ICONSET = [
    (16,   "icon_16x16.png"),
    (32,   "icon_16x16@2x.png"),
    (32,   "icon_32x32.png"),
    (64,   "icon_32x32@2x.png"),
    (128,  "icon_128x128.png"),
    (256,  "icon_128x128@2x.png"),
    (256,  "icon_256x256.png"),
    (512,  "icon_256x256@2x.png"),
    (512,  "icon_512x512.png"),
    (1024, "icon_512x512@2x.png"),
]


def run(*args, **kwargs):
    subprocess.run(args, check=True, **kwargs)


def create_icns():
    svg = Path("icons/off.svg")
    with tempfile.TemporaryDirectory() as tmp:
        iconset = Path(tmp) / "AppIcon.iconset"
        iconset.mkdir()
        rendered: dict[int, Path] = {}
        for size, name in _ICONSET:
            if size not in rendered:
                out = iconset / f"_{size}.png"
                run("sips", "-s", "format", "png", "--resampleWidth", str(size),
                    str(svg), "--out", str(out))
                rendered[size] = out
            shutil.copy(rendered[size], iconset / name)
        run("iconutil", "-c", "icns", str(iconset), "-o", "icon.icns")
    print("✓ icon.icns")


def build():
    create_icns()
    shutil.rmtree("dist", ignore_errors=True)

    run("uv", "run", "pyinstaller", str(SPEC))

    # Re-sign with an ad-hoc signature (no Apple Developer account needed).
    # --force : replace the signature PyInstaller already applied
    # --deep  : also signs every framework and binary nested inside the .app
    # --sign -: "-" means ad-hoc — self-consistent, not tied to any identity
    run("codesign", "--force", "--deep", "--sign", "-", str(APP))

    shutil.rmtree("build", ignore_errors=True)
    print(f"✓ Built: {APP}")


def dmg():
    build()

    TMP_DMG.unlink(missing_ok=True)

    run("hdiutil", "create",
        "-size", "80m", "-fs", "HFS+",
        "-volname", APP_NAME,
        "-ov", str(TMP_DMG))

    run("hdiutil", "attach", str(TMP_DMG), "-mountpoint", str(TMP_MNT))

    try:
        shutil.copytree(str(APP), str(TMP_MNT / APP.name))
        (TMP_MNT / "Applications").symlink_to("/Applications")
    finally:
        run("hdiutil", "detach", str(TMP_MNT))

    run("hdiutil", "convert", str(TMP_DMG),
        "-format", "UDZO", "-o", str(DMG), "-ov")

    TMP_DMG.unlink(missing_ok=True)
    print(f"✓ Created: {DMG}")


if __name__ == "__main__":
    if "--dmg" in sys.argv:
        dmg()
    else:
        build()
