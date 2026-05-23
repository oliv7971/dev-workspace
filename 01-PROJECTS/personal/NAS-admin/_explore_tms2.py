"""Détails TMS : fichier manquant de CHAT2, et analyse des .zip."""
import sqlite3
import os

DB = r'inventaires/inventaire_33-TUNNEL DU CHAT.db'
BASE = '\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\33-TUNNEL DU CHAT\\TMS\\'
NAS_TMS = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT\TMS'

conn = sqlite3.connect(DB)
c = conn.cursor()

# 1. Quel est le 1 fichier de CHAT2 pas dans CHAT ?
prefix1 = BASE + '270616_CHAT\\'
prefix2 = BASE + '270616_CHAT2\\'

c.execute("SELECT filename, size, hash_md5 FROM files WHERE path LIKE ?", (prefix1 + '%',))
f1 = c.fetchall()
h1 = {h for _, _, h in f1 if h}
ns1 = {(fn, sz) for fn, sz, _ in f1}

c.execute("SELECT path, filename, size, hash_md5 FROM files WHERE path LIKE ?", (prefix2 + '%',))
f2 = c.fetchall()

print("=== Fichier(s) de 270616_CHAT2 absents de 270616_CHAT ===")
for path, fn, sz, h in f2:
    if not ((h and h in h1) or (fn, sz) in ns1):
        rel = path[len(prefix2):]
        print(f"  {rel} ({fn}, {sz} octets, hash={h})")

# 2. Taille réelle des .zip sur le disque
print("\n=== Fichiers .zip dans TMS (taille réelle) ===")
for name in os.listdir(NAS_TMS):
    if name.endswith('.zip'):
        path = os.path.join(NAS_TMS, name)
        sz = os.path.getsize(path)
        print(f"  {name}: {sz/1073741824:.2f} Go")

# 3. Résumé : combien de Go on peut récupérer
print("\n=== POTENTIEL DE NETTOYAGE ===")
# CHAT2 (25.43 Go) est 99% dans CHAT → supprimable après fusion 1 fichier
# Les .zip sont probablement des archives des dossiers → vérifiable
c.execute("SELECT SUM(size) FROM files WHERE path LIKE ?", (prefix2 + '%',))
sz_chat2 = c.fetchone()[0] / 1073741824
print(f"  270616_CHAT2: {sz_chat2:.1f} Go → supprimable (99% inclus dans CHAT)")

# Taille des zip
total_zip = 0
for name in os.listdir(NAS_TMS):
    if name.endswith('.zip'):
        total_zip += os.path.getsize(os.path.join(NAS_TMS, name))
print(f"  Fichiers .zip: {total_zip/1073741824:.1f} Go → probablement archives des mêmes données")
print(f"  TOTAL potentiel: {sz_chat2 + total_zip/1073741824:.1f} Go")

# 4. Les .pts et .zfs c'est quoi ?
print("\n=== Fichiers .pts et .zfs (les plus lourds) ===")
c.execute("""SELECT extension, COUNT(*), ROUND(SUM(size)/1073741824.0, 1)
FROM files WHERE path LIKE ? AND extension IN ('pts', 'zfs')
GROUP BY extension""", (BASE + '%',))
for ext, cnt, go in c.fetchall():
    print(f"  .{ext}: {cnt} fichiers, {go} Go")

# Vérifier les doublons de .pts dans CHAT (les mêmes scans en double ?)
print("\n=== Doublons .pts dans 270616_CHAT ===")
c.execute("""SELECT hash_md5, COUNT(*) as cnt, ROUND(SUM(size)/1073741824.0, 2) 
FROM files WHERE path LIKE ? AND extension = 'pts' AND hash_md5 IS NOT NULL
GROUP BY hash_md5 HAVING cnt > 1 ORDER BY SUM(size) DESC""", (prefix1 + '%',))
dupes = c.fetchall()
if dupes:
    total_dup_go = sum(go * (cnt - 1) / cnt for _, cnt, go in dupes)
    print(f"  {len(dupes)} groupes de doublons .pts")
    print(f"  Go récupérables: ~{total_dup_go:.1f}")
else:
    print("  Aucun doublon .pts par hash dans 270616_CHAT")

# Pareil pour .zfs
print("\n=== Doublons .zfs dans 270616_CHAT ===")
c.execute("""SELECT hash_md5, COUNT(*) as cnt, ROUND(SUM(size)/1073741824.0, 2)
FROM files WHERE path LIKE ? AND extension = 'zfs' AND hash_md5 IS NOT NULL
GROUP BY hash_md5 HAVING cnt > 1 ORDER BY SUM(size) DESC""", (prefix1 + '%',))
dupes = c.fetchall()
if dupes:
    total_dup_go = sum(go * (cnt - 1) / cnt for _, cnt, go in dupes)
    print(f"  {len(dupes)} groupes de doublons .zfs")
    print(f"  Go récupérables: ~{total_dup_go:.1f}")
else:
    print("  Aucun doublon .zfs par hash dans 270616_CHAT")

conn.close()
