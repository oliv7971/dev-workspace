from tools.korf import read_bank
from tools.style_reader import parse_style
ref = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
sr = parse_style(ref.objects[0])
print(f'REF style {ref.toc[0].name!r}:')
for i, e in enumerate(sr.style_elements):
    print(f'  elem[{i:2}] cv_flags=0x{e.info.chord_variations_with_data:02x} cue={e.info.cue_mode} '
          f'ts={e.info.time_sig_numerator}/{e.info.time_sig_denominator} masters={len(e.master_tracks)}  '
          f'unk4={e.info.unknown4.hex(" ")} unk5={e.info.unknown5.hex(" ")}')

ours = read_bank(r'verif\TEST.SET\STYLE\USER01.STY')
so = parse_style(ours.objects[0])
print(f'\nOUR style {ours.toc[0].name!r}:')
for i, e in enumerate(so.style_elements):
    print(f'  elem[{i:2}] cv_flags=0x{e.info.chord_variations_with_data:02x} cue={e.info.cue_mode} '
          f'ts={e.info.time_sig_numerator}/{e.info.time_sig_denominator} masters={len(e.master_tracks)}  '
          f'unk4={e.info.unknown4.hex(" ")} unk5={e.info.unknown5.hex(" ")}')

# Also dump StyleInfo unknowns
print(f'\nREF StyleInfo: enabled=0x{sr.info.enabled_style_elements:04x} with_data=0x{sr.info.style_elements_with_data:04x} unknowns={sr.info.unknowns.hex(" ")}')
print(f'OUR StyleInfo: enabled=0x{so.info.enabled_style_elements:04x} with_data=0x{so.info.style_elements_with_data:04x} unknowns={so.info.unknowns.hex(" ")}')
