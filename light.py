#!/usr/bin/python3

# Original Author: M Heidenreich
# Adapted By: Justin B, Jehanthan N

from smbus import SMBus
from gpiozero import PWMLED, Button
from gpiozero.pins.pigpio import PiGPIOFactory
from signal import signal, SIGTERM, SIGHUP, pause
from time import sleep
from math import log10

remote_host = PiGPIOFactory(host="raspberrypi-66.local")

bus = SMBus(1)
light = PWMLED(26, pin_factory=remote_host)
button = Button(20)
steps = 255
fade_factor = (steps * log10(2)) / (log10(steps))


def safe_exit(sig_num, frame):
    exit(1)


ads7830_commands = [0x84, 0xc4, 0x94, 0xd4, 0xa4, 0xe4, 0xb4, 0xf4]


def read_ads7830(input):
    bus.write_byte(0x4b, ads7830_commands[input])
    return bus.read_byte(0x4b)


def values(input):
    while True:
        value = read_ads7830(input)
        yield (pow(2, (value/fade_factor))-1)/steps


def toggle_light():
    if light.source:
        light.source = None
        light.off()
    else:
        light.source = values(0)


try:

    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    button.when_pressed = toggle_light

    light.source_delay = 0.02

    pause()

except KeyboardInterrupt:
    pass

finally:
    light.close()

# JB, JN
