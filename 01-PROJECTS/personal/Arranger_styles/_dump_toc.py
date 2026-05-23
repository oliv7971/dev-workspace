from tools.korf import read_bank, ObjectType
bank = read_bank('données etude/KORG (PA4x musikant)/PA4X (KORG).SET/STYLE/BANK01.STY')
print('TOC entries:', len(bank.toc))
for e in bank.toc:
    print(f'  [{e.pos:2d}] type={ObjectType.name(e.object_type):20s} bank={e.bank_number} name={e.name!r}')
print()
print('Objects in bank:', len(bank.objects))
