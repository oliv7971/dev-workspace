from tools.korf import read_bank, dump_chunks, ObjectType

bank = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')

style_entries = [(i,e) for i,e in enumerate(bank.toc) if e.object_type == ObjectType.Style]
print(f'{len(style_entries)} styles trouves')
print()

i, e = style_entries[0]
print(f'=== Style [{i}] "{e.name}" ({len(bank.objects[i])} bytes) ===')
dump_chunks(bank.objects[i])
