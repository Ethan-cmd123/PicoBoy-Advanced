# Adapting the example in https://learn.adafruit.com/adafruit-oled-featherwing/python-usage
# to use with Raspberry Pi Pico and CircuitPython
import os
import board
import gc
import time
import random
import busio
import digitalio
import displayio

import sys
import supervisor

from terminalio import FONT as font
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
#import adafruit_displayio_sh1106
import adafruit_displayio_ssd1305
from adafruit_display_shapes.sparkline import Sparkline
from neopixel_write import neopixel_write

#import importlib

import pwmio

import audiocore
import audiopwmio

neopixel_pin = digitalio.DigitalInOut(board.NEOPIXEL)
neopixel_pin.direction = digitalio.Direction.OUTPUT

neopixel_write(neopixel_pin, bytearray([2,2,2]))

def layerVisibility(state, layer, target):
    try:
        if state == "show":
            time.sleep(0.1)
            layer.append(target)
        elif state == "hide":
            layer.remove(target)
    except ValueError:
        pass

def gameLibrary(yPos, gameTitle):
    rect = Rect(0, yPos, 128, 20, fill=0, outline=0xFFFFFF)

    text_area = label.Label(font, text=gameTitle, color=0xFFFF00, x=37, y=10+yPos)
    
    return rect, text_area



def main():
    Impact = open("sfx_sounds_impact6.wav", "rb")
    ImpactWAV = audiocore.WaveFile(Impact)
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
        splashScreen = displayio.Group() # Group for View 1 objects
        menuScreen = displayio.Group() # Group for View 2 objects
        view3 = displayio.Group() # Group for View 3 objects
        display.root_group=splash

        color_bitmap = displayio.Bitmap(128, 64, 1) # Full screen white
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF  # White
         
        btnLeftpin = board.GP3
        btnLeft = digitalio.DigitalInOut(btnLeftpin)
        btnLeft.direction = digitalio.Direction.INPUT
        btnLeft.pull = digitalio.Pull.UP
        
        btnRightpin = board.GP6
        btnRight = digitalio.DigitalInOut(btnRightpin)
        btnRight.direction = digitalio.Direction.INPUT
        btnRight.pull = digitalio.Pull.UP
        
        btnUppin = board.GP7
        btnUp = digitalio.DigitalInOut(btnUppin)
        btnUp.direction = digitalio.Direction.INPUT
        btnUp.pull = digitalio.Pull.UP
        
        btnDownpin = board.GP8
        btnDown = digitalio.DigitalInOut(btnDownpin)
        btnDown.direction = digitalio.Direction.INPUT
        btnDown.pull = digitalio.Pull.UP
        
        btnApin = board.GP15
        btnA = digitalio.DigitalInOut(btnApin)
        btnA.direction = digitalio.Direction.INPUT
        btnA.pull = digitalio.Pull.UP
        
        btnBpin = board.GP14
        btnB = digitalio.DigitalInOut(btnBpin)
        btnB.direction = digitalio.Direction.INPUT
        btnB.pull = digitalio.Pull.UP
        
        #-----------------------------------SPLASH SCREEN----------------------------------------# 
        
        text = "Pico Boy"
        text_area = label.Label(font, text=text, color=0xFFFF00, x=37, y=15)
        splashScreen.append(text_area)

        text = "ADVANCED"
        text_area = label.Label(font, text=text, color=0xFFFF00, x=37, y=29)
        splashScreen.append(text_area)
        
        loadingDot1 = "..."
        loadingDot1_text_area = label.Label(font, text=loadingDot1, color=0xFFFF00, x=37, y=44)
        splashScreen.append(loadingDot1_text_area)
        #-----------------------------------SPLASH SCREEN----------------------------------------#
        
        #-----------------------------------MENU SCREEN----------------------------------------# 
        currentGameListPage = 0
        gamesPerPage = 3
        
        
        path = "/GameLibrary/"
        fullGameList = os.listdir(path)
        print(fullGameList)
        #fullGameList = ["Asteroids", "Monkey Game", "Mario Kart", "Brick wall", "A", "b", "c"]
        displayedGameList = fullGameList[3*currentGameListPage:3]
        
        if len(displayedGameList) < gamesPerPage:
            gamesPerPage = len(displayedGameList)
        
        menuText = []
        
    
#         for root, dirs, files in os.walk(folder_path):
#             for file in files:
#                 if file.endswith('.py'):
#                     python_files.append(file)
        print(displayedGameList)
        
        for i,game in enumerate(displayedGameList):
            ypos=20*i
            rect = Rect(0, ypos, 128, 20, fill=0, outline=0xFFFFFF)
            text = label.Label(font, text=game.split(".")[0], color=0xFFFF00, x=37, y=10+ypos)
            
            
            menuScreen.append(rect)
            
            menuText.append(text)
            menuScreen.append(text)
                
        selector = Circle(14, 9, 5, fill=0, outline=0xFFFFFF)
        menuScreen.append(selector)

        #-----------------------------------MENU SCREEN----------------------------------------# 
        currentLayer=splashScreen
        currentSelectedgame = 0
         
        # Start the main loop
        while True:
            keyPressLeft = not btnLeft.value
            keyPressRight = not btnRight.value
            keyPressUp = not btnUp.value
            keyPressDown = not btnDown.value
            keyPressA = not btnA.value
            keyPressB = not btnB.value
            
            if currentLayer == splashScreen:
                layerVisibility("show", splash, splashScreen)
                if loadingDot1_text_area.x < 70:
                    loadingDot1_text_area.x +=3
                else:
                    layerVisibility("hide", splash, splashScreen)
                    currentLayer=menuScreen
            else:
                #audio.play(ImpactWAV)
                currentLayer=menuScreen
                if keyPressDown and currentSelectedgame < len(fullGameList)-1:
                    currentSelectedgame += 1
                     
                if keyPressUp and currentSelectedgame > 0:
                    currentSelectedgame -= 1
                    
                print(f"currentSelectedgame : {currentSelectedgame}")
                
                currentGameListPage = (currentSelectedgame)//3
                print(f"currentGameListPage : {currentGameListPage}")
                
                if keyPressB:
                    print("Loading Next Game You Monkey")
                    supervisor.set_next_code_file('/GameLibrary/'+fullGameList[currentSelectedgame], reload_on_success=True)
                    supervisor.reload()
                
                for i in range(3*currentGameListPage, (3*currentGameListPage)+gamesPerPage):
                    if i < len(fullGameList):
                        menuText[i%3].text = fullGameList[i].split(".")[0]
                    else:
                        menuText[i%3].text = "-"
                
                displaySelector = currentSelectedgame%3
                selector.y =((displaySelector)*20)+4

                    
                
                
                        
            if currentLayer == menuScreen:
                layerVisibility("show", splash, menuScreen)


            time.sleep(0.02)    
try:
    main()
finally:
    displayio.release_displays()
    print("exiting ...")


