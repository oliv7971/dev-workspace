"""Compare raw MIDI track binaries (REF vs OUR) at the byte level."""
from tools.korf import read_bank
from tools.style_reader import parse_style
from tools.style_writer import encode_midi_track

for label, path in [('REF', r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY'),
                    ('OUR', r'verif\TEST.SET\STYLE\USER01.STY')]:
    b = read_bank(path)
    for i, t in enumerate(b.toc):
        if t.object_type == 2:
            s = parse_style(b.objects[i])
            break
    print(f'\n=== {label} {s.info.name!r} ===')
    # First non-empty track
    for tidx, tr in enumerate(s.midi_tracks):
        n = sum(1 for e in tr.events if e.type == 'note_on')
        if n >= 5:
            print(f'  track[{tidx}] {tr.chunk_type} ts={tr.time_scale} unk={tr.unknowns.hex(" ")} events={len(tr.events)} notes={n}')
            data, ct = encode_midi_track(tr)
            print(f'  encoded ct=0x{ct:02x} bytes={len(data)} hex first 80:')
            print(f'    {data[:80].hex(" ")}')
            # Show first 6 events in detail
            for ev in tr.events[:8]:
                attrs = {k: v for k, v in vars(ev).items() if v is not None}
                print(f'    {attrs}')
            break
