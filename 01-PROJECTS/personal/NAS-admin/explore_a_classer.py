import os

BASE = r'\\Nas_louhans_2\01-ds420-data\90-a_classer'

items = []
for entry in os.scandir(BASE):
    try:
        if entry.is_dir(follow_symlinks=False):
            total = 0
            count = 0
            for root, dirs, files in os.walk(entry.path):
                dirs[:] = [d for d in dirs if d not in ('@eaDir', '#recycle')]
                for f in files:
                    try:
                        total += os.path.getsize(os.path.join(root, f))
                        count += 1
                    except OSError:
                        pass
            items.append((total, count, 'DIR ', entry.name))
        else:
            size = entry.stat().st_size
            items.append((size, 1, 'FILE', entry.name))
    except OSError:
        pass

items.sort(reverse=True)
print(f"{'Type':<5} {'Taille':>10}  {'Fichiers':>8}  Nom")
print("-"*80)
for size, count, typ, name in items:
    print(f"{typ}  {size/1024**2:9.1f} Mo  {count:8}  {name}")
