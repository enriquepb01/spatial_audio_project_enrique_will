import pyaudio
import sys, time
import numpy as np
import sounddevice as sd
import soundfile as sf
import math
import numpy as np

# Get audio file to convolve
convolve_audio_file = 'base_audio.wav'
convolve_audio, freq = sf.read(convolve_audio_file)

# Audio stream setup
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = freq
p = pyaudio.PyAudio()
stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                output = True,
                frames_per_buffer = chunk)

exp_scale = [math.exp(3*x) for x in np.linspace(-0.9,-0.05,10)]

for volume in exp_scale:
	print(volume)
	sd.play(volume * convolve_audio[:88200], freq)
	sd.wait()
