"""
Compare les ZIP présents dans A89\ avec leurs dossiers extraits correspondants.
Détecte les fichiers présents dans le ZIP mais absents du dossier (données manquantes).
"""
import os
import zipfile

ROOT = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\39-autoroute A89\A89"

def get_folder_files(folder_path):
    """Retourne un dict {nom_relatif_normalisé: taille} pour tous les fichiers du dossier."""
    result = {}
    for dirpath, _, filenames in os.walk(folder_path):
        for f in filenames:
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, folder_path).replace("\\", "/").lower()
            try:
                result[rel] = os.path.getsize(full)
            except OSError:
                pass
    return result

def get_zip_files(zip_path):
    """Retourne un dict {nom_relatif_normalisé: taille} pour tous les fichiers du zip."""
    result = {}
    with zipfile.ZipFile(zip_path, 'r') as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            # Normalise : retire le premier composant si c'est le nom du dossier racine
            name = info.filename.replace("\\", "/")
            parts = name.split("/")
            # Si premier composant = nom du zip sans extension, on l'enlève
            zip_stem = os.path.splitext(os.path.basename(zip_path))[0].lower()
            if parts[0].lower() == zip_stem:
                name = "/".join(parts[1:])
            result[name.lower()] = info.file_size
    return result

def compare(zip_path, folder_path):
    zip_name = os.path.basename(zip_path)
    folder_name = os.path.basename(folder_path)
    print(f"\n{'='*70}")
    print(f"ZIP   : {zip_name}")
    print(f"DOSSIER : {folder_name}")

    if not os.path.isdir(folder_path):
        print(f"  !! Dossier absent — impossible de comparer")
        return

    zip_files = get_zip_files(zip_path)
    folder_files = get_folder_files(folder_path)

    print(f"  ZIP    : {len(zip_files):>5} fichiers")
    print(f"  Dossier: {len(folder_files):>5} fichiers")

    # Fichiers dans zip mais absents du dossier
    only_in_zip = {k: v for k, v in zip_files.items() if k not in folder_files}
    # Fichiers dans dossier mais absents du zip
    only_in_folder = {k: v for k, v in folder_files.items() if k not in zip_files}

    if only_in_zip:
        total = sum(only_in_zip.values()) / 1024 / 1024
        print(f"\n  ⚠ DANS ZIP SEULEMENT ({len(only_in_zip)} fichiers, {total:.1f} Mo) :")
        for k, v in sorted(only_in_zip.items())[:20]:
            print(f"      {k}  ({v/1024:.1f} Ko)")
        if len(only_in_zip) > 20:
            print(f"      ... et {len(only_in_zip)-20} autres")
    else:
        print(f"\n  ✓ Tous les fichiers du ZIP sont présents dans le dossier")

    if only_in_folder:
        total = sum(only_in_folder.values()) / 1024 / 1024
        print(f"\n  + DANS DOSSIER SEULEMENT ({len(only_in_folder)} fichiers, {total:.1f} Mo) :")
        for k, v in sorted(only_in_folder.items())[:10]:
            print(f"      {k}  ({v/1024:.1f} Ko)")
        if len(only_in_folder) > 10:
            print(f"      ... et {len(only_in_folder)-10} autres")

# Cherche tous les zips dans ROOT
zip_files_found = [
    f for f in os.listdir(ROOT)
    if f.lower().endswith(".zip") and os.path.isfile(os.path.join(ROOT, f))
]

print(f"ZIPs trouvés dans A89\\ : {len(zip_files_found)}")

for zf in sorted(zip_files_found):
    zip_path = os.path.join(ROOT, zf)
    folder_name = os.path.splitext(zf)[0]
    folder_path = os.path.join(ROOT, folder_name)
    compare(zip_path, folder_path)

print("\n\nDone.")
