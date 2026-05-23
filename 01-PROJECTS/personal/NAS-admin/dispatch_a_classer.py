"""
Dispatch _a_classer → SESSIONS CONTROLES, RAPPORTS, _doublons (par dossier+année).
Dry-run par défaut. Relancer avec --execute pour exécuter les déplacements réels.
"""
import sqlite3, re, os, sys, shutil
from collections import defaultdict

DB = "reports/inventory_voussoirs_smp4.db"
NAS = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\34-controle voussoirs SMP4"
A_CLASSER_REL = "_a_classer"
SESSIONS_REL  = "USINE-VOUSSOIRS-SMLP\\SESSIONS CONTROLES"
RAPPORTS_REL  = "USINE-VOUSSOIRS-SMLP\\RAPPORTS"
DOUBLONS_REL  = "_doublons"

EXECUTE = "--execute" in sys.argv
YEAR_RE = re.compile(r'(20\d{2})')
REPORT_EXTS = {".pdf", ".doc", ".docx", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"}

# Dossiers clairement des sauvegardes → _doublons (indépendamment de la détection)
FORCE_DOUBLON = {"06-smp.bak", "SMP - CONTROLES MOULES ET VOUSSOIRS"}

def nas_path(*parts):
    return os.path.join(NAS, *parts)

def extract_year(name):
    years = [int(y) for y in YEAR_RE.findall(name) if 2010 <= int(y) <= 2030]
    return str(min(years)) if years else "_date_inconnue"

def human_size(n):
    for u in ["o", "Ko", "Mo", "Go"]:
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} Go"

print("Chargement de la base de données...")
c = sqlite3.connect(DB)
a_classer_prefix = nas_path(A_CLASSER_REL) + "\\"

rows = c.execute(
    "SELECT path, size, filename, extension FROM files WHERE path LIKE ?",
    (a_classer_prefix + "%",)
).fetchall()

# Fichiers existants dans SESSIONS et RAPPORTS (pour détecter les doublons)
existing_sessions = set()
existing_rapports = set()
for path, size, fn, ext in c.execute(
    "SELECT path, size, filename, extension FROM files WHERE path LIKE ?",
    (nas_path(SESSIONS_REL) + "\\%",)
):
    existing_sessions.add((fn, size or 0))
for path, size, fn, ext in c.execute(
    "SELECT path, size, filename, extension FROM files WHERE path LIKE ?",
    (nas_path(RAPPORTS_REL) + "\\%",)
):
    existing_rapports.add((fn, size or 0))
c.close()

print(f"  {len(rows)} fichiers dans _a_classer")
print(f"  {len(existing_sessions)} fichiers dans SESSIONS CONTROLES")
print(f"  {len(existing_rapports)} fichiers dans RAPPORTS")

# Grouper par sous-dossier de 1er niveau dans _a_classer
groups = defaultdict(list)
root_files = []

for path, size, fn, ext in rows:
    rel = path[len(a_classer_prefix):]
    parts = rel.split("\\")
    if len(parts) == 1:
        root_files.append((path, size or 0, fn, ext))
    else:
        groups[parts[0]].append((path, size or 0, fn, ext))

# Construire le plan de dispatch au niveau dossier
plan = []  # (top_folder, dest_rel, year, nb, total_size, reason)

for top in sorted(groups.keys()):
    files = groups[top]
    nb = len(files)
    total_size = sum(s for _, s, _, _ in files)
    year = extract_year(top)

    # Sauvegardes connues → _doublons
    if top in FORCE_DOUBLON:
        plan.append((top, DOUBLONS_REL, "", nb, total_size, "backup forcé"))
        continue

    # Détection de doublons par nom+taille (>60% de fichiers déjà présents)
    dup_s = sum(1 for _, s, fn, _ in files if (fn, s) in existing_sessions)
    dup_r = sum(1 for _, s, fn, _ in files if (fn, s) in existing_rapports)
    dup_ratio = (dup_s + dup_r) / nb if nb > 0 else 0

    if dup_ratio > 0.6:
        plan.append((top, DOUBLONS_REL, "", nb, total_size,
                     f"doublon {dup_ratio:.0%}"))
        continue

    # Classer en RAPPORTS ou SESSIONS selon la majorité des extensions
    nb_reports = sum(1 for _, _, _, ext in files if (ext or "").lower() in REPORT_EXTS)
    if nb_reports > nb * 0.5:
        plan.append((top, RAPPORTS_REL, year, nb, total_size, "rapports"))
    else:
        plan.append((top, SESSIONS_REL, year, nb, total_size, "sessions"))

# Fichiers à la racine de _a_classer (archives .zip etc.) → laisser en place
if root_files:
    total_root = sum(s for _, s, _, _ in root_files)
    plan.append(("(fichiers racine)", "IGNORER", "", len(root_files), total_root,
                 "archives/zip — non déplacés"))

# ─── Affichage du plan ────────────────────────────────────────────────────────
print("\n" + "="*80)
print(f"PLAN DE DISPATCH {'[DRY-RUN — aucun fichier déplacé]' if not EXECUTE else '[EXÉCUTION]'}")
print("="*80)

dest_summary = defaultdict(lambda: [0, 0])

for top, dest, year, nb, sz, reason in plan:
    if dest == "IGNORER":
        dest_label = "IGNORER"
    elif year:
        dest_label = f"{dest}\\{year}"
    else:
        dest_label = dest
    key = dest_label
    dest_summary[key][0] += nb
    dest_summary[key][1] += sz
    print(f"  {top[:48]:<48}  {nb:>6} fich.  {human_size(sz):>9}  →  {dest_label}  [{reason}]")

print("\n" + "="*80)
print("RÉSUMÉ PAR DESTINATION")
print("="*80)
for dest, (nb, sz) in sorted(dest_summary.items()):
    print(f"  {dest:<60}  {nb:>6} fichiers  {human_size(sz):>9}")

if not EXECUTE:
    print("\n⚠️  DRY-RUN — Aucun fichier déplacé.")
    print("   Vérifier le plan ci-dessus, puis relancer avec : python dispatch_a_classer.py --execute")
    sys.exit(0)

# ─── EXÉCUTION ────────────────────────────────────────────────────────────────
print("\n" + "="*80)
print("EXÉCUTION DES DÉPLACEMENTS")
print("="*80)

moved = 0
errors = []

for top, dest, year, nb, sz, reason in plan:
    if dest == "IGNORER" or top == "(fichiers racine)":
        print(f"  [IGNORÉ]  {top}")
        continue

    src = nas_path(A_CLASSER_REL, top)
    if year:
        dst = nas_path(dest, year, top)
    else:
        dst = nas_path(dest, top)

    label_dst = dst[len(NAS)+1:]
    print(f"  {top[:45]:<45} → {label_dst[:50]}", end=" ", flush=True)

    try:
        if not os.path.exists(src):
            print("⚠️  source introuvable")
            continue

        os.makedirs(os.path.dirname(dst), exist_ok=True)

        if os.path.exists(dst):
            # Fusion item par item si la destination existe déjà
            conflicts = 0
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if not os.path.exists(d):
                    shutil.move(s, d)
                else:
                    conflicts += 1
            try:
                os.rmdir(src)  # supprimer si vide après fusion
            except Exception:
                pass
            print(f"✅ (fusion, {conflicts} conflits ignorés)")
        else:
            shutil.move(src, dst)
            print("✅")

        moved += 1

    except Exception as e:
        errors.append((top, str(e)))
        print(f"❌ {e}")

print(f"\n✅ Dossiers traités : {moved}")
if errors:
    print(f"❌ Erreurs ({len(errors)}) :")
    for top, err in errors:
        print(f"  {top} : {err}")
else:
    print("Aucune erreur.")
