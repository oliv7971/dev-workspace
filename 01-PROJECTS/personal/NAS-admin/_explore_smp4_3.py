"""Analyse des archives dans 34-controle voussoirs SMP4."""
import sqlite3
import os

DB = r'inventaires/inventaire_34-controle voussoirs SMP4.db'
BASE = '\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\34-controle voussoirs SMP4\\'

conn = sqlite3.connect(DB)
c = conn.cursor()

# 1. Contenu du dossier ZIP/
print("=" * 100)
print("USINE-VOUSSOIRS-SMLP/ZIP/ — Contenu")
print("=" * 100)
prefix_zip = BASE + 'USINE-VOUSSOIRS-SMLP\\ZIP\\'
c.execute("""SELECT filename, extension, size, modified_time 
FROM files WHERE path LIKE ? ORDER BY size DESC""", (prefix_zip + '%',))
from datetime import datetime
def ts(t):
    try: return datetime.fromtimestamp(float(t)).strftime('%Y-%m-%d')
    except: return '?'

total_zip_size = 0
for fn, ext, sz, mt in c.fetchall():
    total_zip_size += sz
    print(f"  {fn:<65} {sz/1073741824:.2f} Go  {ts(mt)}")
print(f"\n  Total: {total_zip_size/1073741824:.1f} Go")

# 2. Le gros 11-SMP4.zip
print(f"\n{'=' * 100}")
print("_a_classer/11-SMP4.zip")
print("=" * 100)
c.execute("SELECT filename, size, modified_time FROM files WHERE filename = '11-SMP4.zip'")
for fn, sz, mt in c.fetchall():
    print(f"  {fn}: {sz/1073741824:.2f} Go, modifié {ts(mt)}")

# 3. Overlap USINE/SESSIONS CONTROLES vs _a_classer/SMP - CONTROLES
print(f"\n{'=' * 100}")
print("OVERLAP: USINE/SESSIONS CONTROLES vs _a_classer sous-dossiers")
print("=" * 100)

pref_sessions = BASE + 'USINE-VOUSSOIRS-SMLP\\SESSIONS CONTROLES\\'
c.execute("SELECT filename, size, hash_md5 FROM files WHERE path LIKE ?", (pref_sessions + '%',))
sessions = c.fetchall()
sessions_h = {h for _, _, h in sessions if h}
sessions_ns = {(fn, sz) for fn, sz, _ in sessions}

for sub in ['SMP - CONTROLES MOULES ET VOUSSOIRS', 'CONTROLES SMP A CLASSER', 
            'CONTROLES SMP4', 'MOULES SMP4', '06-smp.bak']:
    pref = BASE + '_a_classer\\' + sub + '\\'
    c.execute("SELECT filename, size, hash_md5 FROM files WHERE path LIKE ?", (pref + '%',))
    files = c.fetchall()
    if not files:
        continue
    matched = sum(1 for fn, sz, h in files if (h and h in sessions_h) or (fn, sz) in sessions_ns)
    pct = matched * 100 // len(files) if files else 0
    sz_total = sum(s for _, s, _ in files)
    print(f"  {sub:<50} {len(files):>6} fich → SESSIONS: {matched} ({pct}%)")

# 4. Overlap: _a_classer complet vs USINE complet
print(f"\n{'=' * 100}") 
print("OVERLAP: _a_classer COMPLET vs USINE-VOUSSOIRS-SMLP COMPLET")
print("=" * 100)

pref_usine = BASE + 'USINE-VOUSSOIRS-SMLP\\'
c.execute("SELECT filename, size, hash_md5 FROM files WHERE path LIKE ? AND path NOT LIKE ?",
          (pref_usine + '%', prefix_zip + '%'))  # exclude ZIP/ subfolder
usine_files = c.fetchall()
usine_h = {h for _, _, h in usine_files if h}
usine_ns = {(fn, sz) for fn, sz, _ in usine_files}

pref_ac = BASE + '_a_classer\\'
c.execute("SELECT path, filename, size, hash_md5 FROM files WHERE path LIKE ?", (pref_ac + '%',))
ac_files = c.fetchall()

ac_matched = 0
ac_missing = 0
ac_matched_sz = 0
for p, fn, sz, h in ac_files:
    if (h and h in usine_h) or (fn, sz) in usine_ns:
        ac_matched += 1
        ac_matched_sz += sz
    else:
        ac_missing += 1

print(f"  USINE (hors ZIP/): {len(usine_files)} fichiers")
print(f"  _a_classer: {len(ac_files)} fichiers")
print(f"  _a_classer → USINE: {ac_matched}/{len(ac_files)} ({ac_matched*100//len(ac_files) if ac_files else 0}%)")
print(f"  Fichiers uniques dans _a_classer: {ac_missing}")

# Inverse
usine_matched = sum(1 for fn, sz, h in usine_files 
                    if (h and h in {h2 for _, _, _, h2 in ac_files if h2}) 
                    or (fn, sz) in {(fn2, sz2) for _, fn2, sz2, _ in ac_files})
print(f"  USINE → _a_classer: {usine_matched}/{len(usine_files)} ({usine_matched*100//len(usine_files) if usine_files else 0}%)")

# 5. USINE/SESSIONS sous-structure
print(f"\n{'=' * 100}")
print("USINE/SESSIONS CONTROLES — Structure L3 (top 20)")
print("=" * 100)
c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, CASE WHEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92)) > 0 
        THEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1 
        ELSE LENGTH(SUBSTR(path, LENGTH(?)+1)) END) as subfolder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go
FROM files WHERE path LIKE ? || '%'
GROUP BY subfolder ORDER BY subfolder LIMIT 20""",
    (pref_sessions, pref_sessions, pref_sessions, pref_sessions, pref_sessions))
for r in c.fetchall():
    print(f"  {r[0]:<55} {r[1]:>6} fich  {r[2]:>6} Go")

conn.close()
