"""Plan de réorganisation - dry run rapide (sans compter les fichiers)"""
import os

BASE = r"\\Nas_travail\01-ds414-data\11-TSGT"
AC = os.path.join(BASE, "_A CLASSER")

MOVES = [
    ("exercices",           "12-TP\\exercices"),
    ("TSGT-2011-2012",      "12-TP\\TSGT-2011-2012"),
    ("releves_batiment",    "12-TP\\releves-batiment"),
    ("routier-covadis",     "12-TP\\routier-covadis"),
    ("route",               "12-TP\\routier-covadis\\route"),
    ("sig",                 "12-TP\\sig"),
    ("GPStestcalcul2012",   "12-TP\\GPS-calcul-2012"),
    ("stages",              "12-TP\\stages"),
    ("cle_20120412",        "13-DONNEES-COURS\\cle_20120412"),
    ("cle_20120606",        "13-DONNEES-COURS\\cle_20120606"),
    ("data_tsgt_2011-2012", "13-DONNEES-COURS\\data_tsgt_2011-2012"),
    ("tsgt",                "13-DONNEES-COURS\\tsgt"),
    ("exam",                "13-DONNEES-COURS\\exam"),
    ("afpa017",             "11-COURS\\formations\\afpa017"),
    ("revisions_cnfpt",     "11-COURS\\formations\\revisions_cnfpt"),
    ("DOCS",                "21-DOCS\\divers\\DOCS"),
    ("docs2",               "21-DOCS\\divers\\docs2"),
    ("docs7",               "21-DOCS\\divers\\docs7"),
    ("MESDOCS",             "21-DOCS\\divers\\MESDOCS"),
    ("images",              "21-DOCS\\divers\\images"),
    ("fiches",              "21-DOCS\\modeles\\fiches"),
    ("exemples_plans",      "21-DOCS\\modeles\\exemples_plans"),
    ("gabarits",            "21-DOCS\\modeles\\gabarits"),
    ("modeles-fichiers",    "21-DOCS\\modeles\\modeles-fichiers"),
    ("Profils Types",       "21-DOCS\\modeles\\Profils Types"),
    ("leve_code",           "21-DOCS\\codes-leve"),
    ("ressources",          "21-DOCS\\ressources"),
    ("leica",               "31-SOFTS\\leica"),
    ("data",                "31-SOFTS\\data-cyclone"),
    ("install",             "31-SOFTS\\install-aclasser"),
    ("PrintScreen Files",   "41-CAPTURES\\PrintScreen Files"),
    ("100OLYMP",            "41-CAPTURES\\100OLYMP"),
    ("rapports",            "01-ADMINISTRATIF\\rapports"),

    # Fichiers en vrac a la racine
    ("TP7-CHEMINEMENT_OB.dwg",         "12-TP\\divers\\TP7-CHEMINEMENT_OB.dwg"),
    ("PLAN8APPART.dwg",                "12-TP\\divers\\PLAN8APPART.dwg"),
    ("new block.dwg",                  "12-TP\\divers\\new block.dwg"),
    ("plan_cite_sotenot_isle_les_villenoy.dwg",  "12-TP\\divers\\plan_cite_sotenot_isle_les_villenoy.dwg"),
    ("plan_cite_sotenot_isle_les_villenoy2.dwg", "12-TP\\divers\\plan_cite_sotenot_isle_les_villenoy2.dwg"),
    ("ruedelaglaisiere.dwg",           "12-TP\\divers\\ruedelaglaisiere.dwg"),
    ("rapport_tp22.doc",               "12-TP\\divers\\rapport_tp22.doc"),
    ("tp19-2.pdf",                     "12-TP\\divers\\tp19-2.pdf"),
    ("feuille_calcul_polygo-20111108-pour-tp-corps_de_rue.ods", "12-TP\\divers\\feuille_calcul_polygo-20111108-pour-tp-corps_de_rue.ods"),
    ("releve_cave_herons_20111210.ods", "12-TP\\divers\\releve_cave_herons_20111210.ods"),
    ("releve_cave_herons_20111210-2.ods", "12-TP\\divers\\releve_cave_herons_20111210-2.ods"),
    ("correction niveau apparent sur les distances.xls", "12-TP\\divers\\correction niveau apparent sur les distances.xls"),
    ("Carnet de levé.xls",             "12-TP\\divers\\Carnet de levé.xls"),
    ("ITSEOA - Fas4-TOPOMETRIE - SETRA - FR.pdf", "21-DOCS\\divers\\ITSEOA - Fas4-TOPOMETRIE - SETRA - FR.pdf"),
    ("corrige-bts-batiment-2007-topographie.pdf",  "15-Annales BTS GT\\corrige-bts-batiment-2007-topographie.pdf"),
    ("Tasa Fiche 002 - Les blocs AutoCAD.pdf",    "21-DOCS\\divers\\Tasa Fiche 002 - Les blocs AutoCAD.pdf"),
    ("guide_assainissement.pdf",       "21-DOCS\\divers\\guide_assainissement.pdf"),
    ("notes_autocad.txt",              "21-DOCS\\divers\\notes_autocad.txt"),
    ("ChemiseVerte.pdf",               "21-DOCS\\modeles\\ChemiseVerte.pdf"),
    ("ChemiseVerteSimple.PDF",         "21-DOCS\\modeles\\ChemiseVerteSimple.PDF"),
    ("sauvegarde_données_terrain.pdf", "21-DOCS\\divers\\sauvegarde_données_terrain.pdf"),
    ("Initiation_ArcGis9.pdf",        "12-TP\\sig\\Initiation_ArcGis9.pdf"),
    ("TD_arcgis_etudiants.pdf",        "12-TP\\sig\\TD_arcgis_etudiants.pdf"),
    ("SIG definition.pdf",             "12-TP\\sig\\SIG definition.pdf"),
    ("sig.pdf",                        "12-TP\\sig\\sig.pdf"),
    ("sig1.pdf",                       "12-TP\\sig\\sig1.pdf"),
    ("qgis-1.6.0_user_guide_fr.pdf",  "12-TP\\sig\\qgis-1.6.0_user_guide_fr.pdf"),
    ("lettre_stage_tsgt_hyparc.pdf",   "12-TP\\stages\\lettre_stage_tsgt_hyparc.pdf"),
    ("c-vandroux.JPG",                 "41-CAPTURES\\photos\\c-vandroux.JPG"),
    ("d-gaudillere.JPG",               "41-CAPTURES\\photos\\d-gaudillere.JPG"),
    ("d-soulage.JPG",                  "41-CAPTURES\\photos\\d-soulage.JPG"),
    ("im012.jpg",                      "41-CAPTURES\\photos\\im012.jpg"),
    ("CycloneSetup561.exe",            "31-SOFTS\\data-cyclone\\CycloneSetup561.exe"),
    ("SetupDWGTrueView2013_32bit.exe", "31-SOFTS\\SetupDWGTrueView2013_32bit.exe"),
    ("data_tsgt_2011-2012.zip",        "13-DONNEES-COURS\\data_tsgt_2011-2012.zip"),
]

print("=" * 80)
print("PLAN DE REORGANISATION (dry-run)")
print("=" * 80)

ok_list = []
skip = 0
conflict = 0

for src_rel, dst_rel in MOVES:
    src = os.path.join(AC, src_rel)
    dst = os.path.join(BASE, dst_rel)
    if not os.path.exists(src):
        print(f"  ABSENT   {src_rel}")
        skip += 1
    elif os.path.exists(dst):
        print(f"  CONFLIT  {src_rel} -> {dst_rel}")
        conflict += 1
    else:
        print(f"  OK       {src_rel:<30} -> {dst_rel}")
        ok_list.append((src_rel, dst_rel))

print(f"\nResume: {len(ok_list)} OK, {skip} absents, {conflict} conflits")

# Elements non couverts
planned = set(s for s, _ in MOVES)
rest = [i for i in os.listdir(AC) if i not in planned]
if rest:
    print(f"\nNon couverts par le plan ({len(rest)}):")
    for i in sorted(rest):
        fp = os.path.join(AC, i)
        typ = "DIR " if os.path.isdir(fp) else "FILE"
        print(f"  {typ}  {i}")
