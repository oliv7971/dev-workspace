"""Examine REF master_tracks unknowns + raw byte structure."""
from tools.korf import read_bank
from tools.style_reader import parse_style
from tools.style_writer import encode_master_midi_track

ref = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
sr = parse_style(ref.objects[0])

elem = sr.style_elements[11]
for mi, (cv_idx, mt) in enumerate(elem.master_tracks):
    print(f'Master {mi}: ts={mt.time_scale} unk2={mt.unknown2} unk3={mt.unknown3}')
    print(f'  encoded: {encode_master_midi_track(mt).hex(" ")}')

print('\n=== OUR ===')
ours = read_bank(r'verif\TEST.SET\STYLE\USER01.STY')
so = parse_style(ours.objects[0])
elem = so.style_elements[11]
for mi, (cv_idx, mt) in enumerate(elem.master_tracks):
    print(f'Master {mi}: ts={mt.time_scale} unk2={mt.unknown2} unk3={mt.unknown3}')
    print(f'  encoded: {encode_master_midi_track(mt).hex(" ")}')
