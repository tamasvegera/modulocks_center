#!/bin/python3

import os
import serial
import subprocess
import time
import RPi.GPIO as GPIO

background_music="/home/pi/background_music.mp3"
main_sound_dir = "/home/pi/"

fade_out_time = 0.01	    # not exact timing
low_background_volume = 50	# background music volume when playing an effect
current_vol = 100

port = serial.Serial(baudrate=9600, bytesize=8, parity=serial.PARITY_NONE, port="/dev/serial0", rtscts=0, xonxoff=0, stopbits=1, timeout=None)

background = subprocess.Popen(['mplayer', '-slave', '-channels' , '6', '-ao', 'pulse', '-quiet', '-loop', '0', background_music], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)

def background_fade_out():
    global current_vol

    while current_vol>low_background_volume:
        current_vol-=5
        if current_vol < low_background_volume:
            current_vol = low_background_volume

        command = "volume " + str(current_vol)+ " 100\r\n"
        background.stdin.write(command.encode("UTF-8"))
        background.stdin.flush()

def background_fade_in():
    global current_vol

    while current_vol<100:
        current_vol+=5
        if current_vol > 100:
            current_vol = 100

        command = "volume " + str(current_vol) + " 100\r\n"
        background.stdin.write(command.encode("UTF-8"))
        background.stdin.flush()
        #time.sleep(fade_out_time/(100-low_background_volume))
	
def play(item):
    background_fade_out()
    os.system("mplayer -ao pulse -volume 100 -channels 6 " + main_sound_dir + item + " -quiet -slave 2> /dev/null")
    background_fade_in()
    print('--> done')

message = "Test\n"
port.write(message.encode())

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, GPIO.HIGH)

while True:
    item = port.readline().decode('ascii').rstrip()
    print(item)
    play(item)
