# Adapting the example in https://learn.adafruit.com/adafruit-oled-featherwing/python-usage
# to use with Raspberry Pi Pico and CircuitPython

import board
import gc
import time
import random
import busio
import digitalio
import displayio
from terminalio import FONT as font
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
#import adafruit_displayio_sh1106
import adafruit_displayio_ssd1305
from adafruit_display_shapes.sparkline import Sparkline
from neopixel_write import neopixel_write

import pwmio

import audiocore
import audiopwmio


neopixel_pin = digitalio.DigitalInOut(board.NEOPIXEL)
neopixel_pin.direction = digitalio.Direction.OUTPUT

neopixel_write(neopixel_pin, bytearray([2,2,2]))

def main():
    data = open("sfx_sounds_impact6.wav", "rb")
    wav = audiocore.WaveFile(data)
    print(wav.sample_rate)
    audio = audiopwmio.PWMAudioOut(board.GP9)
    
    led_red_left = pwmio.PWMOut(board.GP10)
    led_red_right = pwmio.PWMOut(board.GP13)
    led_green_left = pwmio.PWMOut(board.GP11)
    led_green_right = pwmio.PWMOut(board.GP12)
    red_left_level = 0
    red_right_level = 0
    grn_left_level = 0
    grn_right_level = 0
    with busio.I2C(scl=board.GP5, sda=board.GP4) as i2c: # This RPi Pico way to call I2C
        display_bus = displayio.I2CDisplay(i2c, device_address = 0x3C) # The address of my Board

        display = adafruit_displayio_ssd1305.SSD1305(display_bus, width=128, height=64)
        splash = displayio.Group()
        display.root_group=splash

        color_bitmap = displayio.Bitmap(128, 64, 1) # Full screen white
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF  # White
         
#         bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
#         splash.append(bg_sprite)
         
        # Draw a smaller inner rectangle
#         inner_bitmap = displayio.Bitmap(124, 60, 1)
#         inner_palette = displayio.Palette(1)
#         inner_palette[0] = 0x000000  # Black
#         inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=2, y=2)
#         splash.append(inner_sprite)
         
        rect = Rect(0, 0, 128, 64, fill=0, outline=0xFFFFFF)
        splash.append(rect)
        
        circle_radius = 5
        circle = Circle(32, 32, circle_radius, fill=0, outline=0xFFFFFF)
        splash.append(circle)
        
         
        # Draw a label
        text = "Nicolau dos"
        text_area = label.Label(font, text=text, color=0xFFFF00, x=28, y=15)
        #splash.append(text_area)

        text = "Brinquedos"
        text_area = label.Label(font, text=text, color=0xFFFF00, x=32, y=25)
        #splash.append(text_area)
         
        # Define Circle Animation Steps
        delta_x = 2
        delta_y = 2
        # Start the main loop
        while True:
            red_left_level -= 1024*4
            if red_left_level <= 0:
                red_left_level = 0
            red_right_level -= 1024*4
            if red_right_level <= 0:
                red_right_level = 0
            grn_left_level -= 1024*4
            if grn_left_level <= 0:
                grn_left_level = 0
            grn_right_level -= 1024*4
            if grn_right_level <= 0:
                grn_right_level = 0
            
            led_red_left.duty_cycle = red_left_level
            led_red_right.duty_cycle = red_right_level
            led_green_left.duty_cycle = grn_left_level
            led_green_right.duty_cycle = grn_right_level
            
            if circle.y + circle_radius >= display.height - circle_radius:
                delta_y = -2
                audio.play(wav)
                audio.play(wav)
                grn_left_level = 65535
            if circle.y - circle_radius <= 0 - circle_radius:
                delta_y = 2
                audio.play(wav)
                audio.play(wav)
                grn_right_level = 65535
            
            if circle.x - circle_radius <= 0 - circle_radius:
                delta_x = 2
                audio.play(wav)
                audio.play(wav)
                red_left_level = 65535
            if circle.x + circle_radius >= display.width - circle_radius:
                delta_x = -2
                audio.play(wav)
                audio.play(wav)
                red_right_level = 65535
            

            circle.x = circle.x + delta_x
            circle.y = circle.y + delta_y

            time.sleep(0.02)
            gc.collect()
    
try:
    main()
finally:
    displayio.release_displays()
    print("exiting ...")

