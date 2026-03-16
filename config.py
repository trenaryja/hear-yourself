APP_NAME = "Hear Yourself"
APP_VERSION = "1.0.0"
GITHUB_URL = "github.com/gabrycina/hear-yourself"
BUNDLE_ID_PREFIX = "com.gabrycina"

APP_NAME_SLUG = APP_NAME.lower().replace(" ", "")
BUNDLE_ID = f"{BUNDLE_ID_PREFIX}.{APP_NAME_SLUG}"

# Frames per audio buffer. Directly controls latency: latency ≈ (blocksize / samplerate) * 2.
# Lower = less delay, but more CPU pressure per second (more frequent callbacks).
# Values: 8, 16, 32, 64, 128, 256, 512, 1024. Must be a power of 2.
# 32 is ideal for Apple Silicon. Intel Macs may need 64-128.
DEFAULT_BLOCKSIZE = 32

# Audio sample rate in Hz. Must match a rate supported by your audio hardware.
# Common values: 44100 (CD quality), 48000 (standard), 96000 (high-res).
# Higher rates increase CPU load proportionally. 48000 is the macOS default.
DEFAULT_SAMPLERATE = 48000

# Number of audio channels. 1 = mono (mic input is inherently mono),
# 2 = stereo (duplicates mono to both ears, or passes stereo if available).
DEFAULT_CHANNELS = 1

LATENCY_PRESETS = [
    (16,  "Extreme (~0.7ms)"),
    (32,  "Ultra Low (~1.3ms)"),
    (64,  "Low (~2.7ms)"),
    (128, "Normal (~5.3ms)"),
    (256, "High (~10.7ms)"),
]


def audio_callback(indata, outdata, frames, time, status):
    """Direct passthrough callback — copies input buffer to output buffer.
    Called by sounddevice on a real-time audio thread. Must be fast (<1ms).
    The status param flags glitches (input_overflow, output_underflow, etc.)."""
    if status:
        import sys
        print(status, file=sys.stderr)
    outdata[:] = indata
