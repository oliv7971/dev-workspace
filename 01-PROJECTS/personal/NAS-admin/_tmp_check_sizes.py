import sqlite3
conn = sqlite3.connect('inventaires/inventaire_34-controle voussoirs SMP4.db')
c = conn.cursor()

# Tailles des archives dans l'inventaire
print("=== Archives dans l'inventaire ===")
c.execute("SELECT path, filename, size FROM files WHERE extension IN ('.7z', '.zip') ORDER BY size DESC LIMIT 15")
for p, fn, sz in c.fetchall():
    print(f"  {fn:55s}  size={sz:>15,}  ({sz/1073741824:.2f} Go)")

# Verifier le path complet
print("\n=== Path complet des archives ZIP/ ===")
c.execute("""SELECT path, filename, size FROM files 
WHERE path LIKE '%ZIP%' AND extension IN ('.7z', '.zip')
ORDER BY size DESC LIMIT 10""")
for p, fn, sz in c.fetchall():
    print(f"  path={p}")
    print(f"  file={fn}  size={sz}")

# Verifier le chemin dans la requete du script
print("\n=== Requete du script (USINE-VOUSSOIRS-SMLP\\ZIP\\%) ===")
base = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\34-controle voussoirs SMP4'
c.execute("""SELECT path || filename as full, filename, size FROM files 
WHERE path LIKE ? AND extension IN ('.7z', '.zip', '.rar')
ORDER BY size DESC""", (base + '\\USINE-VOUSSOIRS-SMLP\\ZIP\\%',))
rows = c.fetchall()
print(f"  {len(rows)} resultats")
for full, fn, sz in rows[:5]:
    print(f"  {fn:55s}  size={sz}")

# Tester le pattern de path
print("\n=== Echantillon de paths dans l'inventaire ===")
c.execute("SELECT DISTINCT path FROM files WHERE path LIKE '%ZIP%' LIMIT 5")
for (p,) in c.fetchall():
    print(f"  [{p}]")

conn.close()
