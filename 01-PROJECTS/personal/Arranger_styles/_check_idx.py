"""Compare REF vs OUR: how cv_track_mappings reference the global indices."""
from tools.korf import read_bank
from tools.style_reader import parse_style

for label, path in [('REF', r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY'),
                    ('OUR', r'verif\TEST.SET\STYLE\USER01.STY')]:
    b = read_bank(path)
    # find first style
    for i, t in enumerate(b.toc):
        if t.object_type == 2:
            s = parse_style(b.objects[i])
            break
    print(f'\n=== {label} {s.info.name!r} ===')
    tm = s.track_mapping
    print(f'  n_midi_tracks={tm.n_midi_tracks} indices_len={len(tm.indices)}')
    # show indices uniqueness
    print(f'  indices first 30: {tm.indices[:30]}')
    print(f'  indices last 30:  {tm.indices[-30:]}')
    # for each element, show range of cv.track_number used
    for ei, elem in enumerate(s.style_elements):
        all_tns = []
        for cv_idx, mt in elem.master_tracks:
            for cv in mt.cv_track_mappings:
                all_tns.append(cv.track_number)
        if all_tns:
            print(f'  elem[{ei:2d}] cv_flags=0x{elem.info.chord_variations_with_data:02x} masters={len(elem.master_tracks)} '
                  f'track_num min={min(all_tns)} max={max(all_tns)} unique={len(set(all_tns))}')
