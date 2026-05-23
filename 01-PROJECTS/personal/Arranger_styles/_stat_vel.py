"""Patch reader temporarily to keep raw v2 byte and check stats."""
import re
src = open(r'tools/style_reader.py').read()
# Just inspect raw bytes of the first MIDI track in style[0]
from tools.korf import read_bank
b = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
obj = b.objects[0]

# Walk chunks to find MIDITrackList -> first track midi data...
# Simpler: scan for sequences "01 ?? ??" "00 ?? ??" and check bit7 of byte after
counts = {'note_on_with_bit7': 0, 'note_on_without_bit7': 0,
          'note_off_with_bit7': 0, 'note_off_without_bit7': 0}
i = 0
while i < len(obj) - 3:
    code = obj[i]
    # Only check unambiguous code 0/1 not in delta context — heuristic only
    if code in (0, 1) and i > 0 and (obj[i-1] & 0x80):  # preceded by delta end
        v1 = obj[i+1]
        v2 = obj[i+2]
        if v1 < 128:  # plausible pitch
            key = ('note_on' if code == 1 else 'note_off') + ('_with_bit7' if v2 & 0x80 else '_without_bit7')
            counts[key] += 1
    i += 1
print(counts)
