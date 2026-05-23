"""Analyse détaillée de 11-FOURNISSEURS et nettoyables."""
import sqlite3
from collections import defaultdict

DB = "./reports/inventory_ggc.db"
BASE = "\\\\Nas_travail\\01-ds414-data\\32-GGC-BUREAU\\"

def rel(path):
    return path[len(BASE):] if path.startswith(BASE) else path

def fmt(size):
    if size >= 1e9: return f"{size/1e9:.1f} Go"
    if size >= 1e6: return f"{size/1e6:.1f} Mo"
    return f"{size/1e3:.1f} Ko"

def main():
    db = sqlite3.connect(DB)
    cur = db.cursor()
    cur.execute("SELECT path, filename, extension, size FROM files")
    all_files = cur.fetchall()

    # 11-FOURNISSEURS\11-FOURNISSEURS sous-dossiers
    print("=== 11-FOURNISSEURS\\11-FOURNISSEURS — sous-dossiers ===")
    fourn = defaultdict(lambda: [0, 0])
    for path, fn, ext, sz in all_files:
        r = rel(path)
        prefix = "11-FOURNISSEURS\\11-FOURNISSEURS\\"
        if r.startswith(prefix):
            rest = r[len(prefix):]
            k = rest.split("\\")[0]
            fourn[k][0] += 1
            fourn[k][1] += sz

    for k in sorted(fourn, key=lambda x: fourn[x][1], reverse=True):
        nb, sz = fourn[k]
        print(f"  {k:55s}  {nb:>5,} fich  {fmt(sz):>10s}")

    # RIEGL sous-dossiers détaillés
    print("\n=== RIEGL — sous-structure ===")
    riegl = defaultdict(lambda: [0, 0])
    for path, fn, ext, sz in all_files:
        r = rel(path)
        if "RIEGL" in r and r.startswith("11-FOURNISSEURS"):
            segs = r.split("\\")
            for i, s in enumerate(segs):
                if s == "RIEGL" and i+1 < len(segs):
                    k = segs[i+1]
                    riegl[k][0] += 1
                    riegl[k][1] += sz
                    break

    for k in sorted(riegl, key=lambda x: riegl[x][1], reverse=True):
        nb, sz = riegl[k]
        print(f"  {k:55s}  {nb:>5,} fich  {fmt(sz):>10s}")

    # Fichiers nettoyables
    print("\n=== FICHIERS NETTOYABLES ===")
    bak_n, bak_s = 0, 0
    thumb_n, thumb_s = 0, 0
    for path, fn, ext, sz in all_files:
        if ext and ext.lower() == ".bak":
            bak_n += 1
            bak_s += sz
        if fn.lower() == "thumbs.db":
            thumb_n += 1
            thumb_s += sz
    print(f"  .bak       : {bak_n:>5,} fichiers  {fmt(bak_s):>10s}")
    print(f"  Thumbs.db  : {thumb_n:>5,} fichiers  {fmt(thumb_s):>10s}")

    # Dossiers suspects
    print("\n=== DOSSIERS SUSPECTS ===")
    suspects = ["a classer", "divers", "temp", "tmp", "old", "ancien",
                "backup", "bak", "copie", "copy", "nouveau dossier",
                "brouillon", "a trier", "doublon"]
    suspect_folders = defaultdict(lambda: [0, 0])
    for path, fn, ext, sz in all_files:
        r = rel(path).lower()
        for suspect in suspects:
            if suspect in r:
                segs = rel(path).split("\\")
                for i, seg in enumerate(segs):
                    if suspect in seg.lower():
                        folder = "\\".join(segs[:i+1])
                        suspect_folders[folder][0] += 1
                        suspect_folders[folder][1] += sz
                        break
                break

    for folder in sorted(suspect_folders, key=lambda x: suspect_folders[x][1], reverse=True)[:15]:
        nb, sz = suspect_folders[folder]
        print(f"  {folder:60s}  {nb:>5,} fich  {fmt(sz):>10s}")

    # 11-FOURNISSEURS\founrisseurs (faute d'orthographe!)
    print("\n=== 11-FOURNISSEURS\\founrisseurs (faute de frappe) ===")
    typo = defaultdict(lambda: [0, 0])
    for path, fn, ext, sz in all_files:
        r = rel(path)
        if r.startswith("11-FOURNISSEURS\\founrisseurs\\"):
            rest = r[len("11-FOURNISSEURS\\founrisseurs\\"):]
            k = rest.split("\\")[0]
            typo[k][0] += 1
            typo[k][1] += sz
    
    for k in sorted(typo, key=lambda x: typo[x][1], reverse=True):
        nb, sz = typo[k]
        print(f"  {k:55s}  {nb:>5,} fich  {fmt(sz):>10s}")

    db.close()

if __name__ == "__main__":
    main()
