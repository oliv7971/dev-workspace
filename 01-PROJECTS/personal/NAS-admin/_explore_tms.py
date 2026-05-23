"""Analyse détaillée du dossier TMS (106 Go) dans 33-TUNNEL DU CHAT."""
import sqlite3
from datetime import datetime
from collections import defaultdict

DB = r'inventaires/inventaire_33-TUNNEL DU CHAT.db'
BASE = '\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\33-TUNNEL DU CHAT\\TMS\\'

conn = sqlite3.connect(DB)
c = conn.cursor()

# 1. Sous-dossiers L2
print("=" * 90)
print("ANALYSE TMS — Structure L2")
print("=" * 90)
c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, CASE WHEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92)) > 0 
        THEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1 
        ELSE LENGTH(SUBSTR(path, LENGTH(?)+1)) END) as subfolder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go,
    MIN(modified_time), MAX(modified_time)
FROM files WHERE path LIKE ? || '%'
GROUP BY subfolder ORDER BY SUM(size) DESC""", (BASE, BASE, BASE, BASE, BASE))

def ts(t):
    try: return datetime.fromtimestamp(float(t)).strftime('%Y-%m-%d')
    except: return '?'

folders = []
print(f"  {'Dossier':<55} {'Fich':>6} {'Go':>8} {'De':>12} {'À':>12}")
print("-" * 95)
for r in c.fetchall():
    folders.append((r[0], r[1], r[2]))
    print(f"  {r[0]:<55} {r[1]:>6} {r[2]:>8} {ts(r[3]):>12} {ts(r[4]):>12}")

# 2. Extensions dans les 2 gros dossiers
for folder_name in ['270616_CHAT', '270616_CHAT2']:
    prefix = BASE + folder_name + '\\'
    c.execute("""SELECT extension, COUNT(*), ROUND(SUM(size)/1073741824.0, 2)
    FROM files WHERE path LIKE ? || '%'
    GROUP BY extension ORDER BY SUM(size) DESC LIMIT 15""", (prefix,))
    print(f"\n  Extensions dans {folder_name}:")
    for ext, cnt, go in c.fetchall():
        print(f"    .{ext or '(sans)':<10} {cnt:>6} fich  {go:>6} Go")

# 3. Overlap entre 270616_CHAT et 270616_CHAT2
print("\n" + "=" * 90)
print("OVERLAP: 270616_CHAT vs 270616_CHAT2")
print("=" * 90)

prefix1 = BASE + '270616_CHAT\\'
prefix2 = BASE + '270616_CHAT2\\'

c.execute("SELECT filename, size, hash_md5 FROM files WHERE path LIKE ?", (prefix1 + '%',))
f1 = c.fetchall()
c.execute("SELECT filename, size, hash_md5 FROM files WHERE path LIKE ?", (prefix2 + '%',))
f2 = c.fetchall()

h1 = {h for _, _, h in f1 if h}
h2 = {h for _, _, h in f2 if h}
ns1 = {(fn, sz) for fn, sz, _ in f1}
ns2 = {(fn, sz) for fn, sz, _ in f2}

# CHAT2 ⊂ CHAT ?
m2in1 = sum(1 for fn, sz, h in f2 if (h and h in h1) or (fn, sz) in ns1)
print(f"  270616_CHAT:  {len(f1)} fichiers, {sum(s for _, s, _ in f1)/1073741824:.1f} Go")
print(f"  270616_CHAT2: {len(f2)} fichiers, {sum(s for _, s, _ in f2)/1073741824:.1f} Go")
print(f"  CHAT2 → CHAT: {m2in1}/{len(f2)} trouvés ({m2in1*100//len(f2) if f2 else 0}%)")
m1in2 = sum(1 for fn, sz, h in f1 if (h and h in h2) or (fn, sz) in ns2)
print(f"  CHAT → CHAT2: {m1in2}/{len(f1)} trouvés ({m1in2*100//len(f1) if f1 else 0}%)")

# 4. Les .zip — sont-ce des archives des dossiers ?
print("\n" + "=" * 90)
print("FICHIERS .ZIP dans TMS")
print("=" * 90)
c.execute("SELECT path, filename, size, modified_time FROM files WHERE path LIKE ? AND extension = 'zip'",
          (BASE + '%',))
for path, fn, sz, mt in c.fetchall():
    print(f"  {fn}: {sz/1073741824:.1f} Go, modifié {ts(mt)}")

# 5. Sous-structure de 270616_CHAT (L3)
print("\n" + "=" * 90)
print("Sous-structure de 270616_CHAT/ (L3)")
print("=" * 90)
prefix_chat = BASE + '270616_CHAT\\'
c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, CASE WHEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92)) > 0 
        THEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1 
        ELSE LENGTH(SUBSTR(path, LENGTH(?)+1)) END) as subfolder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go,
    MIN(modified_time), MAX(modified_time)
FROM files WHERE path LIKE ? || '%'
GROUP BY subfolder ORDER BY SUM(size) DESC LIMIT 30""", 
    (prefix_chat, prefix_chat, prefix_chat, prefix_chat, prefix_chat))
for r in c.fetchall():
    print(f"  {r[0]:<55} {r[1]:>6} {r[2]:>6} Go  {ts(r[3])} → {ts(r[4])}")

# 6. Sous-structure de 270616_CHAT2/ (L3)
print("\n" + "=" * 90)
print("Sous-structure de 270616_CHAT2/ (L3)")
print("=" * 90)
prefix_chat2 = BASE + '270616_CHAT2\\'
c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, CASE WHEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92)) > 0 
        THEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1 
        ELSE LENGTH(SUBSTR(path, LENGTH(?)+1)) END) as subfolder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go,
    MIN(modified_time), MAX(modified_time)
FROM files WHERE path LIKE ? || '%'
GROUP BY subfolder ORDER BY SUM(size) DESC LIMIT 30""", 
    (prefix_chat2, prefix_chat2, prefix_chat2, prefix_chat2, prefix_chat2))
for r in c.fetchall():
    print(f"  {r[0]:<55} {r[1]:>6} {r[2]:>6} Go  {ts(r[3])} → {ts(r[4])}")

# 7. Overlap entre les petits dossiers et les gros
print("\n" + "=" * 90)
print("PETITS DOSSIERS vs 270616_CHAT")
print("=" * 90)
small_folders = ['Tunnel du chat v20150807', '02-ROUTIER NOUVEAU AXE- OB 20170420',
                 'ROUTIER NOUVEAU AXE', '01-ROUTIER NOUVEAU AXE- PVDZ 20170418',
                 '50-GALERIE SECURITE', '10-CARNEAUX',
                 '04-ROUTIER AXE POUR BOULONS CARNEAUX', '99-Profils théo par GGC']

all_chat_hashes = h1 | h2
all_chat_ns = ns1 | ns2

for sf in small_folders:
    prefix_sf = BASE + sf + '\\'
    c.execute("SELECT filename, size, hash_md5 FROM files WHERE path LIKE ?", (prefix_sf + '%',))
    files = c.fetchall()
    if not files:
        continue
    matched = sum(1 for fn, sz, h in files if (h and h in all_chat_hashes) or (fn, sz) in all_chat_ns)
    pct = matched * 100 // len(files) if files else 0
    print(f"  {sf:<55} {len(files):>4} fich, {matched} dans CHAT/CHAT2 ({pct}%)")

conn.close()
