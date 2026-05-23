#!/usr/bin/env python3
"""
cleanup_40_videos.py
Nettoyage de 40-VIDEOS en 3 actions :

  A) Supprimer les fichiers audio (.m4a/.ogg/.opus/.flac) quand une vidéo
     du même nom existe dans le même dossier (résidus yt-dlp)

  B) Déplacer Joe Dassin FLAC vers 41-MUSIQUE

  C) Supprimer les fichiers vraiment inutiles :
     .tmp, .part, .dashvideo, .dashaudio, Thumbs.db,
     .nfo torrent, .url torrent, .html (cpasbien/oxtorrent)

Usage:
    python cleanup_40_videos.py          # dry-run
    python cleanup_40_videos.py --apply  # exécution réelle
"""

import os, sys, io, shutil, logging
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ──────────────────────────────────────────────────────────────────────────────
BASE        = Path(r"\\Nas_louhans_2\01-ds420-data\40-VIDEOS")
MUSIQUE_DIR = Path(r"\\Nas_louhans_2\01-ds420-data\41-MUSIQUE")

# Dossier Joe Dassin à déplacer
DASSIN_SRC = BASE / "03-VIDEOS" / "20-CONCERTS & clips" / "_DASSIN"
DASSIN_DST = MUSIQUE_DIR / "_DASSIN"

APPLY = "--apply" in sys.argv

# Extensions vidéo reconnues
VIDEO_EXT = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.m4v',
             '.mpg', '.mpeg', '.ts', '.m2ts', '.webm', '.ogv'}

# Extensions audio candidats à suppression si vidéo jumelle présente
AUDIO_EXT = {'.m4a', '.ogg', '.opus', '.flac'}

# Fichiers purement inutiles quelle que soit la situation
JUNK_EXACT_NAMES = {'Thumbs.db', 'thumbs.db'}

# Extensions junk inconditionnelles
JUNK_EXT_UNCONDITIONAL = {'.dashvideo', '.dashaudio', '.part'}

# Extensions junk à contenu connu (torrent/pub)
JUNK_EXT_CONDITIONAL = {'.nfo', '.url', '.html', '.tmp', '.bak'}

# ──────────────────────────────────────────────────────────────────────────────

LOG_FILE = Path("reports/cleanup_40_videos_log.txt")
LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger()

log.info("=== MODE EXECUTION ===" if APPLY else "=== DRY-RUN (simulaton) — relancer avec --apply ===")
log.info(f"Dossier : {BASE}\n")

counters = {
    "del_audio_paired": 0,
    "move_dassin": 0,
    "del_junk": 0,
    "skip": 0,
    "err": 0,
    "del_audio_size": 0,
    "del_junk_size": 0,
}


def do_delete(path: Path, reason: str, counter_key: str, size_key: str):
    try:
        sz = path.stat().st_size
    except Exception:
        sz = 0
    log.info(f"  DEL  {reason}")
    log.info(f"       {path.relative_to(BASE)}  ({fmt(sz)})")
    counters[counter_key] += 1
    counters[size_key]    += sz
    if APPLY:
        try:
            path.unlink()
        except Exception as e:
            log.error(f"  ERREUR suppression : {e}")
            counters["err"] += 1
            counters[counter_key] -= 1


def fmt(n):
    for u in ('o', 'Ko', 'Mo', 'Go'):
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} To"


# ══════════════════════════════════════════════════════════════════════════════
# A) Audio jumeau d'une vidéo → supprimer l'audio
# ══════════════════════════════════════════════════════════════════════════════
log.info("=" * 70)
log.info("A) Fichiers audio dont la vidéo du même nom existe (résidus yt-dlp)")
log.info("=" * 70)

for root, dirs, files in os.walk(BASE):
    rp   = Path(root)
    fset = {f.lower(): f for f in files}  # lower -> original
    for f in files:
        fp  = rp / f
        ext = fp.suffix.lower()
        if ext not in AUDIO_EXT:
            continue
        stem = fp.stem
        # Cherche une vidéo de même stem dans le même dossier
        has_video = any((stem + vx).lower() in fset for vx in VIDEO_EXT)
        if has_video:
            do_delete(fp, "audio jumeau vidéo", "del_audio_paired", "del_audio_size")

log.info(f"\n  --> {counters['del_audio_paired']} fichiers audio jumeaux "
         f"({fmt(counters['del_audio_size'])} recoverable)\n")


# ══════════════════════════════════════════════════════════════════════════════
# B) Joe Dassin FLAC → 41-MUSIQUE
# ══════════════════════════════════════════════════════════════════════════════
log.info("=" * 70)
log.info("B) Déplacement Joe Dassin FLAC → 41-MUSIQUE")
log.info("=" * 70)

if DASSIN_SRC.exists():
    # Compter les fichiers
    nb = sum(1 for _ in DASSIN_SRC.rglob("*") if _.is_file())
    sz = sum(f.stat().st_size for f in DASSIN_SRC.rglob("*") if f.is_file())
    log.info(f"  SRC : {DASSIN_SRC}")
    log.info(f"  DST : {DASSIN_DST}")
    log.info(f"  {nb} fichiers, {fmt(sz)}")
    if DASSIN_DST.exists():
        log.warning(f"  ATTENTION : destination existe déjà — déplacement ignoré")
        counters["skip"] += 1
    else:
        counters["move_dassin"] = nb
        if APPLY:
            try:
                MUSIQUE_DIR.mkdir(parents=True, exist_ok=True)
                shutil.move(str(DASSIN_SRC), str(DASSIN_DST))
                log.info(f"  OK déplacé")
            except Exception as e:
                log.error(f"  ERREUR : {e}")
                counters["err"] += 1
                counters["move_dassin"] = 0
        else:
            log.info(f"  [DRY-RUN] serait déplacé")
else:
    log.warning(f"  Dossier source introuvable : {DASSIN_SRC}")

log.info("")


# ══════════════════════════════════════════════════════════════════════════════
# C) Fichiers junk inconditionnels
# ══════════════════════════════════════════════════════════════════════════════
log.info("=" * 70)
log.info("C) Suppression fichiers inutiles (Thumbs.db, .part, .tmp, .nfo, .url, .html torrent...)")
log.info("=" * 70)

for root, dirs, files in os.walk(BASE):
    rp = Path(root)
    for f in files:
        fp  = rp / f
        ext = fp.suffix.lower()
        name = fp.name

        # Thumbs.db
        if name in JUNK_EXACT_NAMES:
            do_delete(fp, "Thumbs.db", "del_junk", "del_junk_size")
            continue

        # Extensions toujours junk
        if ext in JUNK_EXT_UNCONDITIONAL:
            do_delete(fp, f"junk ({ext})", "del_junk", "del_junk_size")
            continue

        # .tmp : seulement les gros (résidus de téléchargement vidéo)
        if ext == '.tmp':
            do_delete(fp, ".tmp résidu téléchargement", "del_junk", "del_junk_size")
            continue

        # .nfo : fichiers info torrent (petits, pas des fichiers légitimes)
        if ext == '.nfo':
            do_delete(fp, ".nfo torrent", "del_junk", "del_junk_size")
            continue

        # .url : liens torrent
        if ext == '.url':
            do_delete(fp, ".url torrent", "del_junk", "del_junk_size")
            continue

        # .bak : fichiers backup
        if ext == '.bak':
            do_delete(fp, ".bak backup", "del_junk", "del_junk_size")
            continue

        # .html : pages pub piratage (cpasbien, oxtorrent)
        if ext in ('.html', '.htm'):
            name_lower = name.lower()
            if any(k in name_lower for k in ('cpasbien', 'oxtorrent', 'waz-network',
                                              'extreme-down', 'torrent', 'film et serie')):
                do_delete(fp, f".html pub/piratage", "del_junk", "del_junk_size")
            continue

log.info(f"\n  --> {counters['del_junk']} fichiers junk "
         f"({fmt(counters['del_junk_size'])} recoverable)\n")


# ══════════════════════════════════════════════════════════════════════════════
# RÉSUMÉ
# ══════════════════════════════════════════════════════════════════════════════
log.info("=" * 70)
log.info("RÉSUMÉ")
log.info("=" * 70)
action = "effectués" if APPLY else "prévus"
log.info(f"  A) Audio jumeaux supprimés {action}  : {counters['del_audio_paired']}  ({fmt(counters['del_audio_size'])})")
log.info(f"  B) Fichiers Dassin déplacés {action} : {counters['move_dassin']}")
log.info(f"  C) Fichiers junk supprimés {action}  : {counters['del_junk']}  ({fmt(counters['del_junk_size'])})")
log.info(f"  Erreurs                               : {counters['err']}")
total_saved = counters['del_audio_size'] + counters['del_junk_size']
log.info(f"\n  Espace récupérable total              : {fmt(total_saved)}")
log.info("")
