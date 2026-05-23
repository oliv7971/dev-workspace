"""
Nettoyage de 82-sites_web : suppression des artefacts d'aspiration de sites
(HTML, CSS, JS, polices web, scripts serveur, etc.).

Les dossiers kronoscopie sont TOUJOURS exclus.
Les fichiers de contenu (PDF, ZIP, MIDI, audio, vidéo, images, etc.) sont conservés.

Usage:
    python cleanup_sites_web.py              # dry-run : liste ce qui serait supprimé
    python cleanup_sites_web.py --execute    # suppression réelle
    python cleanup_sites_web.py --folder midifind  # dry-run sur un seul dossier
    python cleanup_sites_web.py --folder midifind --execute  # exécution sur un seul dossier

Options:
    --execute     effectue vraiment les suppressions
    --folder NOM  limite au sous-dossier NOM (nom exact, sensible à la casse)
"""
import os
import sys
from collections import defaultdict

BASE = r'\\Nas_louhans_2\01-ds420-data\82-sites_web'

EXECUTE  = '--execute' in sys.argv
FOLDER_ARG = None
if '--folder' in sys.argv:
    idx = sys.argv.index('--folder')
    if idx + 1 < len(sys.argv):
        FOLDER_ARG = sys.argv[idx + 1]

# ── Dossiers à ignorer (Synology + kronoscopie – JAMAIS touché) ─────────────
SKIP_DIRS = {'@eaDir', '#recycle', '@tmp', '.SynologyWorkingDirectory',
             '$RECYCLE.BIN', 'System Volume Information'}

KRONOSCOPIE_DIRS = {'www.kronoscopie.fr', 'kronoscopie secours'}

# ── Extensions clairement inutiles (junk d'aspiration web) ──────────────────
# MODIFIER cette liste si tu veux affiner le périmètre de suppression.
JUNK_EXT = {
    # Pages web (htm/html conservés – contenu principal du site)
    '.shtml', '.xhtml',
    # Styles et scripts
    '.css', '.js', '.mjs', '.map', '.ts', '.jsx', '.tsx',
    '.less', '.sass', '.scss',
    # Polices web (non utilisables offline)
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

# Fichiers de métadonnées courants à supprimer aussi
JUNK_FILENAMES = {
    'thumbs.db', '.ds_store', 'desktop.ini', '.htaccess',
    'robots.txt', 'sitemap.xml', 'sitemap.xml.gz',
    'google-site-verification.html',
}


def fmt(size):
    if size >= 1e9:
        return f"{size/1e9:.1f} Go"
    if size >= 1e6:
        return f"{size/1e6:.1f} Mo"
    if size >= 1e3:
        return f"{size/1e3:.1f} Ko"
    return f"{size} o"


def is_junk(filepath: str, filename: str, ext: str) -> tuple[bool, str]:
    """Retourne (True, raison) si le fichier est un artefact web à supprimer."""
    fn_lower = filename.lower()
    ext_lower = ext.lower()

    if fn_lower in JUNK_FILENAMES:
        return True, f"fichier meta ({filename})"

    if ext_lower in JUNK_EXT:
        return True, f"extension web ({ext_lower})"

    return False, ""


def remove_empty_dirs(root_path: str, dry_run: bool) -> int:
    """Supprime les dossiers vides (après nettoyage des fichiers junk).
    Remonte l'arborescence de bas en haut. Retourne le nombre de dossiers supprimés."""
    removed = 0
    # os.walk bottom-up
    for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
        # Ne jamais supprimer la racine d'un dossier de 1er niveau
        if os.path.normpath(dirpath) == os.path.normpath(root_path):
            continue
        try:
            entries = os.listdir(dirpath)
        except OSError:
            continue
        # Ne supprimer que les dossiers vraiment vides
        if not entries:
            if dry_run:
                print(f"  [DOSSIER VIDE] {dirpath}")
            else:
                try:
                    os.rmdir(dirpath)
                    removed += 1
                except OSError as e:
                    print(f"  [ERREUR rmdir] {dirpath}: {e}")
    return removed


def scan_and_cleanup(root_path: str) -> None:
    to_delete: list[tuple[str, int, str]] = []   # (path, size, reason)
    stats_by_reason: dict[str, list[int]] = defaultdict(lambda: [0, 0])  # [count, size]
    total_kept_count = 0
    total_kept_size  = 0
    skipped_krono    = 0

    for entry in os.scandir(root_path):
        if not entry.is_dir(follow_symlinks=False):
            continue
        folder_name = entry.name
        if folder_name in SKIP_DIRS:
            continue
        if folder_name in KRONOSCOPIE_DIRS:
            skipped_krono += 1
            print(f"  [PROTÉGÉ] {folder_name}")
            continue
        if FOLDER_ARG and folder_name != FOLDER_ARG:
            continue

        for dirroot, dirs, files in os.walk(entry.path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in files:
                fp = os.path.join(dirroot, fn)
                try:
                    size = os.path.getsize(fp)
                except OSError:
                    continue
                ext = os.path.splitext(fn)[1]
                junk, reason = is_junk(fp, fn, ext)
                if junk:
                    to_delete.append((fp, size, reason))
                    stats_by_reason[reason][0] += 1
                    stats_by_reason[reason][1] += size
                else:
                    total_kept_count += 1
                    total_kept_size  += size

    # ── Résumé ────────────────────────────────────────────────────────────
    total_del_count = len(to_delete)
    total_del_size  = sum(s for _, s, _ in to_delete)

    print()
    print('=' * 72)
    mode_label = "DRY-RUN (aucune suppression)" if not EXECUTE else "EXÉCUTION RÉELLE"
    print(f"  CLEANUP 82-sites_web  —  {mode_label}")
    print('=' * 72)
    print(f"\n  Dossiers kronoscopie protégés : {skipped_krono}")
    print(f"  Fichiers à supprimer          : {total_del_count:,}  ({fmt(total_del_size)})")
    print(f"  Fichiers conservés            : {total_kept_count:,}  ({fmt(total_kept_size)})")

    print(f"\n  {'Raison':<35} {'Fichiers':>8}  {'Taille':>10}")
    print('  ' + '-' * 58)
    for reason, (cnt, sz) in sorted(stats_by_reason.items(), key=lambda kv: kv[1][1], reverse=True):
        print(f"  {reason:<35} {cnt:8,}  {fmt(sz):>10}")

    if not to_delete:
        print("\n  Rien à supprimer.")
        return

    if not EXECUTE:
        print()
        print('─' * 72)
        print("  APERÇU (50 premiers fichiers à supprimer) :")
        print('─' * 72)
        for fp, sz, reason in to_delete[:50]:
            rel = fp[len(BASE):].lstrip('\\')
            print(f"  {fmt(sz):>8}  [{reason}]  {rel}")
        if len(to_delete) > 50:
            print(f"  ... et {len(to_delete) - 50:,} autres fichiers.")
        print()
        print("  ► Pour effectuer la suppression, relance avec --execute")
        return

    # ── Suppression réelle ────────────────────────────────────────────────
    print()
    print("  Suppression en cours…")
    errors = []
    deleted_count = 0
    deleted_size  = 0
    for fp, sz, reason in to_delete:
        try:
            os.remove(fp)
            deleted_count += 1
            deleted_size  += sz
        except OSError as e:
            errors.append((fp, str(e)))

    print(f"  Supprimés : {deleted_count:,} fichiers  ({fmt(deleted_size)})")

    # Nettoyage des dossiers vides
    if FOLDER_ARG:
        targets = [os.path.join(BASE, FOLDER_ARG)]
    else:
        targets = [
            os.path.join(BASE, e.name)
            for e in os.scandir(BASE)
            if e.is_dir() and e.name not in SKIP_DIRS and e.name not in KRONOSCOPIE_DIRS
        ]
    rmdir_count = 0
    for t in targets:
        rmdir_count += remove_empty_dirs(t, dry_run=False)
    if rmdir_count:
        print(f"  Dossiers vides supprimés : {rmdir_count}")

    if errors:
        print(f"\n  ERREURS ({len(errors)}) :")
        for fp, err in errors[:20]:
            rel = fp[len(BASE):].lstrip('\\')
            print(f"    {rel}: {err}")

    print()
    print("  Terminé.")


def main():
    if FOLDER_ARG:
        target = os.path.join(BASE, FOLDER_ARG)
        if not os.path.isdir(target):
            print(f"Erreur : dossier introuvable : {target}")
            sys.exit(1)
        print(f"Périmètre limité au dossier : {FOLDER_ARG}")

    scan_and_cleanup(BASE)


if __name__ == '__main__':
    main()
