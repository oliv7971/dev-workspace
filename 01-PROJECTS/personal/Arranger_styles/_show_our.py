"""Show our tracks similarly."""
from tools.korf import read_bank
from tools.style_reader import parse_style

ours = read_bank(r'verif\TEST.SET\STYLE\USER01.STY')
so = parse_style(ours.objects[0])
seen = set()
for tidx, tr in enumerate(so.midi_tracks):
    n = sum(1 for e in tr.events if e.type == 'note_on')
    if n >= 5 and tr.chunk_type not in seen:
        seen.add(tr.chunk_type)
        print(f'\n--- {tr.chunk_type} (track[{tidx}]) {len(tr.events)} events  unk={tr.unknowns.hex(" ")} ---')
        for ev in tr.events[:8]:
            print(f'  {ev}')
        print(f'  ... last 4 events:')
        for ev in tr.events[-4:]:
            print(f'  {ev}')
        if len(seen) >= 4: break

# Also check empty tracks
print('\n--- Empty tracks ---')
for tidx, tr in enumerate(so.midi_tracks):
    if len(tr.events) <= 3:
        print(f'  track[{tidx}] {tr.chunk_type} {len(tr.events)} events: {tr.events}')
        if tidx >= 5: break
