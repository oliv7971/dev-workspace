"""
Explore la structure des dossiers 09 et 10 dans les inventaires.
Affiche les 2 premiers niveaux uniquement.
"""
import sqlite3, os

def show_top_levels(db_path, label, levels=2):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    if 'files' not in tables:
        print(f'Table "files" absente dans {label}')
        conn.close(); return

    c.execute("SELECT COUNT(*), SUM(size) FROM files")
    total_n, total_sz = c.fetchone()
    print(f'\n{"="*70}')
    print(f'{label}  —  {total_n} fichiers  /  {total_sz/1e9:.2f} Go')
    print(f'{"="*70}')

    # Colonnes dispo
    c.execute("PRAGMA table_info(files)")
    cols = [r[1] for r in c.fetchall()]

    # Champ chemin : essayer 'path', 'relative_path', 'filepath'
    path_col = next((col for col in cols if col in ('path','relative_path','filepath','rel_path')), cols[0])
    size_col = next((col for col in cols if col in ('size','file_size','sz')), None)

    print(f'  colonnes: {cols}')
    print(f'  champ path utilisé: {path_col}')

    # Exemples de chemins
    c.execute(f'SELECT "{path_col}" FROM files LIMIT 3')
    for row in c.fetchall():
        print(f'  ex: {row[0]}')

    if size_col:
        # Récupérer tous les chemins + tailles en Python
        c.execute(f'SELECT "{path_col}", "{size_col}" FROM files')
        rows = c.fetchall()

        from collections import defaultdict

        # Trouver le préfixe commun (chemin UNC racine du dossier)
        sample_paths = [r[0].replace('\\', '/') for r in rows[:5] if r[0]]
        # Le préfixe est la partie jusqu'au 2e segment après "31-GGC-DOSSIERS/"
        def get_prefix(p):
            idx = p.find('31-GGC-DOSSIERS/')
            if idx < 0:
                idx = p.find('31-GGC-DOSSIERS\\')
            if idx < 0:
                return ''
            after = p[idx + len('31-GGC-DOSSIERS/'):]
            slash = after.find('/')
            if slash < 0:
                return p
            return p[:idx + len('31-GGC-DOSSIERS/') + slash + 1]

        prefix = get_prefix(sample_paths[0]) if sample_paths else ''
        print(f'  préfixe détecté: {prefix}')

        lvl1 = defaultdict(lambda: [0, 0])
        lvl2 = defaultdict(lambda: [0, 0])
        lvl3 = defaultdict(lambda: [0, 0])
        for p, sz in rows:
            if p is None:
                continue
            p = p.replace('\\', '/')
            sz = sz or 0
            # Chemin relatif
            rel = p[len(prefix):] if p.startswith(prefix) else p
            parts = [s for s in rel.split('/') if s]

            k1 = parts[0] if parts else '(racine)'
            lvl1[k1][0] += 1; lvl1[k1][1] += sz

            k2 = '/'.join(parts[:2]) if len(parts) >= 2 else k1
            lvl2[k2][0] += 1; lvl2[k2][1] += sz

            k3 = '/'.join(parts[:3]) if len(parts) >= 3 else k2
            lvl3[k3][0] += 1; lvl3[k3][1] += sz

        print(f'\n--- Niveau 1 ---')
        for k, (nb, sz) in sorted(lvl1.items(), key=lambda x: -x[1][1]):
            print(f'  {k:50s}  {nb:5d} f  {sz/1e6:8.1f} Mo')

        print(f'\n--- Niveau 2 ---')
        for k, (nb, sz) in sorted(lvl2.items(), key=lambda x: -x[1][1])[:50]:
            print(f'  {k:60s}  {nb:5d} f  {sz/1e6:8.1f} Mo')

        print(f'\n--- Niveau 3 (top 30 par taille) ---')
        for k, (nb, sz) in sorted(lvl3.items(), key=lambda x: -x[1][1])[:30]:
            print(f'  {k:70s}  {nb:5d} f  {sz/1e6:8.1f} Mo')

    conn.close()


for db_name in ['inventaire_09-BARRAGES RENAISON.db', 'inventaire_10-barrage ourdan.db']:
    path = os.path.join('inventaires', db_name)
    if not os.path.exists(path):
        print(f'ABSENT: {db_name}')
        continue
    show_top_levels(path, db_name)
