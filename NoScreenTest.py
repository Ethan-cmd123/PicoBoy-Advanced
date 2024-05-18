import board
import gc
import time
import random
import busio
import digitalio
import displayio
import board
import synthio
import audiopwmio


import pwmio

import audiocore
import audiopwmio



led_red_left = pwmio.PWMOut(board.GP10)
led_red_right = pwmio.PWMOut(board.GP13)
led_green_left = pwmio.PWMOut(board.GP11)
led_green_right = pwmio.PWMOut(board.GP12)
red_left_level = 0
red_right_level = 0
grn_left_level = 0
grn_right_level = 0

dac = audiopwmio.PWMAudioOut(board.GP9)

melody = synthio.MidiTrack(b"\0\x90H\0*\x80H\0\6\x90J\0*\x80J\0\6\x90L\0*\x80L\0\6\x90J\0" +
                           b"*\x80J\0\6\x90H\0*\x80H\0\6\x90J\0*\x80J\0\6\x90L\0T\x80L\0" +
                           b"\x0c\x90H\0T\x80H\0\x0c\x90H\0T\x80H\0", tempo=320)
while True:
    dac.play(melody)
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
    
    grn_left_level = 65535

    grn_right_level = 65535

    red_left_level = 65535
    
    red_right_level = 65535

    time.sleep(0.02)
    gc.collect()