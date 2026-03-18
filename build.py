#!/usr/bin/env -S uv run python
"""Build script — produces dist/<APP_NAME>.app and optionally a DMG."""

import sys
import shutil
import subprocess
from pathlib import Path

from config import APP_NAME, APP_VERSION

APP  = Path(f"dist/{APP_NAME}.app")
DMG  = Path(f"dist/{APP_NAME}.dmg")
SPEC = Path(f"{APP_NAME}.spec")
TMP_DMG  = Path(f"/tmp/{APP_NAME.lower().replace(' ', '-')}-tmp.dmg")
TMP_MNT  = Path(f"/tmp/{APP_NAME.replace(' ', '')}DMG")


def run(*args, **kwargs):
    subprocess.run(args, check=True, **kwargs)


def build():
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("dist",  ignore_errors=True)

    run("uv", "run", "pyinstaller", str(SPEC))

    # Re-sign with an ad-hoc signature (no Apple Developer account needed).
    # --force : replace the signature PyInstaller already applied
    # --deep  : also signs every framework and binary nested inside the .app
    # --sign -: "-" means ad-hoc — self-consistent, not tied to any identity
    run("codesign", "--force", "--deep", "--sign", "-", str(APP))

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
