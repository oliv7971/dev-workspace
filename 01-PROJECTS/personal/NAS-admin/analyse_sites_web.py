"""
Analyse du contenu de 82-sites_web.

Parcourt le répertoire, classe chaque fichier par catégorie (contenu utile,
junk web, inconnu), et génère un rapport par dossier et par extension.

Usage:
    python analyse_sites_web.py
    python analyse_sites_web.py > reports/analyse_sites_web.txt

Note : kronoscopie est exclu de l'analyse (dossiers protégés).
"""
import os
import sys
from collections import defaultdict

BASE = r'\\Nas_louhans_2\01-ds420-data\82-sites_web'

# Dossiers à ignorer complètement (Synology + kronoscopie)
SKIP_DIRS = {'@eaDir', '#recycle', '@tmp', '.SynologyWorkingDirectory',
             '$RECYCLE.BIN', 'System Volume Information'}

# Dossiers kronoscopie à protéger (ne pas toucher)
KRONOSCOPIE_DIRS = {'www.kronoscopie.fr', 'kronoscopie secours'}

# ── Catégories d'extensions ────────────────────────────────────────────────

# Junk web : artefacts typiques d'une aspiration de site
JUNK_EXT = {
    # Pages web (htm/html conservés – contenu principal du site)
    '.shtml', '.xhtml',
    # Styles et scripts
    '.css', '.js', '.mjs', '.map', '.ts', '.jsx', '.tsx',
    '.less', '.sass', '.scss',
    # Polices web
    '.woff', '.woff2', '.eot',
    # Scripts serveur inutiles hors ligne
    '.php', '.php3', '.php4', '.php5', '.phtml',
    '.asp', '.aspx', '.cfc', '.cfm', '.cgi', '.pl',
    # Divers web
    '.htaccess', '.htpasswd',
    '.ico',          # favicons
    '.swf',          # Flash
    '.appcache',
    '.webmanifest',
}

# Contenu utile à conserver impérativement
KEEP_EXT = {
    # Archives
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tgz', '.z',
    # Documents
    '.pdf', '.doc', '.docx', '.odt', '.rtf',
    '.xls', '.xlsx', '.ods', '.csv',
    '.ppt', '.pptx', '.odp',
    # MIDI et notation musicale
    '.mid', '.midi', '.kar',
    '.mxl', '.musicxml', '.xml',   # MusicXML / scores
    '.capx', '.cap',               # Capella
    '.nbs',                        # Noteblock Studio
    '.ptb',                        # PowerTab
    '.gp', '.gp3', '.gp4', '.gp5', '.gpx', '.tg', '.tef',  # Guitar Pro / TuxGuitar
    '.ly', '.lilypond',            # Lilypond
    '.sib', '.mscz', '.mscx',     # Sibelius / MuseScore
    # Audio
    '.mp3', '.wav', '.ogg', '.flac', '.aac', '.wma', '.m4a',
    '.opus', '.ape', '.ac3', '.aiff', '.aif',
    # Vidéo
    '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v',
    '.mpg', '.mpeg', '.3gp',
    # Images (potentiellement contenu)
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
    '.tif', '.tiff', '.psd', '.xcf', '.raw', '.cr2', '.nef',
    # Scripts / code utiles
    '.py', '.bas', '.vba', '.vbs', '.lsp', '.lisp', '.scm',
    '.bat', '.sh',
    # CAO / SIG
    '.dwg', '.dxf', '.shp', '.shx', '.dbf', '.prj', '.gml',
    # Tablatures texte
    '.gpx',   # aussi Guitar Pro
    '.txt',   # paroles, tablatures texte, README
    # Data / config utiles
    '.json',  # données structurées
    '.svg',   # diagrams / partitions vectorielles
    # Autres
    '.exe', '.msi', '.dmg',   # installeurs
}


def fmt(size):
    if size >= 1e9:
        return f"{size/1e9:.1f} Go"
    if size >= 1e6:
        return f"{size/1e6:.1f} Mo"
    if size >= 1e3:
        return f"{size/1e3:.1f} Ko"
    return f"{size} o"


def classify(ext):
    e = ext.lower()
    if e in JUNK_EXT:
        return 'junk'
    if e in KEEP_EXT:
        return 'keep'
    return 'unknown'


def main():
    # Statistiques globales
    stats = {
        'junk':    {'count': 0, 'size': 0},
        'keep':    {'count': 0, 'size': 0},
        'unknown': {'count': 0, 'size': 0},
    }
    # Par dossier de 1er niveau
    by_folder = defaultdict(lambda: {
        'junk': {'count': 0, 'size': 0},
        'keep': {'count': 0, 'size': 0},
        'unknown': {'count': 0, 'size': 0},
        'kronoscopie': False,
    })
    # Extensions inconnues
    unknown_exts = defaultdict(lambda: {'count': 0, 'size': 0})

    kronoscopie_stats = {'count': 0, 'size': 0}

    for entry in os.scandir(BASE):
        if not entry.is_dir(follow_symlinks=False):
            continue
        folder_name = entry.name
        if folder_name in SKIP_DIRS:
            continue

        is_krono = folder_name in KRONOSCOPIE_DIRS
        if is_krono:
            by_folder[folder_name]['kronoscopie'] = True

        for root, dirs, files in os.walk(entry.path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in files:
                fp = os.path.join(root, fn)
                try:
                    size = os.path.getsize(fp)
                except OSError:
                    continue
                ext = os.path.splitext(fn)[1]
                cat = classify(ext)

                if is_krono:
                    kronoscopie_stats['count'] += 1
                    kronoscopie_stats['size'] += size
                else:
                    stats[cat]['count'] += 1
                    stats[cat]['size'] += size
                    by_folder[folder_name][cat]['count'] += 1
                    by_folder[folder_name][cat]['size'] += size
                    if cat == 'unknown':
                        unknown_exts[ext.lower()]['count'] += 1
                        unknown_exts[ext.lower()]['size'] += size

    # ── Rapport ───────────────────────────────────────────────────────────

    sep = '=' * 72
    print(sep)
    print("ANALYSE 82-sites_web")
    print(sep)

    total_count = sum(s['count'] for s in stats.values())
    total_size  = sum(s['size']  for s in stats.values())
    print(f"\nFichiers analysés : {total_count:,}  ({fmt(total_size)})")
    print(f"  Junk web         : {stats['junk']['count']:,}  ({fmt(stats['junk']['size'])})")
    print(f"  Contenu utile    : {stats['keep']['count']:,}  ({fmt(stats['keep']['size'])})")
    print(f"  Inconnus         : {stats['unknown']['count']:,}  ({fmt(stats['unknown']['size'])})")
    print(f"\nKronoscopie (protégé) : {kronoscopie_stats['count']:,}  ({fmt(kronoscopie_stats['size'])})")

    # ── Par dossier ───────────────────────────────────────────────────────
    print(f"\n{sep}")
    print("PAR DOSSIER (trié par taille junk décroissante)")
    print(sep)
    folders_sorted = sorted(
        by_folder.items(),
        key=lambda kv: kv[1]['junk']['size'],
        reverse=True
    )
    hdr = f"{'Dossier':<35} {'Junk':>10} {'Utile':>10} {'Inconnu':>10}"
    print(hdr)
    print('-' * 72)
    for name, s in folders_sorted:
        flag = ' [KRONOSCOPIE]' if s['kronoscopie'] else ''
        line = (
            f"{(name[:33] + '..' if len(name) > 35 else name):<35}"
            f" {fmt(s['junk']['size']):>10}"
            f" {fmt(s['keep']['size']):>10}"
            f" {fmt(s['unknown']['size']):>10}"
            f"{flag}"
        )
        print(line)

    # ── Extensions inconnues ──────────────────────────────────────────────
    if unknown_exts:
        print(f"\n{sep}")
        print("EXTENSIONS INCONNUES (à classifier manuellement)")
        print(sep)
        for ext, s in sorted(unknown_exts.items(), key=lambda kv: kv[1]['size'], reverse=True):
            print(f"  {ext or '(sans ext)':<20} {s['count']:>5} fichiers  {fmt(s['size']):>10}")

    print(f"\n{sep}")
    print("FIN DU RAPPORT")
    print(sep)


if __name__ == '__main__':
    main()
