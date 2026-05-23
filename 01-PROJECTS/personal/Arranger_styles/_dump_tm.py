"""Compare TrackMapping indices structure."""
from tools.korf import read_bank
from tools.style_reader import parse_style

ref = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
sr = parse_style(ref.objects[0])
ours = read_bank(r'verif\TEST.SET\STYLE\USER01.STY')
so = parse_style(ours.objects[0])

print('REF TrackMapping:')
print(f'  n_midi_tracks={sr.track_mapping.n_midi_tracks} indices_count={len(sr.track_mapping.indices)}')
print(f'  first 30 indices: {sr.track_mapping.indices[:30]}')
print(f'  unique indices: {len(set(sr.track_mapping.indices))}')

print('\nOUR TrackMapping:')
print(f'  n_midi_tracks={so.track_mapping.n_midi_tracks} indices_count={len(so.track_mapping.indices)}')
print(f'  first 30 indices: {so.track_mapping.indices[:30]}')
print(f'  unique indices: {len(set(so.track_mapping.indices))}')

# In REF, sum the cv_track_mappings counts across all elements
def total_cv_mappings(s):
    n = 0
    for e in s.style_elements:
        for cv, mt in e.master_tracks:
            n += len(mt.cv_track_mappings)
    return n

print(f'\nREF: total cv_mappings across elements = {total_cv_mappings(sr)} (should match indices_count={len(sr.track_mapping.indices)})')
print(f'OUR: total cv_mappings across elements = {total_cv_mappings(so)} (should match indices_count={len(so.track_mapping.indices)})')
