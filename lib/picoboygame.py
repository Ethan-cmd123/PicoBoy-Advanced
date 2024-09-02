import board
import digitalio
from neopixel_write import neopixel_write
import audiocore
import audiopwmio
import time
import ledfx

import digitalio
from digitalio import DigitalInOut, Direction, Pull
import displayio

from terminalio import FONT as font
from adafruit_display_text import label
#from adafruit_display_shapes.rect import Rect
#from adafruit_display_shapes.circle import Circle
#from adafruit_display_shapes.triangle import Triangle

import vectorio
from vectorio_helpers import rotated_polygon
from vectorio_helpers import line

from adafruit_display_shapes.sparkline import Sparkline


import pwmio

MAX_LED_BRIGHTNESS = 65535
LED_BRIGHTNESS_CORRECTION = 1.4


class _Neopixel:
    def __init__(self, pin):
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.OUTPUT
        neopixel_write(self.pin, bytearray([2,2,2]))
        
    def color(self,colour):
        self.colour(colour)
        
    def colour(self,colour):
        neopixel_write(self.pin, bytearray(colour))

class _Audio:
    last_audio = None

    def __init__(self, speaker_pin):
        self.muted = True
        self.buffer = bytearray(1024)
        self.audio = audiopwmio.PWMAudioOut(speaker_pin)

    def play(self, audio_file, loop=False):
        if self.muted:
            return
        self.stop()
        wave = audiocore.WaveFile(audio_file, self.buffer)
        self.audio.play(wave, loop=loop)

    def stop(self):
        self.audio.stop()
        
    def playing(self):
        self.audio.playing

    def mute(self, value=True):
        self.muted = value

class _Buttons:
    def updateButton():
        global btnLeft, btnRight, btnUp, btnDown,btnA, btnB
        
        btnLeft = None
        btnRight = None
        btnUp = None
        btnDown = None
        btnA = None
        btnB = None

        
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
    def getKeyPress(PromptedKey):
                
        
        keyPressLeft = not btnLeft.value
        keyPressRight = not btnRight.value
        keyPressUp = not btnUp.value
        keyPressDown = not btnDown.value
        keyPressA = not btnA.value
        keyPressB = not btnB.value
        
        if PromptedKey == "Left":
            return keyPressLeft
        if PromptedKey == "Right":
            return keyPressRight
        if PromptedKey == "Up":
            return keyPressUp
        if PromptedKey == "Down":
            return keyPressDown
        if PromptedKey == "A":
            return keyPressA
        if PromptedKey == "B":
            return keyPressB
'''
class _LEDS:
    def __init__(self):
        pass
        #self.left_red = _LED(board.LED_RED_LEFT, 'red', 'left')
        #self.right_red = _LED(board.LED_RED_RIGHT, 'red', 'right')
        #self.left_green = _LED(board.LED_GREEN_LEFT, 'green', 'left')
        #self.right_green = _LED(board.LED_GREEN_RIGHT, 'green', 'right')
        
    def update(self):
        for led in self.leds:
            pass
'''       

display = board.DISPLAY
audio = _Audio(board.SPEAKER)
neopixel = _Neopixel(board.NEOPIXEL)
button = _Buttons