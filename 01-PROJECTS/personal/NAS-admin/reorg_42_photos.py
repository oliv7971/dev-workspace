#!/usr/bin/env python3
"""
reorg_42_photos.py
Reorganise le contenu de \\Nas_louhans_2\\01-ds420-data\\42-PHOTOS
selon une structure thematique.

Structure cible :
  00-ALBUMS/       Albums thematiques (evenements, lieux, voyages)
  01-ANNEES/       Dossiers avec date en prefixe (YYYYMM, YYYYMMDD, YY-MM-DD)
  02-TELEPHONE/    Photos issues de telephones / appareils
  03-TRAVAIL/      Photos chantiers, topographie, pro
  04-CAPTURES-ECRAN/  Screenshots et copies d'ecran
  80-IMAGES-SCANS/ Images, cliparts, scans
  90-a_classer/    Dossiers ambigus a trier manuellement

Usage:
    python reorg_42_photos.py          # dry-run
    python reorg_42_photos.py --apply  # execution reelle
"""

import os
import sys
import shutil
import logging
from pathlib import Path

BASE = Path(r"\\Nas_louhans_2\01-ds420-data\42-PHOTOS")
APPLY = "--apply" in sys.argv

LOG_FILE = Path("reports/reorg_42_photos_log.txt")
LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)),
    ],
)
log = logging.getLogger()

if APPLY:
    log.info("=== MODE EXÉCUTION ===")
else:
    log.info("=== DRY-RUN (simulation) — relancer avec --apply pour exécuter ===")

# ──────────────────────────────────────────────────────────────────────────────
# Déplacements : (nom_actuel_dans_42-PHOTOS, sous-dossier_cible, description)
# ──────────────────────────────────────────────────────────────────────────────
MOVES = [
    # ── 01-ANNEES ─────────────────────────────────────────────────────────────
    # Dossiers avec préfixe date YYYYMMDD, YYYYMM, YY-MM-DD
    ("20050700_Torpes-randos",                "01-ANNEES", "Randos Torpes juillet 2005"),
    ("20060618MusicImpro2",                   "01-ANNEES", "Musique impro juin 2006"),
    ("20060620_MusicImpro",                   "01-ANNEES", "Musique impro juin 2006"),
    ("20060710_photos-jura",                  "01-ANNEES", "Photos Jura juillet 2006"),
    ("20060723_AnniversaireValentin",         "01-ANNEES", "Anniversaire juillet 2006"),
    ("20061100_Sahara_nov2006",               "01-ANNEES", "Sahara novembre 2006"),
    ("20070115_cerene",                       "01-ANNEES", "Cerene janvier 2007"),
    ("20070115_metz",                         "01-ANNEES", "Metz janvier 2007"),
    ("20070301_installation -S2k - EPG",      "01-ANNEES", "Installation mars 2007"),
    ("20070501_apprat_troyes",                "01-ANNEES", "Appartement Troyes mai 2007"),
    ("20070603_metz",                         "01-ANNEES", "Metz juin 2007"),
    ("20070615_verdun",                       "01-ANNEES", "Verdun juin 2007"),
    ("20070801_champagne",                    "01-ANNEES", "Champagne aout 2007"),
    ("20070900_ALGER",                        "01-ANNEES", "Alger septembre 2007"),
    ("20070900_troyes_centreville",           "01-ANNEES", "Troyes centre septembre 2007"),
    ("20071021-2017-24",                      "01-ANNEES", "Octobre 2007"),
    ("20071021-belfort-fribourg-montbeliard", "01-ANNEES", "Belfort-Fribourg octobre 2007"),
    ("2008-06-15",                            "01-ANNEES", "Juin 2008"),
    ("2008-07-06",                            "01-ANNEES", "Juillet 2008"),
    ("2008-09-04",                            "01-ANNEES", "Septembre 2008"),
    ("20100510-canaldunivernais",             "01-ANNEES", "Canal du Nivernais mai 2010"),
    ("2012 meaux",                            "01-ANNEES", "Meaux 2012"),
    ("2012_mai_appartement_LAPRAZ",           "01-ANNEES", "Appartement Lapraz mai 2012"),
    ("2012_mai_appartement_LAPRAZ_etatlieux", "01-ANNEES", "Etat lieux Lapraz mai 2012"),
    ("2012_mai_modane",                       "01-ANNEES", "Modane mai 2012"),
    ("2012_mai_savoie",                       "01-ANNEES", "Savoie mai 2012"),
    ("2012_mai_VIOLAY",                       "01-ANNEES", "Violay mai 2012"),
    ("201303",                                "01-ANNEES", "Mars 2013"),
    ("201304",                                "01-ANNEES", "Avril 2013"),
    ("201305",                                "01-ANNEES", "Mai 2013"),
    ("201310",                                "01-ANNEES", "Octobre 2013"),
    ("201311",                                "01-ANNEES", "Novembre 2013"),
    ("201312",                                "01-ANNEES", "Decembre 2013"),
    ("201401",                                "01-ANNEES", "Janvier 2014"),
    ("201402",                                "01-ANNEES", "Fevrier 2014"),
    ("201402A0",                              "01-ANNEES", "Fevrier 2014 B"),
    ("201403",                                "01-ANNEES", "Mars 2014"),
    ("201404",                                "01-ANNEES", "Avril 2014"),
    ("201405",                                "01-ANNEES", "Mai 2014"),
    ("160310",                                "01-ANNEES", "Mars 2016"),
    ("19-03-20",                              "01-ANNEES", "Mars 2019"),
    ("19-04-01-appareil person",              "01-ANNEES", "Avril 2019 appareil"),
    ("19-06-03",                              "01-ANNEES", "Juin 2019"),
    ("photos-19-02-14",                       "01-ANNEES", "Fevrier 2019"),
    ("photos-19-03-06",                       "01-ANNEES", "Mars 2019"),
    ("photo_20120406",                        "01-ANNEES", "Avril 2012"),
    ("alger_2007-09-22-1026-14",              "01-ANNEES", "Alger septembre 2007"),
    ("PHOTOS 2019 2020",                      "01-ANNEES", "Photos 2019-2020"),
    ("PHOTOS 2020",                           "01-ANNEES", "Photos 2020"),

    # ── 02-TELEPHONE ──────────────────────────────────────────────────────────
    ("50-telephone",                          "02-TELEPHONE", "Photos telephone"),
    ("100OLYMP",                              "02-TELEPHONE", "Olympus carte memoire"),
    ("olympus",                               "02-TELEPHONE", "Olympus"),

    # ── 03-TRAVAIL ────────────────────────────────────────────────────────────
    ("BOULOT CHANTIER TUNNEL FREJUS",         "03-TRAVAIL", "Chantier tunnel Frejus"),
    ("photos xcore",                          "03-TRAVAIL", "Photos topographie Xcore"),
    ("cours_tsgt_meaux",                      "03-TRAVAIL", "Cours TSGT Meaux"),
    ("MEAUX-TSGT",                            "03-TRAVAIL", "TSGT Meaux"),
    ("FichIGN-TP25",                          "03-TRAVAIL", "Fiches IGN TP25"),
    ("Ouvrages",                              "03-TRAVAIL", "Photos ouvrages"),
    ("phtos_maintenance_secu2000_20070713",   "03-TRAVAIL", "Maintenance secu 2007"),

    # ── 04-CAPTURES-ECRAN ─────────────────────────────────────────────────────
    ("copies ecran",                          "04-CAPTURES-ECRAN", "Copies ecran"),
    ("PrintScreen Files",                     "04-CAPTURES-ECRAN", "PrintScreen"),
    ("PrintScreen Files 2",                   "04-CAPTURES-ECRAN", "PrintScreen 2"),
    ("screenshots",                           "04-CAPTURES-ECRAN", "Screenshots"),
    ("mescopiesecranA",                       "04-CAPTURES-ECRAN", "Copies ecran A"),
    ("Desktop",                               "04-CAPTURES-ECRAN", "Bureau / desktop"),

    # ── 80-IMAGES-SCANS ───────────────────────────────────────────────────────
    ("80 images & scans",                     "80-IMAGES-SCANS", "Images et scans"),
    ("images",                                "80-IMAGES-SCANS", "Images"),

    # ── 00-ALBUMS ─────────────────────────────────────────────────────────────
    ("09-photos",                             "00-ALBUMS", "Album 09"),
    ("NORVEGE",                               "00-ALBUMS", "Voyage Norvege"),
    ("Panama",                                "00-ALBUMS", "Voyage Panama"),
    ("AVRIEUX",                               "00-ALBUMS", "AVRIEUX"),
    ("AVRIEUX-VILLARODIN",                    "00-ALBUMS", "AVRIEUX-VILLARODIN"),
    ("ENVIRONS-AVRIEUX",                      "00-ALBUMS", "Environs AVRIEUX"),
    ("appart avrieux",                        "00-ALBUMS", "Appartement AVRIEUX"),
    ("appart saudron",                        "00-ALBUMS", "Appartement Saudron"),
    ("appartement_87_rue_de_la_paix_avant_travaux", "00-ALBUMS", "Appart 87 rue de la paix"),
    ("lapraz_et_standre",                     "00-ALBUMS", "Lapraz et Saint-Andre"),
    ("region_de_modane",                      "00-ALBUMS", "Region de Modane"),
    ("chambery-lebourget",                    "00-ALBUMS", "Chambery Le Bourget"),
    ("CHAMBERY",                              "00-ALBUMS", "Chambery"),
    ("chambre",                               "00-ALBUMS", "Chambre"),
    ("LA NORMA",                              "00-ALBUMS", "La Norma"),
    ("Haute-Savoie",                          "00-ALBUMS", "Haute-Savoie"),
    ("PHOTOS_Haute_Savoie_2009",              "00-ALBUMS", "Haute-Savoie 2009"),
    ("PHOTOS_les_rousses_2008_decembre",      "00-ALBUMS", "Les Rousses decembre 2008"),
    ("photos_lyon_20090430",                  "00-ALBUMS", "Lyon avril 2009"),
    ("photos_paris_20091117",                 "00-ALBUMS", "Paris novembre 2009"),
    ("sahara_non_confidentiel",               "00-ALBUMS", "Sahara"),
    ("sahara_nov2006",                        "00-ALBUMS", "Sahara novembre 2006"),
    ("photos-alger",                          "00-ALBUMS", "Alger"),
    ("Bel algerie",                           "00-ALBUMS", "Algerie"),
    ("Lourdes",                               "00-ALBUMS", "Lourdes"),
    ("disney",                                "00-ALBUMS", "Disney"),
    ("Noces de diamant Calou",                "00-ALBUMS", "Noces de diamant Calou"),
    ("Noel 2006",                             "00-ALBUMS", "Noel 2006"),
    ("Anniversaire des jumeaux (25 novembre 2006)", "00-ALBUMS", "Anniversaire jumeaux 2006"),
    ("diapo pour anniv jumeaux",              "00-ALBUMS", "Diaporama anniversaire jumeaux"),
    ("Photos cousinades 2019",                "00-ALBUMS", "Cousinades 2019"),
    ("Photos Florence",                       "00-ALBUMS", "Florence"),
    ("PHOTOS MONTJAY",                        "00-ALBUMS", "Montjay"),
    ("photos nirajan",                        "00-ALBUMS", "Nirajan"),
    ("SEA - Photos Aériennes",                "00-ALBUMS", "Photos aeriennes SEA"),
    ("Boeme",                                 "00-ALBUMS", "Boheme/Boeme"),
    ("Bord de mer",                           "00-ALBUMS", "Bord de mer"),
    ("belvédères du Jura",                    "00-ALBUMS", "Belvederes du Jura"),
    ("Charente Mediane",                      "00-ALBUMS", "Charente Mediane"),
    ("Charente Nord",                         "00-ALBUMS", "Charente Nord"),
    ("Claix",                                 "00-ALBUMS", "Claix"),
    ("Indre",                                 "00-ALBUMS", "Indre"),
    ("Auxance",                               "00-ALBUMS", "Auxance"),
    ("Piliers",                               "00-ALBUMS", "Piliers"),
    ("Panama",                                "00-ALBUMS", "Panama"),
    ("Papi mami à la mer",                    "00-ALBUMS", "Papi mami a la mer"),
    ("Illuminations Frangy",                  "00-ALBUMS", "Illuminations Frangy"),
    ("NA_bar_aube",                           "00-ALBUMS", "Bar-sur-Aube"),
    ("NA_cartes postales",                    "00-ALBUMS", "Cartes postales"),
    ("NA_Chammagne-montgueux-othe",           "00-ALBUMS", "Champagne Montgueux"),
    ("maison des Bonnets",                    "00-ALBUMS", "Maison des Bonnets"),
    ("oboissard84067",                        "00-ALBUMS", "oboissard"),
    ("route-troyes-montbeliard",              "00-ALBUMS", "Route Troyes-Montbeliard"),
    ("postegaz-dierrey",                      "00-ALBUMS", "Poste gaz Dierrey"),

    # ── 90-a_classer ──────────────────────────────────────────────────────────
    ("photos a classer",                      "90-a_classer", "A classer"),
    ("Nouveau dossier",                       "90-a_classer", "Nouveau dossier"),
    ("BACK",                                  "90-a_classer", "Backup inconnu"),
    ("RATEES",                                "90-a_classer", "Photos ratees"),
    ("album",                                 "90-a_classer", "Album non classe"),
    ("perso",                                 "90-a_classer", "Personnel"),
    ("pose",                                  "90-a_classer", "Pose"),
    ("recent",                                "90-a_classer", "Recent"),
    ("Mes photos Logitech",                   "90-a_classer", "Photos Logitech"),
    ("photos.zip",                            "90-a_classer", "Archive photos zip"),
]

# Dossiers conservés à la racine (déjà bien nommés ou à traiter séparément)
KEEP = [
    "00-ALBUMS",
    "01-ANNEES",
    "02-TELEPHONE",
    "03-TRAVAIL",
    "04-CAPTURES-ECRAN",
    "80-IMAGES-SCANS",
    "90-a_classer",
    "31-PHOTOS",   # doublons à analyser séparément
    "PHOTOS",      # doublons à analyser séparément
    "31-PHOTOS chantier",
    "vouglans.jpg",
]

log.info(f"\nSource : {BASE}")
log.info(f"Mode   : {'EXÉCUTION' if APPLY else 'DRY-RUN'}\n")

counters = {"ok": 0, "skip": 0, "err": 0}
current_dest = None

log.info("=" * 70)
log.info("DÉPLACEMENTS")
log.info("=" * 70)

for name, dest_sub, desc in MOVES:
    src  = BASE / name
    dst_dir  = BASE / dest_sub
    dst  = dst_dir / name

    if dest_sub != current_dest:
        log.info(f"\n  --> {dest_sub}/")
        current_dest = dest_sub

    if not src.exists():
        log.info(f"      ABSENT   {name}")
        counters["skip"] += 1
        continue

    if dst.exists():
        log.warning(f"      CONFLIT  {name} → déjà dans {dest_sub}/ — SKIP")
        counters["skip"] += 1
        continue

    log.info(f"      MOVE  {name}  ({desc})")
    counters["ok"] += 1

    if APPLY:
        try:
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
        except Exception as e:
            log.error(f"      ERREUR  {name}: {e}")
            counters["err"] += 1
            counters["ok"] -= 1

log.info("\n" + "=" * 70)
log.info("RÉSUMÉ")
log.info("=" * 70)
if APPLY:
    log.info(f"  Déplacements effectués : {counters['ok']}")
    log.info(f"  Ignorés (absent/conflit): {counters['skip']}")
    log.info(f"  Erreurs                : {counters['err']}")
else:
    log.info(f"  Actions planifiées     : {counters['ok']} déplacements")
    log.info(f"  Ignorés (absent/conflit): {counters['skip']}")
    log.info(f"\n  → relancer avec --apply pour exécuter")
