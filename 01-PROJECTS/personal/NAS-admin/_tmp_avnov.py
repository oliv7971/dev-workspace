import sqlite3
conn = sqlite3.connect('./reports/inventory_chambon37.db')
cur = conn.cursor()
cur.execute("SELECT DISTINCT path FROM files WHERE path LIKE '%avant nov 2016%' AND path NOT LIKE '%_a_classer%' LIMIT 5")
rows = cur.fetchall()
if rows:
    print("Existe hors _a_classer :")
    for r in rows:
        print(" ", r[0])
else:
    print("AUCUN fichier 'avant nov 2016' hors _a_classer dans la DB")
    print("=> _a_classer est le SEUL endroit ou ces fichiers existent !")
conn.close()
