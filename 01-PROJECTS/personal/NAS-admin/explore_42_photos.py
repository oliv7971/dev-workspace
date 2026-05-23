import os

base = r'\\Nas_louhans_2\01-ds420-data\42-PHOTOS'
items = []
for e in os.scandir(base):
    try:
        if e.is_dir(follow_symlinks=False):
            n = 0
            c = 0
            for r, d, fs in os.walk(e.path):
                d[:] = [x for x in d if x not in ('@eaDir', '#recycle')]
                for f in fs:
                    try:
                        n += os.path.getsize(os.path.join(r, f))
                        c += 1
                    except OSError:
                        pass
            items.append((n, c, 'DIR', e.name))
        else:
            items.append((e.stat().st_size, 1, 'FILE', e.name))
    except OSError:
        pass

items.sort(reverse=True)
total_sz = sum(x[0] for x in items)
total_f  = sum(x[1] for x in items)

print(f"TOTAL : {total_sz/1024**3:.1f} Go, {total_f} fichiers, {len(items)} entrees")
print()
print(f"{'Type':<5} {'Taille':>9}  {'Fich':>5}  Nom")
print("-" * 80)
for sz, cnt, t, n in items:
    print(f"{t:<5} {sz/1024**2:8.0f} Mo  {cnt:5}  {n}")
