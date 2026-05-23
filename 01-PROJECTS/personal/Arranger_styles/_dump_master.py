"""Dump first master track events of REF vs OURS."""
from tools.korf import read_bank
from tools.style_reader import parse_style

ref = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
sr = parse_style(ref.objects[0])
ours = read_bank(r'verif\TEST.SET\STYLE\USER01.STY')
so = parse_style(ours.objects[0])

def dump(label, style, eidx=0):
    print(f'\n=== {label} elem[{eidx}] ===')
    e = style.style_elements[eidx]
    for j, (cv, mt) in enumerate(e.master_tracks):
        print(f'  master[{j}] cv={cv} ts={mt.time_scale} unk2={mt.unknown2} unk3={mt.unknown3}')
        print(f'    {len(mt.events)} events:')
        for k, ev in enumerate(mt.events[:20]):
            if ev.type == 'meta':
                print(f'      [{k}] meta type=0x{ev.meta_type:02x} data={ev.meta_data.hex(" ")}')
            elif ev.type == 'delta':
                print(f'      [{k}] delta={ev.delta}')
            else:
                print(f'      [{k}] {ev.type}')
        if len(mt.events) > 20:
            print(f'      ...+{len(mt.events)-20} more')
        print(f'    {len(mt.cv_track_mappings)} mappings: {[(m.type,m.track_number) for m in mt.cv_track_mappings]}')

dump(f'REF {ref.toc[0].name}', sr, 0)
dump(f'OUR {ours.toc[0].name}', so, 0)
print()
print('REF style elem[0].info:')
print(f'  chord_variations_with_data={sr.style_elements[0].info.chord_variations_with_data}')
print(f'  chord_table.entries={sr.style_elements[0].info.chord_table.entries}')
print('OUR style elem[0].info:')
print(f'  chord_variations_with_data={so.style_elements[0].info.chord_variations_with_data}')
print(f'  chord_table.entries={so.style_elements[0].info.chord_table.entries}')
