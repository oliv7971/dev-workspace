"""Vérification détaillée des doublons : hash, taille, dates."""
import sqlite3
from datetime import datetime

DB = "./reports/inventory_sftrf.db"
BASE = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\01-SFTRF"

conn = sqlite3.connect(DB)
cur = conn.cursor()

def format_size(b):
    for u in ['o','Ko','Mo','Go','To']:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024

def fmt_date(ts):
    if ts:
        try:
            return datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M")
        except:
            return str(ts)
    return "?"

# Top 30 groupes de doublons par espace gaspillé
cur.execute("SELECT hash_md5, size, file_count, wasted_space FROM duplicate_groups ORDER BY wasted_space DESC LIMIT 30")
groups = cur.fetchall()

print("=" * 120)
print("VÉRIFICATION DÉTAILLÉE DES 30 PLUS GROS GROUPES DE DOUBLONS")
print("Les fichiers d'un même groupe ont le MÊME hash MD5 = contenu identique bit à bit")
print("=" * 120)

total_wasted = 0

for i, (hash_md5, size, file_count, wasted) in enumerate(groups, 1):
    cur.execute("""SELECT path, size, hash_md5, modified_time, created_time 
                   FROM files WHERE hash_md5 = ? AND size = ? 
                   ORDER BY LENGTH(path)""", (hash_md5, size))
    files = cur.fetchall()
    
    if len(files) < 2:
        continue
    
    total_wasted += wasted
    
    print(f"\n{'─' * 120}")
    print(f"GROUPE {i}: {len(files)} copies | Taille: {format_size(size)} | Hash: {hash_md5} | Gaspillage: {format_size(wasted)}")
    print(f"{'─' * 120}")
    
    for j, (path, fsize, fhash, mtime, ctime) in enumerate(files):
        short = path.replace(BASE + "\\", "")
        marker = "✅ GARDER " if j == 0 else "🗑️  SUPPR  "
        mod = fmt_date(mtime)
        cre = fmt_date(ctime)
        print(f"  {marker} | Modifié: {mod} | Créé: {cre} | {short[:80]}")

print(f"\n{'=' * 120}")
print(f"TOTAL gaspillé (top 30 groupes) : {format_size(total_wasted)}")

# Stats globales sur les dates
print(f"\n{'=' * 120}")
print("STATISTIQUES SUR LES DATES DES DOUBLONS")
print("=" * 120)

# Pour chaque groupe, vérifier si les dates diffèrent
cur.execute("SELECT hash_md5, size, file_count FROM duplicate_groups ORDER BY wasted_space DESC")
all_groups = cur.fetchall()

same_dates = 0
diff_dates = 0
no_dates = 0

for hash_md5, size, file_count in all_groups:
    cur.execute("SELECT modified_time FROM files WHERE hash_md5 = ? AND size = ?", (hash_md5, size))
    mtimes = [r[0] for r in cur.fetchall()]
    
    if not any(mtimes):
        no_dates += 1
    elif len(set(mtimes)) == 1:
        same_dates += 1
    else:
        diff_dates += 1

print(f"  Groupes avec dates identiques   : {same_dates}")
print(f"  Groupes avec dates différentes  : {diff_dates}")
print(f"  Groupes sans date               : {no_dates}")
print(f"\n  Note: même quand les dates diffèrent, le hash MD5 garantit")
print(f"  que le CONTENU est strictement identique (même fichier copié à une autre date)")

conn.close()
