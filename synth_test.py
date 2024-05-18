import board
import time
import synthio
import audiopwmio
import audiomixer


audio = audiopwmio.PWMAudioOut(board.GP11)

mixer = audiomixer.Mixer(channel_count=1, sample_rate=22050, buffer_size=2048)
synth = synthio.Synthesizer(channel_count=1, sample_rate=22050)

audio.play(mixer)
mixer.voice[0].play(synth)
mixer.voice[0].level = 0.4

while True:
    synth.press((65, 69, 72))  # midi note 65 = F4
    time.sleep(0.5)
    synth.release((65, 69, 72))  # release the note we pressed
    time.sleep(0.5)
    mixer.voice[0].level = (mixer.voice[0].level - 0.1) % 0.4  # reduce volume each pass