#!/usr/bin/python3

# Program: LNX255 Project 03
# Student: AS
# Date: April, 2023

from gpiozero import PWMLED, Button
from smbus import SMBus
from signal import pause, signal, SIGTERM, SIGHUP
from time import sleep
from threading import Thread
from rpi_lcd import LCD
from math import log10

delay = 0.1
speed = 5
active = True

leds = (PWMLED(12), PWMLED(6), PWMLED(26), PWMLED(19), PWMLED(21))

button = Button(20)

lcd = LCD()

steps = 255
fade_factor = (steps * log10(2))/(log10(steps))
bus = SMBus(1)


def cleanup(signum, frame):
    exit(1)


ads7830_commands = (0x84, 0xc4, 0x94, 0xd4, 0xa4, 0xe4, 0xb4, 0xf4)


def read_ads7830(input):
    bus.write_byte(0x4b, ads7830_commands[input])
    return bus.read_byte(0x4b)


def brightness(input):
    value = read_ads7830(input)
    return (pow(2, (value/fade_factor))-1)/steps


def change_speed():
    global delay
    global speed

    speed -= 1
    if speed < 1:
        speed = 5

    delay = 0.6 - (speed * 0.1)


def update_lcd():
    try:
        while active:
            brightness_amount = int(brightness(0) * 100)
            lcd.text("Speed: {}%".format(int(speed / 5 * 100)), 1)
            lcd.text("Brightness: {}%".format(brightness_amount), 2)
            sleep(0.1)

    except AttributeError:
        pass


def show_pattern():
    try:
        while active:
            for num in (0, 1, 2, 3, 4, 3, 2, 1):
                leds[num].value = brightness(0)
                sleep(delay)
                leds[num].off()

    except AttributeError:
        pass


try:
    signal(SIGTERM, cleanup)
    signal(SIGHUP, cleanup)

    button.when_pressed = change_speed

    pattern_thread = Thread(target=show_pattern, daemon=True)
    lcd_thread = Thread(target=update_lcd, daemon=True)

    pattern_thread.start()
    lcd_thread.start()
    lcd.text("Speed: {}%".format(int(speed / 5 * 100)), 1)
    lcd.text("Brightness: {}%".format(int(brightness(0) * 100)), 2)

    pause()

except KeyboardInterrupt:
    pass

finally:
    active = False
    pattern_thread.join()
    lcd_thread.join()
    lcd.clear()
    for led in leds:
        led.close()
    sleep(0.25)
