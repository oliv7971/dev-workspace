"""Trace: for each StyleElement, find which midi_tracks are actually referenced and check their notes."""
from tools.korf import read_bank
from tools.style_reader import parse_style

ours = read_bank(r'verif\TEST.SET\STYLE\USER01.STY')
so = parse_style(ours.objects[0])
indices = so.track_mapping.indices  # 1-based references into midi_tracks

# Walk each element, accumulating offset
offset = 0
for ei, elem in enumerate(so.style_elements[:5]):
    print(f'\n=== Element {ei} ({elem.info.cue_mode}) ===')
    for j, (cv, mt) in enumerate(elem.master_tracks):
        print(f'  master[{j}] cv={cv}, n_mappings={len(mt.cv_track_mappings)}')
        for m in mt.cv_track_mappings:
            global_idx_pos = offset + m.track_number
            if global_idx_pos < len(indices):
                track_idx_1based = indices[global_idx_pos]
                track = so.midi_tracks[track_idx_1based - 1]
                n_notes = sum(1 for e in track.events if e.type == 'note_on')
                print(f'    type={m.type} local={m.track_number} -> indices[{global_idx_pos}]={track_idx_1based} '
                      f'-> midi_track[{track_idx_1based-1}] type={track.chunk_type} notes={n_notes}')
            else:
                print(f'    type={m.type} local={m.track_number} -> indices[{global_idx_pos}] OUT OF RANGE')
        offset += len(mt.cv_track_mappings)
