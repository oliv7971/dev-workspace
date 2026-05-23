"""Check Variation1 (elem 11) tracks in OURS."""
from tools.korf import read_bank
from tools.style_reader import parse_style

ours = read_bank(r'verif\TEST.SET\STYLE\USER01.STY')
so = parse_style(ours.objects[0])

elem = so.style_elements[11]
print(f'Elem 11: cv_flags=0x{elem.info.chord_variations_with_data:02x} masters={len(elem.master_tracks)}')
tm = so.track_mapping
print(f'TrackMapping: n_midi_tracks={tm.n_midi_tracks} indices_len={len(tm.indices)}')

for mi, (cv_idx, mt) in enumerate(elem.master_tracks):
    print(f'\n Master {mi}: cv={cv_idx} ts={mt.time_scale} unk2={mt.unknown2} unk3={mt.unknown3} events={len(mt.events)} mappings={len(mt.cv_track_mappings)}')
    for ev in mt.events[:8]:
        if ev.type == 'meta':
            print(f'   meta type=0x{ev.meta_type:02x} data={ev.meta_data.hex(" ")}')
        elif ev.type == 'delta':
            print(f'   delta=+{ev.delta}')
        else:
            print(f'   {ev.type} v1={ev.value1} v2={ev.value2}')
    print(f'  cv_track_mappings:')
    for cv in mt.cv_track_mappings:
        ti = cv.track_number
        real = tm.indices[ti] - 1 if ti < len(tm.indices) else -1  # 1-based -> 0-based
        track = so.midi_tracks[real] if 0 <= real < len(so.midi_tracks) else None
        if track:
            n_notes = sum(1 for e in track.events if e.type == 'note_on')
            print(f'   type={cv.type} ti={ti}->idx={real}  chunk={track.chunk_type} events={len(track.events)} notes={n_notes}')
        else:
            print(f'   type={cv.type} ti={ti}->idx={real} INVALID')
