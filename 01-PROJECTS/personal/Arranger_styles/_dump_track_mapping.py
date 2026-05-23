"""Dump du contenu des Meta(0x7E) et de la structure TrackMapping."""
import sys
sys.path.insert(0, '.')
from tools.korf import read_bank
from tools.style_reader import parse_style, STYLE_ELEMENT_NAMES, decode_korg_midi

bank = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
style = parse_style(bank.objects[0])
print(f"Style: {style.info.name!r}")
print()

# Contenu des Meta(0x7E) dans le premier StyleElement
print("=== Meta(0x7E) dans StyleElement[0] (Intro1) ===")
elem = style.style_elements[0]
for cv_idx, mt in elem.master_tracks[:2]:
    print(f"\n  CV[{cv_idx}]: {len(mt.cv_track_mappings)} mappings")
    for m in mt.cv_track_mappings:
        print(f"    mapping type={m.type} track={m.track_number}")
    print(f"  Events:")
    for e in mt.events:
        if e.type == 'meta':
            print(f"    Meta(0x{e.meta_type:02X}) data={e.meta_data.hex()} [{len(e.meta_data)} bytes]")
        elif e.type == 'delta':
            if e.delta: print(f"    Delta({e.delta})")
        else:
            print(f"    {e}")

print()
# TrackMapping details
print("=== TrackMapping ===")
tm = style.track_mapping
print(f"  n_midi_tracks={tm.n_midi_tracks}  n_indices={len(tm.indices)}")
print(f"  15 elements * ~8 CVs * ~8 tracks = {15*8*8} max tracks")
# Comment les indices se groupent-ils par element?
# Pattern: par bloc de N selon les CVs?
# Nombre de CVs par element
print()
print("  CVs par element:")
total_mappings_per_elem = []
for i, elem in enumerate(style.style_elements):
    n_cvs = len(elem.master_tracks)
    tracks_per_cv = [len(mt.cv_track_mappings) for _, mt in elem.master_tracks]
    total = sum(tracks_per_cv)
    name = STYLE_ELEMENT_NAMES[i] if i < len(STYLE_ELEMENT_NAMES) else f'?{i}'
    print(f"  [{i:2d}] {name:<12s}  {n_cvs} CVs  tracks/CV={tracks_per_cv}  total={total}")
    total_mappings_per_elem.append(total)

print(f"\n  TOTAL mappings: {sum(total_mappings_per_elem)}")
print(f"  TrackMapping indices count: {len(tm.indices)}")

# Vérifier si les indices contiennent des 0 (padding?) + comment indexer
print()
uniq = sorted(set(tm.indices))
print(f"  Valeurs uniques dans indices: {uniq[:20]}...  max={max(tm.indices)}")
print(f"  Nb de zeros: {tm.indices.count(0)}")
print(f"  Indices[0:20]: {tm.indices[:20]}")
