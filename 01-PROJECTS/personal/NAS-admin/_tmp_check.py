import sqlite3
conn = sqlite3.connect(r'inventaires/inventaire_33-TUNNEL DU CHAT.db')
c = conn.cursor()
base = '\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\33-TUNNEL DU CHAT\\'
# Top-level folders
c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1) as folder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go
FROM files WHERE path LIKE ? || '%'
GROUP BY folder ORDER BY cnt DESC""", (base, base, base))
print("Dossiers L1 restants dans la DB:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]} fich ({r[2]} Go)")

# Paths containing olivier
c.execute("SELECT DISTINCT SUBSTR(path, 1, 130) FROM files WHERE LOWER(path) LIKE '%olivier%' LIMIT 15")
print("\nPaths contenant 'olivier':")
for r in c.fetchall():
    print(f"  {r[0]}")

conn.close()
