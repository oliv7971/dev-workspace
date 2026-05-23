"""Rebuild inventaire de 37-TUNNEL GRAND CHAMBON (post-cleanup)."""
import os, sys, time
sys.path.insert(0, '.')
from nas_admin.inventory import init_db, scan_directory
import yaml

config_path = 'config.yaml'
config = yaml.safe_load(open(config_path, encoding='utf-8')) if os.path.exists(config_path) else {}

db_path = 'inventaires/inventaire_37-TUNNEL GRAND CHAMBON.db'
nas_path = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON'

# Supprimer ancienne DB
if os.path.exists(db_path):
    os.remove(db_path)
    print('Ancienne DB supprimee')

print(f'Scan de {nas_path}...')
t0 = time.time()

conn = init_db(db_path)
scan_directory(nas_path, config, conn, compute_hashes=True)
conn.close()

elapsed = time.time() - t0
print(f'Inventaire termine en {elapsed/60:.1f} min')

# Stats rapides
import sqlite3
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('SELECT COUNT(*), SUM(size) FROM files')
count, total_size = cur.fetchone()
cur.execute('SELECT COUNT(*) FROM files WHERE hash_md5 IS NOT NULL')
hashed = cur.fetchone()[0]
conn.close()

print(f'\nResultat:')
print(f'  Fichiers: {count}')
print(f'  Taille:   {total_size/1073741824:.2f} Go')
print(f'  Hashes:   {hashed} ({hashed*100//max(count,1)}%)')
