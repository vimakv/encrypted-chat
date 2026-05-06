# =========================
# voice_utils.py
# =========================

import sounddevice as sd
from scipy.io.wavfile import write
import os

VOICE_FOLDER = "voice_notes"


# RECORD VOICE
def record_voice(
    filename="voice.wav",
    seconds=5
):

    fs = 44100

    recording = sd.rec(
        int(seconds * fs),
        samplerate=fs,
        channels=2
    )

    sd.wait()

    path = os.path.join(
        VOICE_FOLDER,
        filename
    )

    write(
        path,
        fs,
        recording
    )

    return path