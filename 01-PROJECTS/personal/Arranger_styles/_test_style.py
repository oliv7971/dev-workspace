from tools.korf import read_bank, ObjectType
from tools.style_reader import parse_style, dump_style

bank = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')

style_entries = [(i, e) for i, e in enumerate(bank.toc) if e.object_type == ObjectType.Style]
print(f'{len(style_entries)} styles dans la banque\n')

# Tester les 3 premiers styles
for idx, (i, e) in enumerate(style_entries[:3]):
    print(f'{"="*60}')
    print(f'Style [{i}] "{e.name}"')
    try:
        style = parse_style(bank.objects[i])
        dump_style(style)
    except Exception as ex:
        import traceback
        print(f'  ERREUR: {ex}')
        traceback.print_exc()
    print()
