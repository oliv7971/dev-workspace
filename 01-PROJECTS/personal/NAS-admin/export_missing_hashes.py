import sqlite3
import csv

DB = 'reports/inventory_strasbourg.db'
OUT = 'missing_hashes.csv'

conn = sqlite3.connect(DB)
cur = conn.cursor()

with open(OUT, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['path', 'size'])
    for row in cur.execute('SELECT path, size FROM files WHERE hash_md5 IS NULL'):
        writer.writerow(row)

print(f'Exporté: {OUT}')
