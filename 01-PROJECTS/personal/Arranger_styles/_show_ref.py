"""Show first events with all attributes (REF first non-empty track of each type)."""
from tools.korf import read_bank
from tools.style_reader import parse_style

ref = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
sr = parse_style(ref.objects[0])
seen = set()
for tidx, tr in enumerate(sr.midi_tracks):
    n = sum(1 for e in tr.events if e.type == 'note_on')
    if n >= 5 and tr.chunk_type not in seen:
        seen.add(tr.chunk_type)
        print(f'\n--- {tr.chunk_type} (track[{tidx}]) {len(tr.events)} events ---')
        for ev in tr.events[:6]:
            print(f'  {ev}')
        print(f'  ... last 4 events:')
        for ev in tr.events[-4:]:
            print(f'  {ev}')
        if len(seen) >= 4: break
