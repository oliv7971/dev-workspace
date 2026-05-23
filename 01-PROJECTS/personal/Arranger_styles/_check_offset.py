"""Verify element 11 actually points to its own tracks via cumulative offset."""
from tools.korf import read_bank
from tools.style_reader import parse_style

ours = read_bank(r'verif\TEST.SET\STYLE\USER01.STY')
so = parse_style(ours.objects[0])
tm = so.track_mapping

# Cumulate cv_mapping counts per element to compute the "global offset"
offset = 0
for ei, elem in enumerate(so.style_elements):
    print(f'\nElem {ei} (offset={offset}) masters={len(elem.master_tracks)}')
    for mi, (cv_idx, mt) in enumerate(elem.master_tracks):
        print(f'  Master {mi} cv={cv_idx} mappings:')
        for mappi, cv in enumerate(mt.cv_track_mappings):
            global_pos = offset + mappi
            if global_pos < len(tm.indices):
                idx_val = tm.indices[global_pos]  # 1-based
                tr = so.midi_tracks[idx_val - 1] if 1 <= idx_val <= len(so.midi_tracks) else None
                if tr:
                    n = sum(1 for e in tr.events if e.type == 'note_on')
                    print(f'    [{mappi}] type={cv.type} slot={cv.track_number} -> indices[{global_pos}]={idx_val} -> track[{idx_val-1}] {tr.chunk_type} notes={n}')
                else:
                    print(f'    [{mappi}] indices[{global_pos}]={idx_val} OUT OF RANGE')
            else:
                print(f'    [{mappi}] global_pos {global_pos} >= indices len {len(tm.indices)} OVERFLOW')
        offset += len(mt.cv_track_mappings)
    if ei >= 12: break
