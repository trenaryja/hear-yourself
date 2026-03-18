# -*- mode: python ; coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from config import APP_NAME, APP_VERSION, BUNDLE_ID

a = Analysis(
    ['app.py'],
    hiddenimports=['rumps', 'sounddevice', 'numpy', 'pynput'],
    datas=[('icons/*.svg', 'icons')],
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    upx=True,
    console=False,
    icon=['icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    upx=True,
    name=APP_NAME,
)
app = BUNDLE(
    coll,
    name=f'{APP_NAME}.app',
    icon='icon.icns',
    bundle_identifier=BUNDLE_ID,
    info_plist={
        'CFBundleName': APP_NAME,
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundleVersion': APP_VERSION,
        'LSMinimumSystemVersion': '13.0',
        'LSUIElement': True,
        'NSMicrophoneUsageDescription': f'{APP_NAME} needs microphone access to pass audio through to your speakers.',
    },
)
