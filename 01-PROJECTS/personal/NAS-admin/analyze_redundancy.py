"""Analyse de redondance entre _A CLASSER et le reste de 11-TSGT"""
import sqlite3
from collections import defaultdict

conn = sqlite3.connect('./reports/inventory.db')

# Verifier le format des chemins en base
sample = conn.execute("SELECT path FROM files LIMIT 3").fetchall()
print("=== EXEMPLES DE CHEMINS EN BASE ===")
for (p,) in sample:
    print(f"  [{p}]")

# Séparer les fichiers en 2 groupes via un test simple sur le chemin
print("\n=== SEPARATION DES FICHIERS ===")
all_files = conn.execute("SELECT id, path, hash_md5, size FROM files WHERE hash_md5 IS NOT NULL").fetchall()

ref_files = []      # Hors _A CLASSER
ac_files = []       # Dans _A CLASSER

for fid, path, hash_md5, size in all_files:
    lower = path.lower()
    if '_a classer' in lower:
        ac_files.append((fid, path, hash_md5, size))
    else:
        ref_files.append((fid, path, hash_md5, size))

print(f"  Référence (hors _A CLASSER) : {len(ref_files)}")
print(f"  _A CLASSER                  : {len(ac_files)}")

ref_hashes = set(h for _, _, h, _ in ref_files)

# Grouper les fichiers de _A CLASSER par sous-dossier
def get_subfolder(path):
    lower = path.lower()
    idx = lower.find('_a classer')
    if idx == -1:
        return "(inconnu)"
    rest = path[idx + len('_A CLASSER') + 1:]
    first_sep = rest.find('\\')
    if first_sep == -1:
        return "(racine)"
    return rest[:first_sep]

zone_data = defaultdict(list)  # zone -> [(hash, size), ...]
for fid, path, hash_md5, size in ac_files:
    zone = get_subfolder(path)
    zone_data[zone].append((hash_md5, size))

print(f"\n=== ANALYSE PAR ZONE ===\n")
print(f"{'Zone':<30} {'Fich':>6} {'Taille':>10} {'Hash uniq':>10} {'Déjà dans ref':>14} {'Dupliq inter-zone':>18} {'UNIQUES':>10}")
print("-" * 110)

all_zone_hashes = {}
for zone, items in sorted(zone_data.items(), key=lambda x: -sum(s for _, s in x[1])):
    total_files = len(items)
    total_size = sum(s for _, s in items)
    unique_hashes = set(h for h, _ in items)
    in_ref = unique_hashes & ref_hashes
    all_zone_hashes[zone] = unique_hashes
    
    size_str = f"{total_size/1024/1024:.1f} Mo"
    print(f"{zone:<30} {total_files:>6} {size_str:>10} {len(unique_hashes):>10} {len(in_ref):>14} {'':>18} {'':>10}")

# Maintenant calculer les dupliqués inter-zones
print(f"\n=== ANALYSE INTER-ZONES ===\n")
print(f"{'Zone':<30} {'Hash uniq':>10} {'Dans réf':>10} {'%réf':>6} {'Dans autre zone':>16} {'UNIQUES':>10} {'%uniq':>6}")
print("-" * 100)

total_unique_only = 0
total_all = 0

for zone in sorted(all_zone_hashes, key=lambda z: -len(all_zone_hashes[z])):
    unique_hashes = all_zone_hashes[zone]
    in_ref = unique_hashes & ref_hashes
    
    in_other = set()
    for other_zone, other_hashes in all_zone_hashes.items():
        if other_zone != zone:
            in_other |= (unique_hashes & other_hashes)
    
    unique_only = unique_hashes - ref_hashes - in_other
    pct_ref = len(in_ref) / len(unique_hashes) * 100 if unique_hashes else 0
    pct_uniq = len(unique_only) / len(unique_hashes) * 100 if unique_hashes else 0
    
    total_unique_only += len(unique_only)
    total_all += len(unique_hashes)
    
    print(f"{zone:<30} {len(unique_hashes):>10} {len(in_ref):>10} {pct_ref:>5.0f}% {len(in_other):>16} {len(unique_only):>10} {pct_uniq:>5.0f}%")

print("-" * 100)
pct_total = total_unique_only / total_all * 100 if total_all else 0
print(f"{'TOTAL':<30} {total_all:>10} {'':>10} {'':>6} {'':>16} {total_unique_only:>10} {pct_total:>5.0f}%")

# Resume global
print(f"\n=== RESUME ===")
ac_all_hashes = set(h for h, _ in [(h, s) for _, _, h, s in ac_files])
in_ref_global = ac_all_hashes & ref_hashes
unique_global = ac_all_hashes - ref_hashes
print(f"  Hash uniques dans _A CLASSER : {len(ac_all_hashes)}")
print(f"  Déjà dans le reste de 11-TSGT: {len(in_ref_global)} ({len(in_ref_global)/len(ac_all_hashes)*100:.0f}%)")
print(f"  UNIQUES à _A CLASSER         : {len(unique_global)} ({len(unique_global)/len(ac_all_hashes)*100:.0f}%)")

# Combien de fichiers dans _A CLASSER sont des copies internes (meme hash, plusieurs occurrences dans _A CLASSER)?
from collections import Counter
hash_counts = Counter(h for h, _ in [(h, s) for _, _, h, s in ac_files])
internal_dups = sum(c - 1 for c in hash_counts.values() if c > 1)
print(f"  Doublons internes _A CLASSER  : {internal_dups} fichiers en trop")
