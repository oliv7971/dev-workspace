"""Compare REF master events vs cv_track_mappings to understand the relationship."""
from tools.korf import read_bank
from tools.style_reader import parse_style

ref = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
sr = parse_style(ref.objects[0])

# Look at element 4 (typical Variation, 2 masters)
for ei in [0, 4, 11]:
    elem = sr.style_elements[ei]
    print(f'\n=== Elem {ei} cv_flags=0x{elem.info.chord_variations_with_data:02x} ===')
    for mi, (cv_idx, mt) in enumerate(elem.master_tracks):
        print(f' Master {mi} cv={cv_idx} events={len(mt.events)} mappings={len(mt.cv_track_mappings)}')
        # Show all meta events
        meta_count = 0
        for ev in mt.events:
            if ev.type == 'meta' and ev.meta_type == 0x7E:
                print(f'   meta 0x7E data={ev.meta_data.hex(" ")}')
                meta_count += 1
            elif ev.type == 'meta':
                print(f'   meta 0x{ev.meta_type:02x} data={ev.meta_data.hex(" ")}')
        print(f'   ({meta_count} meta 0x7E events)')
        print(f'   cv_track_mappings:')
        for cv in mt.cv_track_mappings:
            print(f'     type={cv.type} track_number={cv.track_number}')
