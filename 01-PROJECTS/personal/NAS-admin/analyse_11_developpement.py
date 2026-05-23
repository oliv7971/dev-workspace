"""
Analyse du dossier 11-DEVELOPPEMENT par type de langage.
Lit le fichier d'inventaire pré-généré (D:\tmp_devp_files.txt).
"""
import os
from collections import defaultdict

INVENTORY_FILE = r"D:\tmp_devp_files.txt"

LANG_MAP = {
    'Python':      ['.py', '.pyw', '.ipynb'],
    'VBA/Excel':   ['.bas', '.cls', '.frm', '.xlsm', '.xls', '.xla', '.xltm', '.xlam', '.xlsx'],
    'AutoLISP':    ['.lsp', '.fas', '.mnl', '.vlx', '.dcl', '.arx'],
    'Java':        ['.java', '.jar'],
    'Batch/Cmd':   ['.bat', '.cmd'],
    'PowerShell':  ['.ps1', '.psm1', '.psd1'],
    'Bash/Shell':  ['.sh', '.bash'],
    'PHP':         ['.php'],
    'JavaScript':  ['.js', '.ts', '.jsx', '.tsx'],
    'Web':         ['.html', '.htm', '.css'],
    'SQL':         ['.sql', '.sqlite'],
    'C/C++':       ['.c', '.cpp', '.h', '.hpp', '.cxx'],
    'VisualBasic': ['.vb', '.vbs'],
    'Ruby':        ['.rb'],
    'XML/Config':  ['.xml', '.json', '.yaml', '.yml', '.ini', '.cfg', '.toml'],
    'Texte/Doc':   ['.txt', '.md', '.rst', '.odt', '.doc', '.docx', '.pdf', '.rtf'],
    'Archive':     ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
    'Image':       ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg'],
    'Junk':        ['.class', '.bak', '.tmp', '.log', '.suo', '.ncb', '.obj', '.pdb'],
    'Executable':  ['.exe', '.dll', '.msi'],
    'Data':        ['.csv', '.dat', '.dat', '.xls'],
}

# Extension -> langage
ext_to_lang = {}
for lang, exts in LANG_MAP.items():
    for ext in exts:
        ext_to_lang[ext] = lang

# Lire le fichier d'inventaire
with open(INVENTORY_FILE, encoding='utf-8', errors='replace') as f:
    lines = [l.strip() for l in f if l.strip()]

# Filtrer les lignes qui ressemblent à des chemins UNC
files = [l for l in lines if l.startswith('\\\\')]
print(f"Total fichiers: {len(files)}")
print()

counts = defaultdict(int)
ext_counts = defaultdict(int)
unknown_exts = defaultdict(int)

for fp in files:
    name = fp.rsplit('\\', 1)[-1] if '\\' in fp else fp
    ext = os.path.splitext(name)[1].lower()
    lang = ext_to_lang.get(ext, 'Autre')
    counts[lang] += 1
    ext_counts[ext] += 1
    if lang == 'Autre':
        unknown_exts[ext] += 1

print("=== PAR LANGAGE ===")
for lang, n in sorted(counts.items(), key=lambda x: -x[1]):
    bar = '#' * (n // 500)
    print(f"  {lang:<20} {n:>6} fichiers  {bar}")

print()
print("=== TOP 50 EXTENSIONS ===")
for ext, n in list(sorted(ext_counts.items(), key=lambda x: -x[1]))[:50]:
    lang = ext_to_lang.get(ext, '?')
    print(f"  {ext:<15} {n:>6}  ({lang})")

print()
print("=== EXTENSIONS INCONNUES (top 30) ===")
for ext, n in list(sorted(unknown_exts.items(), key=lambda x: -x[1]))[:30]:
    print(f"  {ext!r:<20} {n:>6}")

# Analyse par sous-dossier de premier niveau
print()
print("=== PAR DOSSIER TOP-LEVEL ===")
base = r'\\Nas_louhans_2\01-ds420-data\10-INFORMATIQUE\11-DEVELOPPEMENT'
folder_counts = defaultdict(int)
for fp in files:
    rel = fp[len(base):].lstrip('\\')
    top = rel.split('\\')[0] if '\\' in rel else '(racine)'
    folder_counts[top] += 1

for folder, n in sorted(folder_counts.items(), key=lambda x: -x[1]):
    print(f"  {folder:<40} {n:>6} fichiers")
