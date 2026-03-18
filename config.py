APP_NAME = "Hear Yourself"
APP_VERSION = "1.0.0"
GITHUB_URL = "github.com/gabrycina/hear-yourself"
BUNDLE_ID_PREFIX = "com.gabrycina"

APP_NAME_SLUG = APP_NAME.lower().replace(" ", "")
BUNDLE_ID = f"{BUNDLE_ID_PREFIX}.{APP_NAME_SLUG}"

# Frames per audio buffer. Directly controls latency: latency ≈ (blocksize / samplerate) * 2.
# Lower = less delay, but more CPU pressure per second (more frequent callbacks).
# Values: 8, 16, 32, 64, 128, 256, 512, 1024. Must be a power of 2.
# 32 is ideal for Apple Silicon.
DEFAULT_BLOCKSIZE = 32


SAMPLERATE = 48000

def _latency_label(name, blocksize):
    ms = (blocksize / SAMPLERATE) * 2 * 1000
    return (blocksize, f"{name} (~{ms:.1f}ms)" if ms < 1000 else f"{name} (~{ms / 1000:.1f}s)")

LATENCY_PRESETS = [
    _latency_label("Extreme", 32),
    _latency_label("Low", 64),
    _latency_label("Test", 16384),
]
