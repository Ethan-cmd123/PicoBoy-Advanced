import board
import digitalio
from neopixel_write import neopixel_write
import audiocore
import audiopwmio
import time
import ledfx

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

    def mute(self, value=True):
        self.muted = value

class _Buttons:
    def __init__(self):
        self.btnLeftpin = board.BUTTON_LEFT
        self.btnLeft = digitalio.DigitalInOut(btnLeftpin)
        self.btnLeft.direction = digitalio.Direction.INPUT
        self.btnLeft.pull = digitalio.Pull.UP

        self.btnRightpin = board.BUTTON_RIGHT
        self.btnRight = digitalio.DigitalInOut(btnRightpin)
        self.btnRight.direction = digitalio.Direction.INPUT
        self.btnRight.pull = digitalio.Pull.UP

        self.btnUppin = board.BUTTON_UP
        self.btnUp = digitalio.DigitalInOut(btnUppin)
        self.btnUp.direction = digitalio.Direction.INPUT
        self.btnUp.pull = digitalio.Pull.UP

        self.btnDownpin = board.BUTTON_DOWN
        self.btnDown = digitalio.DigitalInOut(btnDownpin)
        self.btnDown.direction = digitalio.Direction.INPUT
        self.btnDown.pull = digitalio.Pull.UP

        self.btnApin = board.BUTTON_X
        self.btnA = digitalio.DigitalInOut(btnApin)
        self.btnA.direction = digitalio.Direction.INPUT
        self.btnA.pull = digitalio.Pull.UP

        self.btnBpin = board.BUTTON_O
        self.btnB = digitalio.DigitalInOut(btnBpin)
        self.btnB.direction = digitalio.Direction.INPUT
        self.btnB.pull = digitalio.Pull.UP

        keyPress = None
    def getKeyPress():
                
        
        keyPressLeft = not self.btnLeft.value
        keyPressRight = not self.btnRight.value
        keyPressUp = not self.btnUp.value
        keyPressDown = not self.btnDown.value
        keyPressA = not self.btnA.value
        keyPressB = not self.btnB.value
        
        if keyPressLeft:
            keyPress = "Left"
        if keyPressRight:
            keyPress = "Right"   
        if keyPressUp:
            keyPress = "Up"
        if keyPressDown:
            keyPress = "Down"
        else:
            keyPress = None
        
        return keyPress
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