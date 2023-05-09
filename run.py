import pyaudio
import sys, time
import numpy as np
import sounddevice as sd
import soundfile as sf
import RPi.GPIO as GPIO
from gpiozero import AngularServo
import math

# Get audio file to convolve
convolve_audio_file = 'base_audio.wav'
convolve_audio, freq = sf.read(convolve_audio_file)

# Constant direction arrays
directions = ['W', 'NW', 'N', 'NE', 'E']
angles = [90, 45, 0, -45, -90]

# Initiate GPIO for ultrasonic sensor and servo motor
trigger = 18
echo = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(trigger, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
servo = AngularServo(23, min_pulse_width=0.0006, max_pulse_width=0.0023)

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

# Read distance from ultrasonic sensor
def read_ultrasonic_sensor():
    GPIO.output(trigger, True)
    time.sleep(0.00001)
    GPIO.output(trigger, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(echo) == 0:
        start_time = time.time()

    while GPIO.input(echo) == 1:
        stop_time = time.time()
    
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2
    return distance

# Maps distances (5-120) to volume (0-1, exponential)    
def select_volume(distance):
    scaled_distance = np.interp(distance, [5, 120], [0.05, 0.9])
    volume = math.exp(-3*scaled_distance)
    return volume

current_direction = 0
while True:
    servo.angle = angles[current_direction]
    time.sleep(1)
    distance = read_ultrasonic_sensor()
    print(distance)

    if distance < 120:
        directional_audio = convolve_hrtf(directions[current_direction], convolve_audio, freq)
        volume = select_volume(distance)
        sd.play(volume*directional_audio[:88200], freq)
        sd.wait()
    else:
        current_direction = (current_direction+1)%5

