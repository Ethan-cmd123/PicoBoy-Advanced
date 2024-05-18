import board
import audiocore
import audiopwmio
import digitalio
import pwmio

data = open("sfx_movement_jump1.wav", "rb")
wav = audiocore.WaveFile(data)
a = audiopwmio.PWMAudioOut(board.GP11)

print("playing")
a.play(wav)
while a.playing:
  pass
print("stopped")