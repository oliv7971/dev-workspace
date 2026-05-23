"""Show first global track's events (REF vs OURS)."""
from tools.korf import read_bank
from tools.style_reader import parse_style

ref = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
sr = parse_style(ref.objects[0])
ours = read_bank(r'verif\TEST.SET\STYLE\USER01.STY')
so = parse_style(ours.objects[0])

def show(label, t):
    print(f'\n{label}: chunk_type={t.chunk_type} ts={t.time_scale} unknowns={t.unknowns.hex(" ")}')
    print(f'  {len(t.events)} events. First 20:')
    cum = 0
    for ev in t.events[:20]:
        if ev.type == 'delta':
            cum += ev.delta
            print(f'    delta=+{ev.delta}  (cum={cum})')
        elif ev.type == 'note_on':
            print(f'    note_on  ch?  pitch={ev.value1} vel={ev.value2}  unk={ev.unknown_additional}')
        elif ev.type == 'note_off':
            print(f'    note_off pitch={ev.value1} vel={ev.value2}  unk={ev.unknown_additional}')
        elif ev.type == 'cc':
            print(f'    cc {ev.value1}={ev.value2}  unk={ev.unknown_additional}')
        elif ev.type == 'meta':
            print(f'    meta type=0x{ev.meta_type:02x} data={ev.meta_data.hex(" ")}')
        else:
            print(f'    {ev.type} v1={ev.value1} v2={ev.value2}')

# REF first track
show('REF track[0]', sr.midi_tracks[0])
# OUR first track
show('OUR track[0]', so.midi_tracks[0])
# OUR drum track
for t in so.midi_tracks:
    if t.chunk_type == 'drum' and any(e.type == 'note_on' for e in t.events):
        show('OUR first drum track with notes', t)
        break
