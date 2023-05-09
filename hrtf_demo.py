import pyaudio
import sys, time
import numpy as np
import sounddevice as sd
import soundfile as sf
import RPi.GPIO as GPIO
from gpiozero import AngularServo

# Get audio file to convolve
convolve_audio_file = 'base_audio.wav'
convolve_audio, freq = sf.read(convolve_audio_file)

# Constant direction arrays
directions = ['W', 'NW', 'N', 'NE', 'E']
angles = [-90, -45, 0, 45, 90]

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

# Convolve audio to get directional audio
def convolve_hrtf(direction, input_audio, freq):
    L_hrtf_data, _ = sf.read('hrtf_sound_files/L_' + direction + '.wav')
    R_hrtf_data, _ = sf.read('hrtf_sound_files/R_' + direction + '.wav')
    left_audio = np.convolve(input_audio, L_hrtf_data)
    right_audio = np.convolve(input_audio, R_hrtf_data)
    output_audio = np.vstack((left_audio, right_audio)).T
    return(output_audio)

current_direction = 0
for direction in directions:
	directional_audio = convolve_hrtf(direction, convolve_audio, freq)
	sd.play(directional_audio[:88200], freq)
	sd.wait()

for direction in reversed(directions):
	directional_audio = convolve_hrtf(direction, convolve_audio, freq)
	sd.play(directional_audio[:88200], freq)
	sd.wait()
