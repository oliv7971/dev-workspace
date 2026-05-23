"""Compare playable structure (notes, CV mappings, enable flags) between REF and OURS."""
from tools.korf import read_bank
from tools.style_reader import parse_style
from collections import Counter

def stats(label, style):
    print(f'\n=== {label} ===')
    print(f'  StyleInfo: enabled=0x{style.info.enabled_style_elements:04x} '
          f'with_data=0x{style.info.style_elements_with_data:04x}')
    print(f'  global midi_tracks: {len(style.midi_tracks)}')
    track_notes = []
    for t in style.midi_tracks:
        n = sum(1 for e in t.events if e.type == 'note_on')
        track_notes.append(n)
    print(f'  notes per track: total={sum(track_notes)} '
          f'min={min(track_notes) if track_notes else 0} '
          f'max={max(track_notes) if track_notes else 0}')
    print(f'  StyleElements: {len(style.style_elements)}')
    for i, e in enumerate(style.style_elements[:3]):
        print(f'    elem[{i}]: cv_flags=0x{e.info.chord_variations_with_data:02x} '
              f'cue={e.info.cue_mode} ts={e.info.time_sig_numerator}/{e.info.time_sig_denominator} '
              f'n_master_tracks={len(e.master_tracks)}')
        for j, (cv, mt) in enumerate(e.master_tracks[:2]):
            n_evs = len(mt.events)
            mappings = [(m.type, m.track_number) for m in mt.cv_track_mappings]
            print(f'      master[{j}] cv={cv} ts={mt.time_scale} n_events={n_evs} '
                  f'mappings={mappings[:5]}{"..." if len(mappings)>5 else ""}')
    print(f'  TrackMapping: n={style.track_mapping.n_midi_tracks} '
          f'indices_count={len(style.track_mapping.indices)}')

ref = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
sr = parse_style(ref.objects[0])
stats(f'REF: {ref.toc[0].name!r}', sr)

ours = read_bank(r'verif\TEST.SET\STYLE\USER01.STY')
so = parse_style(ours.objects[0])
stats(f'OUR: {ours.toc[0].name!r}', so)
