#!/usr/bin/python3
# Original Author: M.Heinderich
# Adapted By: Jehanthan Naraentheraraja

from smbus import SMBus
from signal import signal, SIGTERM, SIGHUP, pause
from gpiozero import LED, PWMLED, Button
from threading import Thread
from time import sleep
from random import randrange
from rpi_lcd import LCD
from math import log10

patterns = (
                [1, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 1, 0, 1, 0, 1, 0],
                [1, 1, 0, 1, 1, 0, 1, 1],
                [1, 1, 1, 0, 1, 1, 1, 0],
           )


leds = (PWMLED(16), PWMLED(21), PWMLED(20), PWMLED(12),
        PWMLED(22), PWMLED(13), PWMLED(27), PWMLED(17))
button = Button(23)
lcd = LCD()
bus = SMBus(1)

is_running = True
is_showing = True
delay = 0.1

index = 0
led_in = 7
led_out = 0
counter = 1
steps = 255
fade_factor = (steps * log10(2)) / (log10(steps))


def safe_exit(signum, frame):
    exit(1)


ads7830_commands = [0x84, 0xc4, 0x94, 0xd4, 0xa4, 0xe4, 0xb4, 0xf4]


def read_ads7830(input):
    bus.write_byte(0x4b, ads7830_commands[input])
    return bus.read_byte(0x4b)


def speed_adjust():
    global delay
    while is_running:
        value = read_ads7830(input)
        delay = 0.2+0.04*value/255

        for id in range(8):
            leds[id].value = patterns[index][id]*brightness

        sleep(delay)


def brightness_adjust():
    global brightness
    while is_running:
        value = read_ads7830(input)
        brightness = (pow(2, (value / fade_factor)) - 1) / steps
        sleep(0.1)


def pattern():
    while is_running:
        token = patterns[index].pop(led_out)
        patterns[index].insert(led_in, token)


def change_direction():
    global led_in, led_out, index, counter

    led_in, led_out = led_out, led_in
    while True:
        new_index = randrange(0, len(patterns))
        counter += 1
        if new_index != index:
            index = new_index
            sleep(0.1)
            break


def show_display():
    global counter

    while is_showing:
        if(counter % 2) == 0:
            lcd.text(f"Pattern: {index+5}/8 <<", 1)
        else:
            lcd.text(f"Pattern: {index+1}/8 >>", 1)
            sleep(0.25)

        display.text(f"B:{brightness*100:3.0f}% D:{delay:2.2f}s", 2)


try:

    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    button.when_pressed = change_direction
    index = randrange(0, len(patterns))

    getPattern = Thread(target=pattern, daemon=True)
    getPattern.start()

    worker = Thread(target=speed_adjust, daemon=True)
    worker.start()

    brightnessLevel = Thread(target=brightness_adjust, daemon=True)
    brightnessLevel.start()

    display = Thread(target=show_display, daemon=True)
    display.start()

    pause()

except KeyboardInterrupt:
    pass

finally:
    is_running = False
    worker.join()

    is_showing = False
    sleep(0.5)
    lcd.clear()

    for id in range(8):
        leds[id].close()
