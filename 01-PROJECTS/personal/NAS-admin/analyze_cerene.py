"""Analyse structurelle de 21-CERENE pour identifier les problèmes d'organisation."""
import sqlite3
from collections import defaultdict

DB = "./reports/inventory_cerene.db"
BASE = "\\\\Nas_travail\\01-ds414-data\\21-CERENE\\"

def fmt(size):
    if size >= 1e9: return f"{size/1e9:.1f} Go"
    if size >= 1e6: return f"{size/1e6:.1f} Mo"
    if size >= 1e3: return f"{size/1e3:.1f} Ko"
    return f"{size} o"

def rel(path):
    """Chemin relatif à 21-CERENE."""
    if path.startswith(BASE):
        return path[len(BASE):]
    return path

def parts(path, depth):
    """Retourne les N premiers niveaux du chemin relatif."""
    r = rel(path)
    segs = r.split("\\")
    return "\\".join(segs[:depth])

def main():
    db = sqlite3.connect(DB)
    cur = db.cursor()
    
    # Compter les fichiers encore présents (pas supprimés)
    # La DB contient toujours tous les fichiers - on ne peut pas vérifier lesquels existent
    # On va travailler avec ce qu'on a et noter que ~48k fichiers ont été supprimés
    
    print("=" * 80)
    print("ANALYSE STRUCTURELLE DE 21-CERENE")
    print("=" * 80)
    
    # === NIVEAU 1 ===
    print("\n📁 DOSSIERS NIVEAU 1")
    print("-" * 80)
    lvl1 = defaultdict(lambda: [0, 0])
    cur.execute("SELECT path, size FROM files")
    total_files = 0
    total_size = 0
    for path, size in cur:
        total_files += 1
        total_size += size
        k = parts(path, 1)
        lvl1[k][0] += 1
        lvl1[k][1] += size
    
    for k in sorted(lvl1, key=lambda x: lvl1[x][1], reverse=True):
        nb, sz = lvl1[k]
        pct = sz / total_size * 100
        print(f"  {k:40s}  {nb:>8,} fichiers  {fmt(sz):>10s}  ({pct:.1f}%)")
    
    print(f"\n  TOTAL: {total_files:,} fichiers, {fmt(total_size)}")
    
    # === NIVEAU 2 ===
    print("\n📁 DOSSIERS NIVEAU 2 (top 30 par taille)")
    print("-" * 80)
    lvl2 = defaultdict(lambda: [0, 0])
    cur.execute("SELECT path, size FROM files")
    for path, size in cur:
        k = parts(path, 2)
        lvl2[k][0] += 1
        lvl2[k][1] += size
    
    sorted_lvl2 = sorted(lvl2.items(), key=lambda x: x[1][1], reverse=True)[:30]
    for k, (nb, sz) in sorted_lvl2:
        pct = sz / total_size * 100
        print(f"  {k:55s}  {nb:>8,} fichiers  {fmt(sz):>10s}  ({pct:.1f}%)")
    
    # === Fichiers à la racine ou mal classés ===
    print("\n📄 FICHIERS À LA RACINE DE 21-CERENE")
    print("-" * 80)
    cur.execute("SELECT path, filename, size FROM files")
    root_files = []
    for path, fn, size in cur:
        r = rel(path)
        if "\\" not in r.split("\\", 1)[-1].rsplit("\\", 1)[0] if "\\" in r else True:
            # Fichier directement dans un dossier niveau 1 (pas de sous-dossier)
            pass
        segs = r.split("\\")
        if len(segs) <= 1:
            root_files.append((fn, size))
    
    if root_files:
        for fn, sz in sorted(root_files, key=lambda x: x[1], reverse=True)[:20]:
            print(f"  {fn:60s}  {fmt(sz)}")
    else:
        print("  (aucun)")
    
    # === Dossiers « fourre-tout » (beaucoup de sous-dossiers variés) ===
    print("\n🔍 ANALYSE DES NOMS DE DOSSIERS SUSPECTS")
    print("-" * 80)
    suspect_names = ["a classer", "divers", "temp", "tmp", "old", "ancien",
                     "backup", "bak", "copie", "copy", "nouveau dossier", 
                     "new folder", "sans titre", "untitled", "brouillon",
                     "a trier", "en cours", "a ranger", "doublon", "poubelle",
                     "corbeille", "trash"]
    
    cur.execute("SELECT DISTINCT path FROM files")
    suspect_folders = defaultdict(lambda: [0, 0])
    all_paths = cur.fetchall()
    
    cur.execute("SELECT path, size FROM files")
    path_to_size = {}
    for path, size in cur:
        path_to_size[path] = size
    
    for (path,) in all_paths:
        r = rel(path).lower()
        for suspect in suspect_names:
            if suspect in r:
                # Trouver le dossier suspect
                segs = rel(path).split("\\")
                for i, seg in enumerate(segs):
                    if suspect in seg.lower():
                        folder = "\\".join(segs[:i+1])
                        suspect_folders[folder][0] += 1
                        suspect_folders[folder][1] += path_to_size.get(path, 0)
                        break
                break
    
    if suspect_folders:
        sorted_suspects = sorted(suspect_folders.items(), key=lambda x: x[1][1], reverse=True)
        for folder, (nb, sz) in sorted_suspects[:20]:
            print(f"  {folder:60s}  {nb:>6,} fichiers  {fmt(sz):>10s}")
    else:
        print("  (aucun dossier suspect trouvé)")
    
    # === Dossiers avec dates dans le nom (dumps/sauvegardes) ===
    print("\n📅 DOSSIERS AVEC DATES (possibles dumps/sauvegardes)")
    print("-" * 80)
    import re
    date_pattern = re.compile(r'\b(20[0-2]\d[-_]\d{2}[-_]\d{2}|\d{2}[-_]\d{2}[-_]20[0-2]\d|sauvegarde|save|backup)\b', re.IGNORECASE)
    
    date_folders = defaultdict(lambda: [0, 0])
    for (path,) in all_paths:
        r = rel(path)
        segs = r.split("\\")
        for i, seg in enumerate(segs[:4]):  # max 4 niveaux
            if date_pattern.search(seg):
                folder = "\\".join(segs[:i+1])
                date_folders[folder][0] += 1
                date_folders[folder][1] += path_to_size.get(path, 0)
                break
    
    if date_folders:
        sorted_dates = sorted(date_folders.items(), key=lambda x: x[1][1], reverse=True)
        for folder, (nb, sz) in sorted_dates[:20]:
            print(f"  {folder:60s}  {nb:>6,} fichiers  {fmt(sz):>10s}")
    else:
        print("  (aucun)")
    
    # === Extensions par dossier niveau 1 ===
    print("\n📊 TYPES DE FICHIERS PAR DOSSIER NIVEAU 1")
    print("-" * 80)
    
    exts_by_folder = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    cur.execute("SELECT path, extension, size FROM files")
    for path, ext, size in cur:
        k = parts(path, 1)
        e = (ext or "(sans ext)").lower()
        exts_by_folder[k][e][0] += 1
        exts_by_folder[k][e][1] += size
    
    for folder in sorted(lvl1, key=lambda x: lvl1[x][1], reverse=True):
        exts = exts_by_folder[folder]
        top_exts = sorted(exts.items(), key=lambda x: x[1][1], reverse=True)[:5]
        ext_str = ", ".join(f"{e} ({fmt(s)})" for e, (n, s) in top_exts)
        print(f"  {folder:30s}  → {ext_str}")
    
    # === Cohérence : fichiers d'un type dans le mauvais dossier ===
    print("\n⚠️  INCOHÉRENCES POTENTIELLES")
    print("-" * 80)
    
    # Compter les fichiers .exe, .msi, .iso (installeurs) hors d'un dossier soft/install
    cur.execute("SELECT path, filename, size FROM files WHERE extension IN ('.exe', '.msi', '.iso', '.zip', '.rar')")
    installers_misplaced = []
    for path, fn, size in cur:
        r = rel(path).lower()
        l1 = parts(path, 1).lower()
        if l1 not in ("", ) and "soft" not in r.split("\\")[0].lower() and "install" not in r.split("\\")[0].lower():
            if size > 10_000_000:  # > 10 Mo
                installers_misplaced.append((rel(path), fn, size))
    
    if installers_misplaced:
        print(f"  Gros exécutables/archives (>10Mo) potentiellement mal placés : {len(installers_misplaced)}")
        for path, fn, sz in sorted(installers_misplaced, key=lambda x: x[2], reverse=True)[:15]:
            p1 = parts(BASE + path, 1)
            print(f"    [{p1}] {fn} ({fmt(sz)})")
    
    # === Résumé profondeur d'arborescence ===
    print("\n📏 PROFONDEUR D'ARBORESCENCE")
    print("-" * 80)
    depths = defaultdict(int)
    cur.execute("SELECT path FROM files")
    for (path,) in cur:
        d = len(rel(path).split("\\"))
        depths[d] += 1
    
    for d in sorted(depths):
        bar = "█" * (depths[d] // 1000)
        print(f"  Profondeur {d:2d}: {depths[d]:>8,} fichiers  {bar}")
    
    db.close()

if __name__ == "__main__":
    main()
