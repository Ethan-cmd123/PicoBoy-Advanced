import board
import synthio
import audiopwmio


dac = audiopwmio.PWMAudioOut(board.GP11)

melody = synthio.MidiTrack(b"\0\x90H\0*\x80H\0\6\x90J\0*\x80J\0\6\x90L\0*\x80L\0\6\x90J\0" +
                           b"*\x80J\0\6\x90H\0*\x80H\0\6\x90J\0*\x80J\0\6\x90L\0T\x80L\0" +
                           b"\x0c\x90H\0T\x80H\0\x0c\x90H\0T\x80H\0", tempo=320)
dac.play(melody)
print("playing")
while dac.playing:
  pass
print("stopped")