import sqlite3
conn = sqlite3.connect('./reports/inventory_chambon37.db')
before = conn.execute("SELECT COUNT(id) FROM files").fetchone()[0]
conn.execute('DELETE FROM files')
conn.commit()
after = conn.execute("SELECT COUNT(id) FROM files").fetchone()[0]
print(f"Avant : {before} entrees")
print(f"Apres purge : {after} entrees")
conn.close()
