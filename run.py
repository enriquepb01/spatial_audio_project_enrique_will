import pyaudio
import sys, time
import numpy as np
import sounddevice as sd
import soundfile as sf
import RPi.GPIO as GPIO

# Get audio file to convolve
convolve_audio_file = 'base_audio.wav'
convolve_audio, freq = sf.read(convolve_audio_file)

# Initiate GPIO for ultrasonic sensor and servo motor
trigger = 18
echo = 24

GPIO.setmode(GPIO.BCM)

GPIO.setup(trigger, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = freq
 
p = pyaudio.PyAudio()

directions = ['W', 'NW', 'N', 'NE', 'E']
 
stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                output = True,
                frames_per_buffer = chunk)

def convolve_hrtf(direction, input_audio, freq):
    L_hrtf_data, _ = sf.read('hrtf_sound_files/L_' + direction + '.wav')
    R_hrtf_data, _ = sf.read('hrtf_sound_files/R_' + direction + '.wav')
    left_audio = np.convolve(input_audio, L_hrtf_data)
    right_audio = np.convolve(input_audio, R_hrtf_data)
    output_audio = np.vstack((left_audio, right_audio)).T
    return(output_audio)

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

current_direction = 0
while True:

    distance = read_ultrasonic_sensor()
    print(distance)

    if distance < 10:
        directional_audio = convolve_hrtf(directions[4], convolve_audio, freq)
        sd.play(directional_audio[:88200], freq)
        sd.wait()
        current_direction = (current_direction+1)%5