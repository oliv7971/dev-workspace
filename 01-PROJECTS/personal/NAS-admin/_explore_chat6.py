"""Vérif overlap 99-olivier et 2017 vs reste."""
import sqlite3
conn = sqlite3.connect(r'inventaires/inventaire_33-TUNNEL DU CHAT.db')
c = conn.cursor()
BASE = '\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\33-TUNNEL DU CHAT\\'

def get_files(prefix):
    c.execute("SELECT path, filename, size, hash_md5 FROM files WHERE path LIKE ?", (prefix + '%',))
    return c.fetchall()

# 1. 99-olivier L1 vs 20150904-CHAT\99-olivier
print("=== 99-olivier (L1) vs 20150904-CHAT\\99-olivier ===")
f_main = get_files(BASE + '99-olivier\\')
f_sub = get_files(BASE + '20150904-CHAT\\99-olivier\\')
print(f"  L1 99-olivier: {len(f_main)} fichiers")
print(f"  20150904-CHAT\\99-olivier: {len(f_sub)} fichiers")

h_sub = {h for _, _, _, h in f_sub if h}
ns_sub = {(fn, sz) for _, fn, sz, _ in f_sub}
matched = 0
missing = []
for p, fn, sz, h in f_main:
    if (h and h in h_sub) or (fn, sz) in ns_sub:
        matched += 1
    else:
        missing.append((fn, sz))
print(f"  L1 → sub: {matched} trouvés, {len(missing)} manquants")
if len(missing) <= 20:
    for fn, sz in missing[:20]:
        print(f"    → {fn} ({sz//1024 if sz else 0} Ko)")

h_main = {h for _, _, _, h in f_main if h}
ns_main = {(fn, sz) for _, fn, sz, _ in f_main}
matched2 = 0
missing2 = []
for p, fn, sz, h in f_sub:
    if (h and h in h_main) or (fn, sz) in ns_main:
        matched2 += 1
    else:
        missing2.append((fn, sz))
print(f"  sub → L1: {matched2} trouvés, {len(missing2)} manquants")
if len(missing2) <= 20:
    for fn, sz in missing2[:20]:
        print(f"    → {fn} ({sz//1024 if sz else 0} Ko)")

# 2. Dossier 2017/ — vérifier si son contenu est dans les dossiers correspondants de L1
print("\n=== Analyse du dossier 2017/ ===")
f_2017 = get_files(BASE + '2017\\')
print(f"  2017/: {len(f_2017)} fichiers")

# Sous-dossiers de 2017
sub_dirs = {}
for p, fn, sz, h in f_2017:
    rel = p[len(BASE + '2017\\'):]
    top = rel.split('\\')[0] if '\\' in rel else '_racine'
    sub_dirs.setdefault(top, []).append((fn, sz, h))

# Tous les autres fichiers (hors 2017/ et dossiers déjà supprimés en P1)
all_other = get_files(BASE)
# Exclure 2017/ et dossiers P1 supprimés
other_hashes = set()
other_ns = set()
for p, fn, sz, h in all_other:
    rel = p[len(BASE):]
    top = rel.split('\\')[0]
    if top == '2017':
        continue
    if h:
        other_hashes.add(h)
    other_ns.add((fn, sz))

print(f"\nSous-dossiers de 2017/ vs le reste:")
for sd in sorted(sub_dirs.keys()):
    files = sub_dirs[sd]
    m = sum(1 for fn, sz, h in files if (h and h in other_hashes) or (fn, sz) in other_ns)
    miss = len(files) - m
    pct = m * 100 // len(files) if files else 0
    print(f"  2017\\{sd}: {len(files)} fich, {m} trouvés ({pct}%), {miss} manquants")

# 3. tunnel-chat — quels sous-dossiers ?
print("\n=== tunnel-chat/ structure ===")
f_tc = get_files(BASE + 'tunnel-chat\\')
sub_dirs2 = {}
for p, fn, sz, h in f_tc:
    rel = p[len(BASE + 'tunnel-chat\\'):]
    top = rel.split('\\')[0] if '\\' in rel else '_racine'
    sub_dirs2.setdefault(top, []).append((fn, sz, h))
for sd in sorted(sub_dirs2.keys(), key=lambda x: -len(sub_dirs2[x])):
    print(f"  tunnel-chat\\{sd}: {len(sub_dirs2[sd])} fich")

# tunnel-chat vs 03-tunnel chat
print("\n=== tunnel-chat vs 03-tunnel chat ===")
f_03 = get_files(BASE + '03-tunnel chat\\')
h_03 = {h for _, _, _, h in f_03 if h}
ns_03 = {(fn, sz) for _, fn, sz, _ in f_03}
m_tc = sum(1 for fn, sz, h in [(fn, sz, h) for _, fn, sz, h in f_tc] if (h and h in h_03) or (fn, sz) in ns_03)
print(f"  tunnel-chat ({len(f_tc)} fich) → 03-tunnel chat: {m_tc} trouvés, {len(f_tc) - m_tc} manquants")

# tunnel-chat vs TMS
h_tms = set()
ns_tms = set()
for p, fn, sz, h in all_other:
    if p.startswith(BASE + 'TMS\\'):
        if h: h_tms.add(h)
        ns_tms.add((fn, sz))
m_tms = sum(1 for fn, sz, h in [(fn, sz, h) for _, fn, sz, h in f_tc] if (h and h in h_tms) or (fn, sz) in ns_tms)
print(f"  tunnel-chat ({len(f_tc)} fich) → TMS: {m_tms} trouvés, {len(f_tc) - m_tms} manquants")

conn.close()
