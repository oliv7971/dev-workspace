"""Compare StyleTrackData slot layout REF vs OUR for elem 0."""
from tools.korf import read_bank
from tools.style_reader import parse_style

for label, path in [('REF', r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY'),
                    ('OUR', r'verif\TEST.SET\STYLE\USER01.STY')]:
    b = read_bank(path)
    for i, t in enumerate(b.toc):
        if t.object_type == 2:
            s = parse_style(b.objects[i])
            break
    elem = s.style_elements[0]
    print(f'\n=== {label} elem 0 StyleTrackData ===')
    for i, e in enumerate(elem.track_data):
        print(f'  slot[{i}] expr={e.expression} msb={e.sound.msb} lsb={e.sound.lsb} pc={e.sound.program} '
              f'range=[{e.range_bottom}..{e.range_top}] ntt={e.ntt} unk1={e.unknown1.hex(" ")} unk3={e.unknown3}')
