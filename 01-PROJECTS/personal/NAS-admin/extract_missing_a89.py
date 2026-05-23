# Extrait les fichiers presents dans le ZIP mais absents du dossier extrait.
# Strategie : extraction vers D:\x (chemin court) pour eviter MAX_PATH,
# puis copie vers le NAS.
import os
import sys
import zipfile
import shutil

ZIP_PATH   = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\39-autoroute A89\A89\A89-auscultations OCT 2022.zip"
FOLDER     = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\39-autoroute A89\A89\A89-auscultations OCT 2022"
LOCAL_TEMP = r"D:\x"   # chemin ultra-court pour éviter MAX_PATH

DRY_RUN = "--execute" not in sys.argv

def get_folder_files(folder_path):
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

def normalize_zip_name(name, zip_stem):
    name = name.replace("\\", "/")
    parts = name.split("/")
    if parts[0].lower() == zip_stem.lower():
        name = "/".join(parts[1:])
    return name

def main():
    zip_stem = os.path.splitext(os.path.basename(ZIP_PATH))[0]
    folder_files = get_folder_files(FOLDER)

    missing = []
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            rel = normalize_zip_name(info.filename, zip_stem)
            if rel.lower() not in folder_files:
                missing.append((info.filename, rel, info.file_size))

    print(f"Fichiers manquants dans le dossier : {len(missing)}")
    total = sum(s for _, _, s in missing) / 1024 / 1024
    print(f"Taille totale : {total:.1f} Mo")
    print()

    if not missing:
        print("Rien à faire.")
        return

    mode = "DRY-RUN" if DRY_RUN else "EXÉCUTION"
    print(f"=== {mode} ===\n")

    for zip_name, rel, size in missing:
        local_dest = os.path.join(LOCAL_TEMP, rel.replace("/", os.sep))
        nas_dest   = os.path.join(FOLDER, rel.replace("/", os.sep))
        print(f"  {rel[:80]}...")

        if not DRY_RUN:
            # 1. Extraire vers D:\x\
            os.makedirs(os.path.dirname(local_dest), exist_ok=True)
            with zipfile.ZipFile(ZIP_PATH, 'r') as z:
                with z.open(zip_name) as src, open(local_dest, 'wb') as dst:
                    shutil.copyfileobj(src, dst)

            # 2. Copier vers NAS
            nas_dir = os.path.dirname(nas_dest)
            os.makedirs(nas_dir, exist_ok=True)
            shutil.copy2(local_dest, nas_dest)
            print(f"      → copié vers NAS")

    if not DRY_RUN:
        print(f"\nNettoyage du dossier temporaire {LOCAL_TEMP}...")
        shutil.rmtree(LOCAL_TEMP, ignore_errors=True)
        print("Done.")
    else:
        print(f"\nRelancer avec --execute pour extraire.")

main()
