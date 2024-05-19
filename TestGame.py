# Adapting the example in https://learn.adafruit.com/adafruit-oled-featherwing/python-usage
# to use with Raspberry Pi Pico and CircuitPython
import math
import analogio
import board
import gc
import time
import random
import busio
import digitalio
from digitalio import DigitalInOut, Direction, Pull
import displayio
from neopixel_write import neopixel_write
from terminalio import FONT as font
from adafruit_display_text import label
#from adafruit_display_shapes.rect import Rect
#from adafruit_display_shapes.circle import Circle
#from adafruit_display_shapes.triangle import Triangle

import adafruit_displayio_ssd1305

import vectorio
from vectorio_helpers import rotated_polygon
from vectorio_helpers import line

from adafruit_display_shapes.sparkline import Sparkline
import synthio
import audiopwmio
import microcontroller

import supervisor

import pwmio

import audiocore
import audiopwmio

display=None

x_axis_pin = analogio.AnalogIn(board.A0)
y_axis_pin = analogio.AnalogIn(board.A1)

neopixel_pin = digitalio.DigitalInOut(board.NEOPIXEL)
neopixel_pin.direction = digitalio.Direction.OUTPUT

neopixel_write(neopixel_pin, bytearray([2,2,2]))

class PhysicsShape:
    def __init__(self, points, x,y, initvx=0.0, initvy=0.0, initva=0.0, vmax=3,screen=None):
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
    def __init__(self,x,y, minRadius=11,maxRadius=15, initvx=0.0, initvy=0.0, initva=0.0, vmax=3,screen=None):
        points=generateAstroidPoly(minRadius, maxRadius)
        super().__init__(points, x,y, initvx, initvy, initva, vmax,screen)
        self.screen=screen
        self.minRadius=minRadius
        self.maxRadius=maxRadius
    def smash(self, impact_vx, impact_vy):
        if self.minRadius//2 > 1:
            new_va = self.va + random.randint(0,2)
            roks.append(Rok(int(self.x), int(self.y), minRadius=self.minRadius//2,maxRadius=self.maxRadius//2, initvx=impact_vx+self.vx, initvy=impact_vy-self.vy, initva=new_va, screen=self.screen))
            new_va = self.va - random.randint(0,2)
            roks.append(Rok(int(self.x), int(self.y), minRadius=self.minRadius//2,maxRadius=self.maxRadius//2, initvx=impact_vx+self.vx, initvy=impact_vy-self.vy, initva=new_va, screen=self.screen))
        self.annihilated()
    def annihilated(self):
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
        points=creatBullet(size)
        super().__init__(points, x,y, initvx, initvy, initva,vmax,screen)
        self.screen=screen
        self.size=size
def creatBullet(size):
    return [(0,1),(2,0),(0,4)]
        
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

roks=[]
data = open("sounds/sfx_movement_jump1.wav", "rb")
data2 = open("sounds/sfx_sounds_impact6.wav", "rb")

wav = audiocore.WaveFile(data)
wav2 = audiocore.WaveFile(data2)
a = audiopwmio.PWMAudioOut(board.GP9)


def main():
    with busio.I2C(scl=board.GP5, sda=board.GP4) as i2c: # This RPi Pico way to call I2C
        global display
        display_bus = displayio.I2CDisplay(i2c, device_address = 0x3C) # The address of my Board

        # Display RAM is 132 pixels wide, but physical display is 128 pixels wide 
        display = adafruit_displayio_ssd1305.SSD1305(display_bus, width=128, height=64)
        # Display seems to be offset by 2 pixel
        splash = displayio.Group()
        display.root_group=splash
        
        print(display)
        
        
        led_red_left = pwmio.PWMOut(board.GP10)
        led_red_right = pwmio.PWMOut(board.GP13)
        led_green_left = pwmio.PWMOut(board.GP11)
        led_green_right = pwmio.PWMOut(board.GP12)
        
        leftBTNpin = board.GP3
        leftBTN = digitalio.DigitalInOut(leftBTNpin)
        leftBTN.direction = digitalio.Direction.INPUT
        leftBTN.pull = digitalio.Pull.UP
        
        rightBTNpin = board.GP6
        rightBTN = digitalio.DigitalInOut(rightBTNpin)
        rightBTN.direction = digitalio.Direction.INPUT
        rightBTN.pull = digitalio.Pull.UP
        
        topBTNpin = board.GP7
        topBTN = digitalio.DigitalInOut(topBTNpin)
        topBTN.direction = digitalio.Direction.INPUT
        topBTN.pull = digitalio.Pull.UP
        
        bottomBTNpin = board.GP8
        bottomBTN = digitalio.DigitalInOut(bottomBTNpin)
        bottomBTN.direction = digitalio.Direction.INPUT
        bottomBTN.pull = digitalio.Pull.UP
        
        aBTNpin = board.GP15
        aBTN = digitalio.DigitalInOut(aBTNpin)
        aBTN.direction = digitalio.Direction.INPUT
        aBTN.pull = digitalio.Pull.UP
        
        bBTNpin = board.GP14
        bBTN = digitalio.DigitalInOut(bBTNpin)
        bBTN.direction = digitalio.Direction.INPUT
        bBTN.pull = digitalio.Pull.UP
        
        while True:
            # Draw a label
            gameOver=False

            score=0
            text = "00"+str(score)
            score_text = label.Label(font, text=text, color=0xFFFF00, x=2, y=4)
            splash.append(score_text)
            #rockShape=circle
            #rock = physicsShape(rockShape)
            
            #pew_line = line.Line(points=[(12,12),(24,24)], palette=color_palette, stroke=1)
            #splash.append(pew_line)
            
            #points=[(0, 5), (4, -6), (0,0), (-4, -6)]
            shippoints=[(0, 5), (4, -6), (0,-3), (-4, -6)]
            ship = PhysicsShape(shippoints, x=64, y=32, screen=splash)
            
            print(ship.bbox())
            
            shipCrashed=False
            
            
            red_left_level = 0
            red_right_level = 0
            grn_left_level = 0
            grn_right_level = 0
            
            
            acceleration = 0
            
                        
            keyPress = None
            shooting = False
            
            bullets=[]
            while True:
                if not leftBTN.value:
                    keyPress = "left"
                if not rightBTN.value:
                    keyPress = "right"
                if not topBTN.value:
                    keyPress = "top"
                if not bottomBTN.value:
                    keyPress = "bottom"
                if not aBTN.value and gameOver:
                    keyPress = "a"


                    #print("a")
                #if not bBTN.value:
                #    keyPress = "b"
                    #print("b")

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
                
                if keyPress == "right":
                    ship.rotate(8)
                    grn_right_level = 65535

                if keyPress == "left":
                    ship.rotate(-8)
                    grn_left_level = 65535

                if keyPress == "top" and acceleration < 2:
                    acceleration+=4

                if keyPress == "bottom" and acceleration > -2:
                    acceleration-=1
                if acceleration > 0.5:
                    acceleration -= 0.05
                
                if not bBTN.value and shooting == False:
                    print("shoot")
                    red_left_level = 65535
        
                    red_right_level = 65535
                    a.play(wav)

                    
                    bullet = Bullet(x=int(ship.x), y=int(ship.y), screen=splash)
                    bullet.rotation = ship.rotation
                    bullet.accelerate(3, float(ship.shape.rotation))
                    bullets.append(bullet)
                    shooting = True
                    
                if bBTN.value and shooting:
                    print("NoShoot")
                    shooting = False
                    
                for bullet in bullets:
                    bullet.updatePosition()
                    if int(bullet.x) < 0 or int(bullet.x) > 127 or int(bullet.y) < 0 or int(bullet.y) > 63:
                        bullet.shape.pop()
                        bullet.screen.remove(bullet.shape)
                        bullets.remove(bullet)
                    else:
                        for rok in roks:
                            if rok.collidesWith(bullet):
                                print("ff")
                                a.play(wav2)
                                if rok.minRadius < 6:
                                    rok.shape.pop()
                                    rok.screen.remove(rok.shape)
                                    roks.remove(rok)
                                else:
                                    rok.smash(bullet.vx/2, bullet.vy/2)

                                score += 1
                                score_text.text = "00" + str(score)
                                print(rok.minRadius)
                
                if not gameOver:
                    ship.screenWrap()
                            
                #print(x_value, y_value)
                
                if len(roks) == 0:
                    rok = Rok(x=[32,96][random.randint(0,1)], y=[16,32,48][random.randint(0,2)], initva=4, screen=splash)
                    roks.append(rok)
                    rok.accelerate(1+score/2, -130)
                
                ship.accelerate(acceleration)
                
        
                ship.updatePosition()
                shipCollision=False
                for rok in roks:
                    rok.updatePosition()
                    rok.screenWrap()
                    if ship.collidesWith(rok):
                        gameOver = True
                        ship.x,ship.y=400, 400
                        #splash.remove(ship)
                if gameOver:
                    if keyPress == "a":
                        print(splash)
                        gameOver=False
                        score_text.text = ""
                        
                        
                        rok.shape.pop()
                        rok.screen.remove(rok.shape)
                        roks.remove(rok)
                        
                        ship.shape.pop()
                        ship.screen.remove(ship.shape)
                        
                        for bullet in bullets:
                            bullet.shape.pop()
                            bullet.screen.remove(bullet.shape)
                            bullets.remove(bullet)
                        break
                    
                    
                     
                    score_text.text = "GAME OVER"    
                            
                time.sleep(0.02)
                gc.collect()
    
try:
    main()
finally:
    displayio.release_displays()
    print("exiting ...")


