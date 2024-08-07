# Adapting the example in https://learn.adafruit.com/adafruit-oled-featherwing/python-usage
# to use with Raspberry Pi Pico and CircuitPython
import board
from picoboygame import audio, neopixel
import time
import math
import random
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

## Un/mute Game :D
audio.mute(False)

# Load the dispaly and unset screen 
display=board.DISPLAY
display.root_group=None

# Create a new screen and set it to the display
splash = displayio.Group()
display.root_group=splash

color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

FPS_DELAY = 1/30 # 50FPS

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

roks=[]
sfx_laser = open("sounds/sfx_wpn_laser5.wav", "rb")
data2 = open("sounds/sfx_sounds_impact6.wav", "rb")

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


led_red_left = pwmio.PWMOut(board.LED_RED_LEFT)
led_red_right = pwmio.PWMOut(board.LED_RED_RIGHT)
led_green_left = pwmio.PWMOut(board.LED_GREEN_LEFT)
led_green_right = pwmio.PWMOut(board.LED_GREEN_RIGHT)

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
    
    last_update_time = time.monotonic()
                
    keyPress = None
    shooting = False
    
    bullets=[]
    while True:
        keyPressLeft = not btnLeft.value
        keyPressRight = not btnRight.value
        keyPressUp = not btnUp.value
        keyPressDown = not btnDown.value
        keyPressA = not btnA.value
        keyPressB = not btnB.value
           
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
        
        if keyPressRight:
            ship.rotate(8)
            grn_right_level = 65535

        if keyPressLeft:
            ship.rotate(-8)
            grn_left_level = 65535

        if keyPressUp and acceleration < 2:
            acceleration+=4

        if keyPressDown and acceleration > -2:
            acceleration-=1
        if acceleration > 0.5:
            acceleration -= 0.05
        
        if keyPressB and shooting == False and not gameOver:
            print("shoot")
            red_left_level = 65535

            red_right_level = 65535
            audio.play(sfx_laser)

            
            bullet = Bullet(x=int(ship.x), y=int(ship.y), screen=splash)
            bullet.rotation = ship.rotation
            bullet.accelerate(3, float(ship.shape.rotation))
            bullets.append(bullet)
            shooting = True
            
        if not keyPressB and shooting:
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
                        #audio.play(wav2)
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
                audio.stop()
                gameOver = True
                ship.x,ship.y=400, 400
                #splash.remove(ship)
        if gameOver:
            if keyPressA:
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
                    
        now = time.monotonic()
        # see if we should wait to render the next frame.
        while now <= last_update_time + FPS_DELAY:
            now = time.monotonic()
        last_update_time = time.monotonic()
