"""
Analyse détaillée de _a_classer pour préparer le dispatch
vers SESSIONS CONTROLES ou RAPPORTS (par année).
Ne déplace rien — génère un plan de classement.
"""
import sqlite3
import re
import os
from collections import defaultdict

DB = "reports/inventory_voussoirs_smp4.db"
ROOT = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\34-controle voussoirs SMP4\\"
A_CLASSER = ROOT + "_a_classer\\"
USINE = ROOT + "USINE-VOUSSOIRS-SMLP\\"
SESSIONS = USINE + "SESSIONS CONTROLES\\"
RAPPORTS_DIR = USINE + "RAPPORTS\\"

def human_size(n):
    for u in ["o", "Ko", "Mo", "Go"]:
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} Go"

# Regex pour extraire une année ou une date dans le chemin
YEAR_RE = re.compile(r'(20\d{2})')
DATE_RE = re.compile(r'(20\d{2})[_\-\s]?(\d{2})[_\-\s]?(\d{2})')

def extract_year(path):
    """Extrait l'année la plus pertinente du chemin."""
    matches = YEAR_RE.findall(path)
    if matches:
        years = [int(y) for y in matches if 2010 <= int(y) <= 2030]
        if years:
            return str(min(years))  # prendre la plus ancienne (date de la session)
    return None

def classify_file(path, ext, size):
    """
    Retourne (destination, categorie) :
    - destination : 'RAPPORTS', 'SESSIONS', 'DOUBLONS', 'IGNORER'
    - categorie : description courte
    """
    rel = path[len(A_CLASSER):]
    rel_lower = rel.lower()
    ext = (ext or "").lower()

    # Rapports PDF
    if ext == ".pdf":
        if any(k in rel_lower for k in ["rapport", "report", "compte-rendu", "cr-"]):
            return "RAPPORTS", "rapport PDF"
        return "RAPPORTS", "PDF"

    # Documents bureautique
    if ext in (".doc", ".docx", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"):
        return "RAPPORTS", f"document {ext}"

    # Fichiers sessions de contrôle PolyWorks
    if ext in (".pwk", ".pwsa", ".pwzip", ".vlt", ".tol", ".nom",
               ".iminspect", ".archive", ".meas", ".mask", ".gz"):
        return "SESSIONS", "données contrôle"

    # Fichiers sans extension (données PolyWorks internes)
    if not ext:
        return "SESSIONS", "données PolyWorks"

    # CAO / géométrie
    if ext in (".stp", ".iges", ".igs", ".dxf", ".dwg"):
        return "SESSIONS", "fichier CAO"

    # Images
    if ext in (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"):
        return "SESSIONS", "image"

    # Installeur / exécutable → ignorer (ne pas déplacer)
    if ext in (".msi", ".exe", ".dll"):
        return "IGNORER", f"installeur/exe {ext}"

    # Archives racine
    if ext in (".zip", ".7z", ".rar"):
        return "IGNORER", f"archive {ext}"

    # Fichiers GUID (locks/temp)
    if re.match(r'\.[0-9a-f]{8}-', ext):
        return "IGNORER", "fichier temporaire GUID"

    # Fichiers temporaires
    if ext in (".doc#", ".odt#", ".tmp"):
        return "IGNORER", "fichier temporaire"

    return "SESSIONS", f"autre ({ext})"

c = sqlite3.connect(DB)
rows = c.execute(
    "SELECT path, size, filename, extension FROM files WHERE path LIKE ?",
    (A_CLASSER + "%",)
).fetchall()

# Récupérer les chemins existants dans SESSIONS et RAPPORTS pour détection de doublons
existing_sessions = set()
existing_rapports = set()

for path, size, filename, ext in c.execute(
    "SELECT path, size, filename, extension FROM files WHERE path LIKE ?",
    (SESSIONS + "%",)
):
    existing_sessions.add((filename, size))

for path, size, filename, ext in c.execute(
    "SELECT path, size, filename, extension FROM files WHERE path LIKE ?",
    (RAPPORTS_DIR + "%",)
):
    existing_rapports.add((filename, size))

c.close()

print(f"Fichiers dans _a_classer : {len(rows)}")
print(f"Fichiers existants dans SESSIONS CONTROLES : {len(existing_sessions)}")
print(f"Fichiers existants dans RAPPORTS : {len(existing_rapports)}")

# Stats par destination
stats = defaultdict(lambda: [0, 0])  # {dest: [nb, taille]}
year_stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # {dest: {year: [nb, taille]}}
doublon_count = [0, 0]
plan = []  # liste de (src_rel, dest, year, categorie, is_doublon)

for path, size, filename, ext in rows:
    rel = path[len(A_CLASSER):]
    dest, cat = classify_file(path, ext, size)
    year = extract_year(rel) or "date_inconnue"
    size = size or 0

    # Vérifier si doublon dans la destination
    key = (filename, size)
    is_doublon = False
    if dest == "RAPPORTS" and key in existing_rapports:
        is_doublon = True
    elif dest == "SESSIONS" and key in existing_sessions:
        is_doublon = True

    if is_doublon:
        dest_final = "DOUBLONS"
        doublon_count[0] += 1
        doublon_count[1] += size
    else:
        dest_final = dest

    stats[dest_final][0] += 1
    stats[dest_final][1] += size
    if dest_final in ("RAPPORTS", "SESSIONS"):
        year_stats[dest_final][year][0] += 1
        year_stats[dest_final][year][1] += size

    plan.append((rel, dest_final, year, cat, is_doublon))

# Affichage du plan
print("\n" + "="*70)
print("PLAN DE DISPATCH")
print("="*70)
for dest_final, (nb, sz) in sorted(stats.items()):
    print(f"  → {dest_final:<12} : {nb:>7} fichiers   {human_size(sz):>10}")

print("\n" + "="*70)
print("SESSIONS CONTROLES — répartition par année")
print("="*70)
for year in sorted(year_stats["SESSIONS"].keys()):
    nb, sz = year_stats["SESSIONS"][year]
    print(f"  {year} : {nb:>7} fichiers   {human_size(sz):>10}")

print("\n" + "="*70)
print("RAPPORTS — répartition par année")
print("="*70)
for year in sorted(year_stats["RAPPORTS"].keys()):
    nb, sz = year_stats["RAPPORTS"][year]
    print(f"  {year} : {nb:>7} fichiers   {human_size(sz):>10}")

print("\n" + "="*70)
print("ÉCHANTILLON — RAPPORTS détectés (20 premiers)")
print("="*70)
count = 0
for rel, dest, year, cat, is_dup in plan:
    if dest == "RAPPORTS" and not is_dup:
        print(f"  [{year}] {rel[:80]}")
        count += 1
        if count >= 20:
            break

print("\n" + "="*70)
print("ÉCHANTILLON — À IGNORER (10 premiers)")
print("="*70)
count = 0
for rel, dest, year, cat, is_dup in plan:
    if dest == "IGNORER":
        print(f"  {cat:<25} {rel[:70]}")
        count += 1
        if count >= 10:
            break

print("\n" + "="*70)
print("DOUBLONS détectés par nom+taille (20 premiers)")
print("="*70)
count = 0
for rel, dest, year, cat, is_dup in plan:
    if dest == "DOUBLONS":
        print(f"  {rel[:90]}")
        count += 1
        if count >= 20:
            break

print(f"\nTotal doublons : {doublon_count[0]} fichiers, {human_size(doublon_count[1])}")
print("\nAnalyse terminée — aucun fichier déplacé.")
