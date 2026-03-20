import mido
import pygame.midi

pygame.midi.init()

# Ouvre la sortie MIDI
output = pygame.midi.Output(0)

midi_file = mido.MidiFile('Yiruma-RiversFlowInYou.mid')

for message in midi_file.play():
    if message.type == 'note_on':
        # Note on - jouer la note
        output.note_on(message.note, message.velocity)
    elif message.type == 'note_off':
        # Note off - arrêter la note
        output.note_off(message.note, message.velocity)

pygame.midi.quit()

