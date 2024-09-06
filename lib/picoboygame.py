import board
import digitalio
from neopixel_write import neopixel_write
import audiocore
import audiopwmio
import time
import ledfx
import math
import digitalio
from digitalio import DigitalInOut, Direction, Pull
import displayio

from terminalio import FONT as font
from adafruit_display_text import label
#from adafruit_display_shapes.rect import Rect
#from adafruit_display_shapes.circle import Circle
#from adafruit_display_shapes.triangle import Triangle
import random

import vectorio
from vectorio_helpers import rotated_polygon
from vectorio_helpers import line

from adafruit_display_shapes.sparkline import Sparkline


import pwmio

MAX_LED_BRIGHTNESS = 65535
LED_BRIGHTNESS_CORRECTION = 1.4



class PhysicsShape:
    def __init__(self, points, x,y, initvx=0.0, initvy=0.0, initva=0.0, vmax=3,screen=None):
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF  # White
        self.shape=rotated_polygon.RotatedPolygon(pixel_shader=color_palette, points=points, x=x, y=y, rotation=0)
        self.screen=screen
        screen.append(self.shape)
        self.init_x, self.init_y = float(x),float(y)
        self.x, self.y = float(x),float(y)
        self.vx,self.vy, self.va = initvx,initvy,initva
        self.vmax=vmax
    def rotate(self, angle):
        self.shape.rotation+=angle
    def rotation(self, angle):
        self.shape.rotation=angle
    def accelerate(self, amount, angle=None):
        if not angle:
            angle=self.shape.rotation
        self.vx = -max(min(self.vx + (math.sin(math.radians(angle)) * amount), self.vmax),-self.vmax)
        self.vy = -max(min(self.vy - (math.cos(math.radians(angle)) * amount), self.vmax),-self.vmax)
    def bbox(self, relative=False):
        minX, minY, maxX, maxY = 128, 64, 0, 0
        for px,py in self.shape[0].points:
            if px < minX:
                minX=px
            if py < minY:
                minY=py
            if px > maxX:
                maxX=px
            if py > maxY:
                maxY=py
        if relative:
            return [(minX, minY), (maxX, maxY)]
        return [(int(self.x)+minX, int(self.y)+minY), (int(self.x)+maxX, int(self.y)+maxY)]

    def collidesWith(self, shape):
        r1min,r1max=self.bbox()
        r2min,r2max=shape.bbox()
        
        return r1max[0] >= r2min[0] and r1min[0]<=r2max[0] and r1max[1] >= r2min[1] and r1min[1]<=r2max[1]
    def screenWrap(self):
        if int(self.x) < 0:
            self.x = 127
        if int(self.x) > 127:
            self.x = 0
        if int(self.y) < 0:
            self.y=63
        if int(self.y) > 63:
            self.y=0
        self.updateShapePos()
    def updatePosition(self):
        self.x+=self.vx
        self.y+=self.vy
        self.updateShapePos()
        self.rotate(self.va)
    def updateShapePos(self):
        self.shape.x=int(self.x - self.init_x)
        self.shape.y=int(self.y - self.init_y)
        
class Rok(PhysicsShape):
    roks = []
    
    def __init__(self,x,y, minRadius=11,maxRadius=15, initvx=0.0, initvy=0.0, initva=0.0, vmax=3,screen=None):
        points=generateAstroidPoly(minRadius, maxRadius)
        super().__init__(points, x,y, initvx, initvy, initva, vmax,screen)
        self.screen=screen
        self.minRadius=minRadius
        self.maxRadius=maxRadius
    def smash(self, impact_vx, impact_vy, roks):
        if self.minRadius//2 > 1:
            new_va = self.va + random.randint(0,2)
            roks.append(Rok(int(self.x), int(self.y), minRadius=self.minRadius//2,maxRadius=self.maxRadius//2, initvx=impact_vx+self.vx, initvy=impact_vy-self.vy, initva=new_va, screen=self.screen))
            new_va = self.va - random.randint(0,2)
            roks.append(Rok(int(self.x), int(self.y), minRadius=self.minRadius//2,maxRadius=self.maxRadius//2, initvx=impact_vx+self.vx, initvy=impact_vy-self.vy, initva=new_va, screen=self.screen))
        self.annihilated(roks)
    def annihilated(self, roks):
        self.shape.pop()
        self.screen.remove(self.shape)
        roks.remove(self)
def generateAstroidPoly(minRadius, maxRadius, segments=8):
    seg=[random.random() for _ in range(segments)]
    seg.sort()
    return [pointOnCircle(_,random.randint(minRadius,maxRadius)) for _ in seg]
    

def pointOnCircle(angle, radius):
    x = int(math.cos(2 * math.pi * angle) * radius)
    y = int(math.sin(2 * math.pi * angle) * radius)
    return (x,y)

class Bullet(PhysicsShape):
    def __init__(self,x,y, size=1, initvx=0.0, initvy=0.0, initva=0.0, vmax=3,screen=None):
        points=createBullet(size)
        super().__init__(points, x,y, initvx, initvy, initva,vmax,screen)
        self.screen=screen
        self.size=size
def createBullet(size):
    return [(0,1),(2,0),(0,4)]


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