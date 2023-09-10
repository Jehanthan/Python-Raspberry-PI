#!/usr/bin/python3

# Original author: M. Heidenreich (c)
# Adapted by: Jehanthan Naraentheraraja, July 29th 2023
# Purpose: Measure distance and sound button

from gpiozero import RGBLED, Button, DistanceSensor, Buzzer
from colorzero import Color
from signal import signal, SIGTERM, SIGHUP, pause
from time import sleep
from threading import Thread

buzzer = Buzzer(17)
button = Button(22)
led = RGBLED(27, 18, 4)
sensor = DistanceSensor(echo=21, trigger=20)
reading = True
buzz = False


def safe_exit(signum, frame):
    exit(1)


def mute_buzzer():
    global buzz
    if buzz:
        buzz = False
    else:
        buzz = True


def read_distance():
    global buzz
    while reading:
        print("Distance: " + '{:1.2f}' .format(sensor.value) + " m")
        if (sensor.value >= 0.2):
            led.color = (0, 1, 0)
            buzzer.off()
        elif (0.05 <= sensor.value < 0.2):
            led.color = (0, 1, 1)
            if not buzz:
                buzzer.beep(on_time=0.05, off_time=0.05, n=1, background=True)
            else:
                buzzer.off()
        else:
            led.color = (1, 0, 0)
            if not buzz:
                buzzer.on()
            else:
                buzzer.off()
        sleep(0.1)


try:

    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    reader = Thread(target=read_distance, daemon=True)
    reader.start()
    sensor.when_in_range = buzzer.on
    sensor.when_out_of_range = buzzer.off

    button.when_pressed = mute_buzzer

    pause()


except KeyboardInterrupt:
    pass


finally:
    reading = False
    sensor.close()
    led.close()
    buzzer.close()

# JN, 2023
