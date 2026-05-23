"""Compute cumulative cv_mapping count per element to understand indices layout."""
from tools.korf import read_bank
from tools.style_reader import parse_style

for label, path in [('REF', r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY'),
                    ('OUR', r'verif\TEST.SET\STYLE\USER01.STY')]:
    b = read_bank(path)
    for i, t in enumerate(b.toc):
        if t.object_type == 2:
            s = parse_style(b.objects[i])
            break
    print(f'\n=== {label} {s.info.name!r} ===')
    tm = s.track_mapping
    print(f'  n_midi_tracks={tm.n_midi_tracks} indices_len={len(tm.indices)}')
    cum = 0
    cum_master = 0
    for ei, elem in enumerate(s.style_elements):
        n_masters = len(elem.master_tracks)
        per_master = [len(mt.cv_track_mappings) for _, mt in elem.master_tracks]
        n_total = sum(per_master)
        print(f'  elem[{ei:2d}] masters={n_masters} cvmap_per={per_master} total={n_total}')
        cum += n_total
        cum_master += n_masters
    print(f'  TOTAL cv_mappings={cum}  TOTAL master_tracks={cum_master}')
