"""
Nettoyage de 01-SFTRF :
- Suppression des doublons (garder le chemin le plus court / hors dossiers secondaires)
- Suppression des Thumbs.db
- Suppression des .bak
- Suppression des ~$ (fichiers temporaires Office)
- Suppression des .log

Usage:
  python cleanup_sftrf.py            # Dry-run
  python cleanup_sftrf.py --execute  # Exécution réelle
"""
import os
import sys
import sqlite3

DB = "./reports/inventory_sftrf.db"
BASE = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\01-SFTRF"

DRY_RUN = "--execute" not in sys.argv

def format_size(b):
    for u in ['o','Ko','Mo','Go','To']:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024

conn = sqlite3.connect(DB)
cur = conn.cursor()

# ═══════════════════════════════════════════════════════════════
# PARTIE 1 : DOUBLONS
# ═══════════════════════════════════════════════════════════════
print("=" * 70)
print("PARTIE 1 : SUPPRESSION DES DOUBLONS")
print("=" * 70)

cur.execute("SELECT hash_md5, size, file_count FROM duplicate_groups ORDER BY wasted_space DESC")
groups = cur.fetchall()

dup_delete = []
dup_keep = []

for hash_md5, size, file_count in groups:
    cur.execute("SELECT path FROM files WHERE hash_md5 = ? AND size = ?", (hash_md5, size))
    paths = [r[0] for r in cur.fetchall()]
    if len(paths) < 2:
        continue
    
    def score(p):
        s = 0
        lp = p.lower()
        # Prefer keeping originals, delete copies/recaps
        if 'copie de ' in lp or 'copy of ' in lp: s += 1000
        if '60-projets recap' in lp: s += 500
        if '_aclasser' in lp: s += 400
        if 'backup' in lp: s += 300
        if 'old' in lp or 'ancien' in lp: s += 200
        if 'nouveau dossier' in lp: s += 100
        s += len(p)  # shorter path = likely original
        return s
    
    paths.sort(key=score)
    dup_keep.append(paths[0])
    dup_delete.extend(paths[1:])

total_dup_size = 0
for p in dup_delete:
    cur.execute("SELECT size FROM files WHERE path = ?", (p,))
    row = cur.fetchone()
    if row:
        total_dup_size += row[0]

print(f"  Doublons à supprimer : {len(dup_delete)} fichiers, {format_size(total_dup_size)}")
print(f"  Fichiers conservés   : {len(dup_keep)}")

# Show some examples
print("\n  Exemples de suppressions :")
examples = [(p, cur.execute("SELECT size FROM files WHERE path = ?", (p,)).fetchone()) for p in dup_delete[:10]]
for p, row in examples:
    if row:
        short = p.replace(BASE + "\\", "")
        print(f"    SUPPR: {short[:85]}  ({format_size(row[0])})")

# ═══════════════════════════════════════════════════════════════
# PARTIE 2 : THUMBS.DB
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PARTIE 2 : THUMBS.DB")
print("=" * 70)

cur.execute("SELECT path, size FROM files WHERE LOWER(filename) = 'thumbs.db'")
thumbs_files = cur.fetchall()
thumbs_paths = [r[0] for r in thumbs_files]
thumbs_size = sum(r[1] for r in thumbs_files)
print(f"  Thumbs.db : {len(thumbs_paths)} fichiers, {format_size(thumbs_size)}")

# ═══════════════════════════════════════════════════════════════
# PARTIE 3 : .BAK
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PARTIE 3 : FICHIERS .BAK")
print("=" * 70)

cur.execute("SELECT path, size FROM files WHERE extension = '.bak'")
bak_files = cur.fetchall()
bak_paths = [r[0] for r in bak_files]
bak_size = sum(r[1] for r in bak_files)
print(f"  .bak : {len(bak_paths)} fichiers, {format_size(bak_size)}")

# ═══════════════════════════════════════════════════════════════
# PARTIE 4 : ~$ FICHIERS OFFICE TEMP
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PARTIE 4 : FICHIERS TEMPORAIRES OFFICE (~$)")
print("=" * 70)

cur.execute("SELECT path, size FROM files WHERE filename LIKE '~$%'")
office_files = cur.fetchall()
office_paths = [r[0] for r in office_files]
office_size = sum(r[1] for r in office_files)
print(f"  ~$ fichiers : {len(office_paths)} fichiers, {format_size(office_size)}")

# ═══════════════════════════════════════════════════════════════
# PARTIE 5 : .LOG
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PARTIE 5 : FICHIERS .LOG")
print("=" * 70)

cur.execute("SELECT path, size FROM files WHERE extension = '.log'")
log_files = cur.fetchall()
log_paths = [r[0] for r in log_files]
log_size = sum(r[1] for r in log_files)
print(f"  .log : {len(log_paths)} fichiers, {format_size(log_size)}")

# ═══════════════════════════════════════════════════════════════
# RÉSUMÉ
# ═══════════════════════════════════════════════════════════════
all_delete = set(dup_delete) | set(thumbs_paths) | set(bak_paths) | set(office_paths) | set(log_paths)
total_size = total_dup_size + thumbs_size + bak_size + office_size + log_size

print("\n" + "=" * 70)
print("RÉSUMÉ TOTAL")
print("=" * 70)
print(f"  Doublons          : {len(dup_delete):5d} fichiers, {format_size(total_dup_size)}")
print(f"  Thumbs.db         : {len(thumbs_paths):5d} fichiers, {format_size(thumbs_size)}")
print(f"  .bak              : {len(bak_paths):5d} fichiers, {format_size(bak_size)}")
print(f"  ~$ Office temp    : {len(office_paths):5d} fichiers, {format_size(office_size)}")
print(f"  .log              : {len(log_paths):5d} fichiers, {format_size(log_size)}")
print(f"  ─────────────────────────────────────────")
print(f"  TOTAL             : {len(all_delete):5d} fichiers, {format_size(total_size)}")

if DRY_RUN:
    print("\n🔍 DRY-RUN : aucun fichier supprimé.")
    print("   Relancez avec --execute pour supprimer.")
else:
    print(f"\n🗑️  SUPPRESSION EN COURS...")
    deleted = 0
    errors = 0
    freed = 0
    
    for path in sorted(all_delete):
        try:
            if os.path.isfile(path):
                size = os.path.getsize(path)
                os.remove(path)
                deleted += 1
                freed += size
                if deleted % 500 == 0:
                    print(f"  ... {deleted} fichiers supprimés ({format_size(freed)})")
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  ⚠️  Erreur: {e}")
    
    print(f"\n✅ Terminé !")
    print(f"  Fichiers supprimés : {deleted}")
    print(f"  Espace libéré      : {format_size(freed)}")
    if errors:
        print(f"  Erreurs            : {errors}")

conn.close()
