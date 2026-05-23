"""Diff REF style[0] vs round-trip byte-by-byte to find writer bug."""
from tools.korf import read_bank
from tools.style_reader import parse_style
from tools.style_writer import encode_style

ref = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
orig = ref.objects[0]
st = parse_style(orig)
re = encode_style(st)

print(f'orig={len(orig)} re={len(re)} diff={len(re)-len(orig)}')

# find first diff
n = min(len(orig), len(re))
i = 0
while i < n and orig[i] == re[i]:
    i += 1
print(f'\nFirst diff at offset 0x{i:x}')
print(f'  orig[{i:x}..{i+32:x}]: {orig[i:i+32].hex(" ")}')
print(f'  re  [{i:x}..{i+32:x}]: {re[i:i+32].hex(" ")}')

# context before
print(f'\nContext before:')
print(f'  orig[{i-16:x}..{i:x}]: {orig[max(0,i-16):i].hex(" ")}')
