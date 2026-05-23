"""Dump des events KORG avec delta times pour comprendre le timescale."""
import sys
sys.path.insert(0, '.')
from tools.korf import read_bank
from tools.style_reader import parse_style, STYLE_ELEMENT_NAMES

bank = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
style = parse_style(bank.objects[0])
print(f"Style: {style.info.name!r}")

# Trouver les pistes de Variation1 en utilisant le TrackMapping
tm = style.track_mapping
elem11 = style.style_elements[11]  # Variation1
print(f"\n=== Variation1 (elem[11]) ===")
print(f"  TimeSig: {elem11.info.time_sig_numerator}/{elem11.info.time_sig_denominator}")
print(f"  CV flags: 0b{elem11.info.chord_variations_with_data:08b}")
for cv_idx, mt in elem11.master_tracks:
    print(f"  CV[{cv_idx}]: timescale={mt.time_scale}  mappings={[(m.type, m.track_number) for m in mt.cv_track_mappings]}")
    for e in mt.events:
        if e.type != 'delta':
            print(f"    {e}")
        else:
            print(f"    Delta({e.delta})")

# Calculer la position dans le TrackMapping pour Variation1
# Somme des totals pour elem[0..10]
from tools.style_reader import STYLE_ELEMENT_NAMES
def count_mappings(elems, upto):
    total = 0
    for i in range(upto):
        for _, mt in elems[i].master_tracks:
            total += len(mt.cv_track_mappings)
    return total

offset11 = count_mappings(style.style_elements, 11)
print(f"\nTrackMapping offset pour Variation1: {offset11}")

cv0_tracks = []
for _, mt in elem11.master_tracks[:1]:  # CV[0] seulement
    for m in mt.cv_track_mappings:
        abs_idx = m.track_number  # test: est-ce absolu dans tm.indices?
        if abs_idx < len(tm.indices):
            global_track_1based = tm.indices[abs_idx]
            global_track_0based = global_track_1based - 1
            if global_track_0based < len(style.midi_tracks):
                track = style.midi_tracks[global_track_0based]
                cv0_tracks.append((m.type, m.track_number, global_track_0based, track))

print("\nPistes Variation1 CV[0] (via TrackMapping.indices):")
for t, tn, gi, trk in cv0_tracks:
    print(f"  mapping_type={t}  track_number={tn}  ->  global[{gi}]={trk.chunk_type}  "
          f"timescale={trk.time_scale}  {len(trk.events)} events")
    
    # Events avec delta
    abs_tick = 0
    for evt in trk.events[:15]:
        if evt.type == 'delta':
            abs_tick += evt.delta
        else:
            print(f"    t={abs_tick:6d}  {evt}")

print()
# Test avec offset depuis start de Variation1
print("Pistes Variation1 CV[0] (via offset + TrackMapping.indices):")
for cv_idx, mt in elem11.master_tracks[:1]:
    for i, m in enumerate(mt.cv_track_mappings):
        abs_pos = offset11 + i  # position absolue dans TrackMapping
        if abs_pos < len(tm.indices):
            global_1based = tm.indices[abs_pos]
            global_0based = global_1based - 1
            if 0 <= global_0based < len(style.midi_tracks):
                trk = style.midi_tracks[global_0based]
                print(f"  i={i}  abs_pos={abs_pos}  TM[{abs_pos}]={global_1based}  "
                      f"global[{global_0based}]={trk.chunk_type}  ts={trk.time_scale}  {len(trk.events)} evts")
                abs_tick = 0
                for evt in trk.events[:10]:
                    if evt.type == 'delta':
                        abs_tick += evt.delta
                    else:
                        print(f"      t={abs_tick:6d}  {evt}")
