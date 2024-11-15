#!/usr/bin/env python3
import colorsys
import time

import ioexpander as io

from  rpi_backlight import Backlight

I2C_ADDR = 0x0F  # 0x18 for IO Expander, 0x0F for the encoder breakout

PIN_RED = 1
PIN_GREEN = 7
PIN_BLUE = 2

POT_ENC_A = 12
POT_ENC_B = 3
POT_ENC_C = 11

BRIGHTNESS = 1.0                # Effectively the maximum fraction of the period that the LED will be on
PERIOD = int(100 / BRIGHTNESS)  # Add a period large enough to get 0-255 steps at the desired brightness

ioe = io.IOE(i2c_addr=I2C_ADDR, interrupt_pin=4)

# Swap the interrupt pin for the Rotary Encoder breakout
if I2C_ADDR == 0x0F:
    ioe.enable_interrupt_out(pin_swap=True)

ioe.setup_rotary_encoder(1, POT_ENC_A, POT_ENC_B, pin_c=POT_ENC_C)

ioe.set_pwm_period(PERIOD)
ioe.set_pwm_control(divider=2)  # PWM as fast as we can to avoid LED flicker

ioe.set_mode(PIN_RED, io.PWM, invert=True)
ioe.set_mode(PIN_GREEN, io.PWM, invert=True)
ioe.set_mode(PIN_BLUE, io.PWM, invert=True)

count = 0
r, g, b = 0, 0, 0

backlight = Backlight()

while True:
    brightness = backlight.brightness
    
    if ioe.get_interrupt():
        old_count = count
        count = ioe.read_rotary_encoder(1)
        ioe.clear_interrupt()
        if count - old_count > 0:
            brightness = min(100, brightness + 3)
        if count - old_count < 0:
            brightness = max(0, brightness - 3)
        backlight.brightness = brightness

    r = (int)(255 * ((100 - brightness)/100))
    b = (int)(255 * (brightness/100))
    ioe.output(PIN_RED, r)
    ioe.output(PIN_GREEN, 0)
    ioe.output(PIN_BLUE, b)

    time.sleep(1.0 / 30)
