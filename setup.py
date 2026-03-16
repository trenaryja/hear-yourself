"""
Setup script for building the app as a standalone macOS application.
"""

from setuptools import setup
from config import APP_NAME, APP_VERSION, BUNDLE_ID

APP = ['app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleIdentifier': BUNDLE_ID,
        'CFBundleVersion': APP_VERSION,
        'CFBundleShortVersionString': APP_VERSION,
        'LSMinimumSystemVersion': '10.13',
        'LSUIElement': True,  # Menu bar app, no dock icon
        'NSHighResolutionCapable': True,
        'NSMicrophoneUsageDescription': f'{APP_NAME} needs microphone access to pass audio through to your speakers.',
    },
    'packages': ['rumps', 'sounddevice', 'numpy'],
}

setup(
    app=APP,
    name=APP_NAME,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
