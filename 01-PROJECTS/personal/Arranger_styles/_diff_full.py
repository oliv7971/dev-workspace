ref = open(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY','rb').read()
h = open(r'verif\TEST_H_RESTYLE.SET\STYLE\FAVORITE01.STY','rb').read()
print('REF size:', len(ref))
print('H size:  ', len(h))
print('Diff size:', len(h) - len(ref))
n = min(len(ref), len(h))
i = 0
while i < n and ref[i] == h[i]: i += 1
print(f'First diff @ 0x{i:x} ({i})')
print(f'  ref: {ref[i:i+32].hex(" ")}')
print(f'  h  : {h[i:i+32].hex(" ")}')
print(f'\nContext before:')
print(f'  ref: {ref[max(0,i-32):i].hex(" ")}')
print(f'  h  : {h[max(0,i-32):i].hex(" ")}')
