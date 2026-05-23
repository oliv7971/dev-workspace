"""Compare structural attributes REF vs OUR after writer fix."""
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
    info = s.info
    print(f'  unknowns ({len(info.unknowns)}): {info.unknowns.hex(" ")}')
    print(f'  enabled=0x{info.enabled_style_elements:04x} with_data=0x{info.style_elements_with_data:04x}')
    tm = s.track_mapping
    print(f'  TrackMapping: n_tracks={tm.n_midi_tracks} n_indices={len(tm.indices)}')
    # Element 11 (Variation 1) details
    elem = s.style_elements[11]
    print(f'  elem[11] cv_flags=0x{elem.info.chord_variations_with_data:02x} '
          f'ts={elem.info.time_sig_numerator}/{elem.info.time_sig_denominator} '
          f'cue={elem.info.cue_mode}')
    print(f'    chord_table entries (24): {elem.info.chord_table.entries}')
    for mi, (cv, mt) in enumerate(elem.master_tracks):
        meta_count = sum(1 for e in mt.events if e.type=='meta' and e.meta_type==0x7E)
        print(f'    master[{mi}] cv={cv} ts={mt.time_scale} unk2={mt.unknown2} unk3={mt.unknown3} '
              f'meta_7E={meta_count} mappings={len(mt.cv_track_mappings)}')
