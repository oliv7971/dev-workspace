from tools.korf import read_bank, ObjectType
from tools.style_reader import parse_style

bank = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
style_entries = [(i, e) for i, e in enumerate(bank.toc) if e.object_type == ObjectType.Style]
print(f'{len(style_entries)} styles\n')

errors = 0
for i, e in style_entries:
    try:
        style = parse_style(bank.objects[i])
        elems = len(style.style_elements)
        tracks = len(style.midi_tracks)
        total_ev = sum(len(t.events) for t in style.midi_tracks)
        print(f'  OK  [{i:2d}] {e.name:<20s}  elements={elems:2d}  tracks={tracks:3d}  events={total_ev:5d}')
    except Exception as ex:
        errors += 1
        print(f'  ERR [{i:2d}] {e.name:<20s}  {ex}')

print(f'\n{len(style_entries) - errors}/{len(style_entries)} OK, {errors} erreurs')
