# Adapting the example in https://learn.adafruit.com/adafruit-oled-featherwing/python-usage
# to use with Raspberry Pi Pico and CircuitPython
from picoboygame import *

import time
import math
import random

import vectorio

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


roks=[]


sfx_laser = open("sounds/sfx_wpn_laser5.wav", "rb")
data2 = open("sounds/sfx_sounds_impact6.wav", "rb")






led_red_left = pwmio.PWMOut(board.LED_RED_LEFT)
led_red_right = pwmio.PWMOut(board.LED_RED_RIGHT)
led_green_left = pwmio.PWMOut(board.LED_GREEN_LEFT)
led_green_right = pwmio.PWMOut(board.LED_GREEN_RIGHT)




button.updateButton()






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
        
        if button.getKeyPress("Right"):
            ship.rotate(8)
            grn_right_level = 65535

        if button.getKeyPress("Left"):
            ship.rotate(-8)
            grn_left_level = 65535

        if button.getKeyPress("Up") and acceleration < 2:
            acceleration+=4

        if button.getKeyPress("Down") and acceleration > -2:
            acceleration-=1
        if acceleration > 0.5:
            acceleration -= 0.05
        
        if button.getKeyPress("B") and shooting == False and not gameOver:
            print("shoot")
            red_left_level = 65535

            red_right_level = 65535
            audio.play(sfx_laser)

            
            bullet = Bullet(x=int(ship.x), y=int(ship.y), screen=splash)
            bullet.rotation = ship.rotation
            bullet.accelerate(3, float(ship.shape.rotation))
            bullets.append(bullet)
            shooting = True
            
        if not button.getKeyPress("B") and shooting:
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
                            rok.smash(bullet.vx/2, bullet.vy/2, roks)

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
            if button.getKeyPress("A"):
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
