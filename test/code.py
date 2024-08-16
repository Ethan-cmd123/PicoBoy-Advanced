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

from picoboygame import audio, neopixel

audio.mute(False)


sfx_laser = open("sounds/sfx_wpn_laser5.wav", "rb")
data2 = open("sounds/sfx_sounds_impact6.wav", "rb")

print("Test Script")







ledMaxBrightness = 65535

led_red_left = pwmio.PWMOut(board.LED_RED_LEFT)
led_red_right = pwmio.PWMOut(board.LED_RED_RIGHT)
led_green_left = pwmio.PWMOut(board.LED_GREEN_LEFT)
led_green_right = pwmio.PWMOut(board.LED_GREEN_RIGHT)

red_left_level = 0
red_right_level = 0
grn_left_level = 0
grn_right_level = 0



currentTest = 0

def updateLeds():
    global red_left_level, red_right_level, grn_left_level, grn_right_level
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
    
    return red_left_level == 0 and red_right_level == 0 and grn_left_level == 0 and grn_right_level == 0


ledsOff = True

# print("Testing Audio")
# audio.play(sfx_laser)

btnLeftpin = board.BUTTON_LEFT
btnLeft = digitalio.DigitalInOut(btnLeftpin)
btnLeft.direction = digitalio.Direction.INPUT
btnLeft.pull = digitalio.Pull.UP

btnRightpin = board.BUTTON_RIGHT
btnRight = digitalio.DigitalInOut(btnRightpin)
btnRight.direction = digitalio.Direction.INPUT
btnRight.pull = digitalio.Pull.UP

btnUppin = board.BUTTON_UP
btnUp = digitalio.DigitalInOut(btnUppin)
btnUp.direction = digitalio.Direction.INPUT
btnUp.pull = digitalio.Pull.UP

btnDownpin = board.BUTTON_DOWN
btnDown = digitalio.DigitalInOut(btnDownpin)
btnDown.direction = digitalio.Direction.INPUT
btnDown.pull = digitalio.Pull.UP

btnApin = board.BUTTON_X
btnA = digitalio.DigitalInOut(btnApin)
btnA.direction = digitalio.Direction.INPUT
btnA.pull = digitalio.Pull.UP

btnBpin = board.BUTTON_O
btnB = digitalio.DigitalInOut(btnBpin)
btnB.direction = digitalio.Direction.INPUT
btnB.pull = digitalio.Pull.UP






while True:
    keyPressLeft = not btnLeft.value
    keyPressRight = not btnRight.value
    keyPressUp = not btnUp.value
    keyPressDown = not btnDown.value
    keyPressA = not btnA.value
    keyPressB = not btnB.value
    if currentTest == 0:


        ledsOff = updateLeds()
        

        led_red_left.duty_cycle = red_left_level
        led_red_right.duty_cycle = red_right_level
        led_green_left.duty_cycle = grn_left_level
        led_green_right.duty_cycle = grn_right_level
          

        led_red_left.duty_cycle = 8000
        
        time.sleep(0.8)
        
        led_red_left.duty_cycle = 0
        
        time.sleep(0.8)

        led_red_right.duty_cycle = 8000
        
        time.sleep(0.8)
        
        led_red_right.duty_cycle = 0
        
        
        
        
        
        time.sleep(0.8)
        
        
        
        
        
        led_green_left.duty_cycle = 8000
        
        time.sleep(0.8)
        
        led_green_left.duty_cycle = 0
        
        time.sleep(0.8)

        led_green_right.duty_cycle = 8000
        
        time.sleep(0.8)
        
        led_green_right.duty_cycle = 0
        
        
        time.sleep(0.8)
        
        audio.play(sfx_laser)
        
        time.sleep(0.8)
        currentTest +=1
    
    if keyPressLeft or keyPressRight or keyPressUp or keyPressDown or keyPressA or keyPressB:
        audio.play(sfx_laser)

    