"""État actuel du dossier TMS après phase 2e."""
import os

TMS = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT\TMS'

print("=== Contenu actuel de TMS/ ===\n")
entries = []
root_files = []
for name in sorted(os.listdir(TMS)):
    path = os.path.join(TMS, name)
    if os.path.isdir(path):
        count = sum(len(files) for _, _, files in os.walk(path))
        size = sum(os.path.getsize(os.path.join(d, f)) for d, _, files in os.walk(path) for f in files)
        entries.append((name, count, size, True))
    else:
        size = os.path.getsize(path)
        root_files.append((name, size))

entries.sort(key=lambda x: -x[2])
total_size = 0
print(f"  {'Dossier':<60} {'Fich':>6} {'Taille':>10}")
print("  " + "-" * 80)
for name, count, size, _ in entries:
    if size > 1073741824: sz = f"{size/1073741824:.1f} Go"
    elif size > 1048576: sz = f"{size/1048576:.0f} Mo"
    else: sz = f"{size/1024:.0f} Ko"
    print(f"  📁 {name:<57} {count:>6} {sz:>10}")
    total_size += size

if root_files:
    print(f"\n  Fichiers en racine de TMS/:")
    for name, size in root_files:
        total_size += size
        if size > 1048576: sz = f"{size/1048576:.0f} Mo"
        else: sz = f"{size/1024:.0f} Ko"
        print(f"  📄 {name:<57}        {sz:>10}")

print(f"\n  Total: {len(entries)} dossiers, {sum(e[1] for e in entries)} fichiers, {total_size/1073741824:.1f} Go")

# Détail de 270616_CHAT (le gros)
print(f"\n=== Sous-dossiers de 270616_CHAT/ ===\n")
chat_path = os.path.join(TMS, '270616_CHAT')
sub_entries = []
chat_root_files = 0
chat_root_size = 0
for name in sorted(os.listdir(chat_path)):
    path = os.path.join(chat_path, name)
    if os.path.isdir(path):
        count = sum(len(files) for _, _, files in os.walk(path))
        size = sum(os.path.getsize(os.path.join(d, f)) for d, _, files in os.walk(path) for f in files)
        sub_entries.append((name, count, size))
    else:
        chat_root_files += 1
        chat_root_size += os.path.getsize(path)

sub_entries.sort(key=lambda x: -x[2])
for name, count, size in sub_entries:
    if size > 1073741824: sz = f"{size/1073741824:.1f} Go"
    elif size > 1048576: sz = f"{size/1048576:.0f} Mo"
    else: sz = f"{size/1024:.0f} Ko"
    print(f"  📁 {name:<57} {count:>6} {sz:>10}")
if chat_root_files:
    print(f"  📄 ({chat_root_files} fichiers en racine)                                          {chat_root_size/1024:.0f} Ko")
