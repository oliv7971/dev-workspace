# analyse_11_phase2.py -- Analyse globale des dossiers restants de 11-DEVELOPPEMENT
# Objectif : detecter chevauchements, doublons, repartition par langage
# avant toute reorganisation

import os
import hashlib
from collections import defaultdict

BASE = r'\\Nas_louhans_2\01-ds420-data\10-INFORMATIQUE\11-DEVELOPPEMENT'

# Dossiers a analyser (ce qui reste apres phase 1+2)
FOLDERS = [
    'DEVP', 'developpement', 'sources', 'progs',
    'Topo', 'outils topo', 'CALCUL',
    'Gisement et distance', 'IMPORTXYZ', 'CircleBestFitting',
    'menutopo', 'polyroute', 'AXE',
    'VBA', 'excel',
    'CPP', 'VisualBasic',
    'rubyLibraryDepot',
    'java',
    'lisp',
    'BIBLIOTHEQUE AUTOCAD', 'BATCH',
    '11-CODES EXEMPLES',
    '00.Utilitaire de travail', '04-LASERSCAN',
    '13-FRENEY', '17-PL TMS',
    'admin', 'boulons radio', 'BURE8OLIVIER',
    'demo_scan', 'info', 'Olivier BURE',
    'sources',
]
FOLDERS = list(dict.fromkeys(FOLDERS))  # dedup ordre

# Extension -> langage
EXT_LANG = {
    '.lsp': 'AutoLISP', '.dcl': 'AutoLISP', '.mnu': 'AutoLISP', '.scr': 'AutoLISP',
    '.py':  'Python',
    '.java': 'Java', '.class': 'Java',
    '.vba': 'VBA', '.bas': 'VBA', '.frm': 'VBA', '.cls': 'VBA',
    '.vbs': 'VBScript',
    '.vb':  'VisualBasic',
    '.cs':  'C#',
    '.cpp': 'C++', '.c': 'C++', '.h': 'C++', '.hpp': 'C++',
    '.rb':  'Ruby',
    '.bat': 'Batch', '.cmd': 'Batch',
    '.sh':  'Shell',
    '.sql': 'SQL',
    '.js':  'JavaScript', '.ts': 'TypeScript',
    '.html': 'HTML', '.htm': 'HTML', '.css': 'CSS',
    '.xml': 'XML', '.xsd': 'XML',
    '.xls': 'Excel', '.xlsx': 'Excel', '.xlsm': 'Excel', '.xlsb': 'Excel',
    '.dwg': 'AutoCAD', '.dxf': 'AutoCAD',
    '.pdf': 'Doc', '.doc': 'Doc', '.docx': 'Doc', '.txt': 'Text',
    '.zip': 'Archive', '.rar': 'Archive', '.7z': 'Archive', '.gz': 'Archive',
    '.exe': 'Binary', '.dll': 'Binary', '.lib': 'Binary',
    '.png': 'Image', '.jpg': 'Image', '.gif': 'Image', '.bmp': 'Image',
}

# Collecte tous les fichiers
all_files = []  # (folder, relpath, size)
by_name   = defaultdict(list)  # basename_lower -> [(folder, relpath)]
by_lang   = defaultdict(lambda: defaultdict(int))  # folder -> lang -> count

print(f'Scan de {len(FOLDERS)} dossiers...')
for folder in FOLDERS:
    fpath = os.path.join(BASE, folder)
    if not os.path.exists(fpath):
        print(f'  ABSENT : {folder}')
        continue
    for root, dirs, files in os.walk(fpath):
        # Exclure sous-dossiers connus deja traites
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git')]
        for f in files:
            fp = os.path.join(root, f)
            rel = fp[len(fpath)+1:]
            try:
                sz = os.path.getsize(fp)
            except OSError:
                sz = 0
            all_files.append((folder, rel, sz))
            by_name[f.lower()].append((folder, rel))
            ext = os.path.splitext(f)[1].lower()
            lang = EXT_LANG.get(ext, f'Autre ({ext})' if ext else 'Autre (sans ext)')
            by_lang[folder][lang] += 1

print(f'\nTotal : {len(all_files)} fichiers dans {len(by_lang)} dossiers\n')

# ─── 1. Repartition par dossier et langage dominant ──────────────────────────
print('=' * 70)
print('1. REPARTITION PAR DOSSIER')
print('=' * 70)
for folder in FOLDERS:
    if folder not in by_lang:
        continue
    langs = by_lang[folder]
    total = sum(langs.values())
    top = sorted(langs.items(), key=lambda x: -x[1])[:5]
    top_str = ', '.join(f'{l}:{n}' for l, n in top)
    print(f'  {folder:<35} {total:>5} fichiers  |  {top_str}')

# ─── 2. Chevauchements par nom de fichier ────────────────────────────────────
print('\n' + '=' * 70)
print('2. NOMS DE FICHIERS PRESENTS DANS PLUSIEURS DOSSIERS')
print('=' * 70)
overlaps = {name: locs for name, locs in by_name.items()
            if len(set(loc[0] for loc in locs)) > 1}
print(f'  {len(overlaps)} noms en chevauchement entre dossiers differents')

# Grouper les chevauchements par paire de dossiers
pair_count = defaultdict(int)
for name, locs in overlaps.items():
    folders_involved = sorted(set(loc[0] for loc in locs))
    for i in range(len(folders_involved)):
        for j in range(i+1, len(folders_involved)):
            pair_count[(folders_involved[i], folders_involved[j])] += 1

print('\n  Paires de dossiers avec le plus de noms en commun :')
for (f1, f2), cnt in sorted(pair_count.items(), key=lambda x: -x[1])[:20]:
    print(f'    {f1}  <->  {f2}  :  {cnt} noms communs')

# ─── 3. Doublons exacts (meme nom + meme taille) ─────────────────────────────
print('\n' + '=' * 70)
print('3. DOUBLONS EXACTS (meme nom + meme taille, dossiers differents)')
print('=' * 70)
by_name_size = defaultdict(list)
for folder, rel, sz in all_files:
    key = (os.path.basename(rel).lower(), sz)
    by_name_size[key].append((folder, rel))

exact_dups = {k: v for k, v in by_name_size.items()
              if len(set(loc[0] for loc in v)) > 1}
print(f'  {len(exact_dups)} fichiers (nom+taille) en doublon entre dossiers')
print('\n  Exemples (50 premiers) :')
for (name, sz), locs in sorted(exact_dups.items(), key=lambda x: -x[0][1])[:50]:
    folders = [loc[0] for loc in locs]
    sz_str = f'{sz:,}' if sz < 1024*1024 else f'{sz//1024//1024} Mo'
    print(f'    {name}  ({sz_str})  dans : {folders}')

# ─── 4. Vue synthetique par langage (tous dossiers confondus) ────────────────
print('\n' + '=' * 70)
print('4. REPARTITION GLOBALE PAR LANGAGE')
print('=' * 70)
lang_total = defaultdict(int)
for folder_langs in by_lang.values():
    for lang, cnt in folder_langs.items():
        lang_total[lang] += cnt
for lang, cnt in sorted(lang_total.items(), key=lambda x: -x[1]):
    bar = '#' * min(cnt // 5, 60)
    print(f'  {lang:<25} {cnt:>6}  {bar}')

# ─── 5. Dossiers candidates pour fusion (meme langage dominant) ──────────────
print('\n' + '=' * 70)
print('5. DOSSIERS PAR LANGAGE DOMINANT (candidats fusion)')
print('=' * 70)
dom_lang = {}
for folder, langs in by_lang.items():
    if langs:
        dom = max(langs.items(), key=lambda x: x[1])
        dom_lang[folder] = dom[0]

by_dom = defaultdict(list)
for folder, lang in dom_lang.items():
    by_dom[lang].append(folder)

for lang, flist in sorted(by_dom.items(), key=lambda x: -sum(sum(by_lang[f].values()) for f in x[1])):
    if len(flist) > 1 or sum(sum(by_lang[f].values()) for f in flist) > 10:
        print(f'\n  [{lang}]')
        for f in flist:
            t = sum(by_lang[f].values())
            print(f'    {f:<35} {t} fichiers')
