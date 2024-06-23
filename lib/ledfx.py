import time
import math
import pwmio

MAX_LED_BRIGHTNESS = 65535
LED_BRIGHTNESS_CORRECTION = 1.4

class ledfx:
    animation_speed = 1
    animation_length = 0
    set_brightness = 0
    
    def __init__(self, pin, colour, position):
        self.pin = pin
        self.output = pwmio.PWMOut(self.pin)
        self.colour = colour
        self.position = position
        self.animating = 0
        self.animation_start_time = time.monotonic()

    def set(self,value):
        self.set_brightness = value
        self.output.duty_cycle = self.set_brightness

    def _set(self,value):
        self.output.duty_cycle = value
        
    def animate(self,mode,speed=1,length=0):
        self.animating = mode
        self.animation_speed=speed
        self.animation_length=length
        
    def pulse(self,times,speed):
        self.animation_speed = speed
        self.animation_length = (times*speed)*math.pi
        self.animation_start_time = time.monotonic()
        self.animating = 1
        
    def update(self):
        elapsed_time = (time.monotonic()-self.animation_start_time)
        if self.animation_length and elapsed_time > self.animation_length:
            self.animation = 0
            self._set(self.set_brightness)
            return
        if self.animating == 0:
            return
        elif self.animating == 1:
            self.update_pulse(elapsed_time)
        elif self.animating == 2:
            self.update_antipulse(elapsed_time)
            
    def update_pulse(self,elapsed_time):
        # Calculate breathing cycle position based on elapsed time and speed
        cycle_position = elapsed_time * self.animation_speed
        # Use sine wave to simulate brightness with offset and scaling
        brightness = MAX_LED_BRIGHTNESS / 2 * (1 + math.sin(cycle_position))
        corrected_brightness = int(MAX_LED_BRIGHTNESS * (brightness / MAX_LED_BRIGHTNESS) ** LED_BRIGHTNESS_CORRECTION)
        self._set(int(corrected_brightness))
        
    def update_antipulse(self,elapsed_time):
        # Calculate breathing cycle position based on elapsed time and speed
        cycle_position = elapsed_time * self.animation_speed
        # Use sine wave to simulate brightness with offset and scaling
        brightness = MAX_LED_BRIGHTNESS / 2 * (1 + -math.sin(cycle_position))
        corrected_brightness = int(MAX_LED_BRIGHTNESS * (brightness / MAX_LED_BRIGHTNESS) ** LED_BRIGHTNESS_CORRECTION)
        self._set(int(corrected_brightness))
        
        