import pyaudio
import sys, time
import numpy as np
import sounddevice as sd
import soundfile as sf
import RPi.GPIO as GPIO

# Get audio file to convolve
convolve_audio_file = 'base_audio.wav'
convolve_audio, freq = sf.read(convolve_audio_file)

# Constant direction arrays
directions = ['W', 'NW', 'N', 'NE', 'E']
angles = [0, 45, 90, 135, 180]

# Initiate GPIO for ultrasonic sensor and servo motor
trigger = 18
echo = 24
servo = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(trigger, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
GPIO.setup(servo, GPIO.OUT)
pwm = GPIO.PWM(servo, 50)

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

# Move the servo to the appropriate angle
def set_servo_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(servo, True)
    pwm.ChangeDutyCycle(duty)

current_direction = 0
while True:
    set_servo_angle(angles[current_direction])
    distance = read_ultrasonic_sensor()
    print(distance)

    if distance < 10:
        directional_audio = convolve_hrtf(directions[current_direction], convolve_audio, freq)
        sd.play(directional_audio[:88200], freq)
        sd.wait()
    else:
        current_direction = (current_direction+1)%5

