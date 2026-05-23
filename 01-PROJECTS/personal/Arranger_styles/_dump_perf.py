from tools.korf import read_bank, ObjectType
import struct

bank = read_bank('données etude/KORG (PA4x musikant)/PA4X (KORG).SET/STYLE/BANK01.STY')

# Find the first StylePerformances entry and its object index
print('TOC entries:', len(bank.toc))
print('Objects:', len(bank.objects))

# Objects are in same order as TOC entries
for i, e in enumerate(bank.toc):
    if e.object_type == ObjectType.StylePerformances:
        obj = bank.objects[i]
        print(f'\nStylePerformances[{i}] for style at pos={e.pos}, name={e.name!r}')
        print(f'  Size: {len(obj)} bytes')
        print(f'  Hex (first 64): {obj[:64].hex()}')
        print(f'  Hex (all):')
        for off in range(0, len(obj), 16):
            chunk = obj[off:off+16]
            h = ' '.join(f'{b:02x}' for b in chunk)
            a = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            print(f'  {off:04x}: {h:<47}  {a}')
        break  # Just first one

# Also check second one
count = 0
for i, e in enumerate(bank.toc):
    if e.object_type == ObjectType.StylePerformances:
        count += 1
        obj = bank.objects[i]
        # Find one with non-empty name
        if e.name:
            print(f'\nStylePerformances[{i}] with name={e.name!r}')
            print(f'  Size: {len(obj)} bytes')
            for off in range(0, len(obj), 16):
                chunk = obj[off:off+16]
                h = ' '.join(f'{b:02x}' for b in chunk)
                a = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                print(f'  {off:04x}: {h:<47}  {a}')
            break
        if count > 10:
            break
