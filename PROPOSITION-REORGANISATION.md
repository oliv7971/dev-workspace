# Proposition de réorganisation du dev-workspace

## Diagnostic de l'existant

### Problèmes identifiés

1. **Mélange BOULOT / PERSO** : Les projets Korg PA4X (musique) et MIDI cohabitent avec les projets de topographie/tunnel/auscultation dans `01-PROJECTS/python/projets/`
2. **Pas de regroupement thématique** : 38+ projets Python à plat dans un seul répertoire, sans distinction entre axes routiers, auscultation, tunnel, extraction de données, etc.
3. **Dossiers vides ou quasi-vides** : `05-ARCHIVE/` (juste un README), `PA4x-extrait_archives/` (vide), `configs/` (juste `.vscode/`)
4. **Scripts en vrac** : des `.py` isolés dans `python/fichiers/` et `python/projets/` (sans répertoire projet)
5. **Duplication** : `lisp/github-devs/rename_layers/` et `04-EXTERNAL/github-devs/rename_layers/` semblent identiques
6. **Environnement virtuel à la racine** `python/` : `Lib/`, `Scripts/`, `pyvenv.cfg` mélangés avec le code
7. **Scripts PowerShell en vrac** : ~25 scripts à plat sans catégorisation

---

## Inventaire par domaine

### BOULOT - Topographie & Axes Routiers
| Projet | Langage | Description |
|--------|---------|-------------|
| `axe_routier` | Python | Calcul d'axe routier |
| `CalculateurAxes` | Python | Calculateur d'axes complet (le plus abouti) |
| `kit_axe_routier` | Python | Version allégée du calculateur |
| `topoAxis` | Python | Outil CLI axes topo |
| `topoStation` | Python | Station libre, parser GSI |

### BOULOT - Projections & Géométrie
| Projet | Langage | Description |
|--------|---------|-------------|
| `projectionPline3D` | Python | Projection sur polyligne 3D |
| `proj_ligne_2D` | Python | Projection sur ligne 2D |
| `proj_ligne_3D` | Python | Projection sur ligne 3D |
| `comparaisonPolygo` | Python | Comparaison/projection de points sur polygonales |
| `reception ligne 3D` | Python | Réception de lignes 3D (implantation) |

### BOULOT - Auscultation & Monitoring
| Projet | Langage | Description |
|--------|---------|-------------|
| `auscultationCarrefour` | Python | Auscultation de carrefour (le plus gros projet) |
| `recupDernieresAuscultations` | Python | Récupération automatique des dernières mesures |
| `DeplaceAnciennesAuscultations` | Python | Archivage des anciens fichiers de mesure |
| `extractionCibles` | Python | Extraction de coordonnées de cibles |
| `TraitementCarnet` | Python | Traitement et renommage de carnets de terrain |
| `auscult carrefour` | VBA | Module de calcul VBA pour auscultation |

### BOULOT - Tunnel
| Projet | Langage | Description |
|--------|---------|-------------|
| `developpeeTunnel` | Python | Développée de profil tunnel |
| `rapportMensuel` | Python | Génération de rapports mensuels |
| `rapportMensuelV2` | Python | Version refactorisée des rapports |
| `FREJUS` | Python | Spécifique tunnel du Fréjus |
| `concat_csv_beton` | Python | Compilation CSV relevés béton |

### BOULOT - Extraction & Traitement de données
| Projet | Langage | Description |
|--------|---------|-------------|
| `extractPM_PDF` | Python | Extraction de PM depuis PDF |
| `Fiche_implantation` | Python | Génération de fiches d'implantation |
| `csv_tools` | Python | Outils de traitement CSV |
| `remplacerChainesGeobases` | Python | Remplacement de chaînes dans geobases |
| `copie_jobs` | Python | Synchro exports Captivate |

### BOULOT - AutoCAD / AutoLISP
| Projet | Langage | Description |
|--------|---------|-------------|
| `calage coupes` | AutoLISP | Calage 3D de coupes |
| `ConstruitFaces` | AutoLISP | Reconstruction de points Covadis |
| `eclaircir cotes` | AutoLISP | Simplification de cotations |
| `INClabelTextes` | AutoLISP | Labellisation de textes |
| `placePresentations` | AutoLISP | Placement de présentations |
| `place_tcpoint` | AutoLISP | Placement de points TC |
| `vecteursDep` | AutoLISP | Vecteurs de déplacement |
| `a_classer` | AutoLISP | Scripts divers à trier |

### BOULOT - Géodésie (projets externes)
| Projet | Langage | Description |
|--------|---------|-------------|
| `jag3d` | Java | Compensation géodésique 3D (externe) |
| `StaMPS` | C/Matlab | InSAR processing (externe) |
| `ImporterTCPOINT` | .NET | Import de points TC |

### BOULOT - Scripts loose (python/fichiers/)
| Fichier | Description |
|---------|-------------|
| `AmbergExtraitDonnéesMetrés.py` | Extraction données Amberg |
| `AmbergLogExtractor.py` | Extraction logs Amberg |
| `convert_dxf_tms.py` | Conversion DXF TMS |
| `CorrectionAtmo.py` | Correction atmosphérique |
| `creerCalques.py` | Création de calques AutoCAD |
| `impression_niv_excel_vers_pdf.py` | Impression nivellement Excel→PDF |
| `test_zones.py` | Test de zones |

### BOULOT - Scripts loose (python/projets/)
| Fichier | Description |
|---------|-------------|
| `diagnostic_graphiques.py` | Diagnostic de graphiques |
| `generateur_donnees_temporelles.py` | Générateur de données temporelles |
| `generateur_graphiques_excel.py` | Générateur graphiques Excel |
| `optimiseur_graphiques_20_cibles.py` | Optimiseur graphiques 20 cibles |

### PERSO - Musique Korg PA4X
| Projet | Langage | Description |
|--------|---------|-------------|
| `PA4x-setmerger` | Python | Fusion de fichiers SET |
| `PA4x-classement` | Python | Classement/détection doublons styles |
| `PA4x-midi2styles` | Python | Analyse de fichiers STY |
| `PA4x-extrait_archives` | Python | **(vide)** |

### PERSO - MIDI / Musique
| Projet | Langage | Description |
|--------|---------|-------------|
| `midi-tempofollower` | Python | Suivi tempo MIDI en live |
| `midistyle_toolkit` | Python | Toolkit de styles MIDI |

### UTILITAIRES (ni boulot ni perso spécifiquement)
| Projet | Langage | Description |
|--------|---------|-------------|
| `detectGrosFichiers` | Python/PS1 | Détection gros fichiers |
| `zipRepertoire` | Python | Zip de sous-répertoires |
| `prog_classement` | Python | Classement automatique de fichiers |

---

## Structure proposée

```
dev-workspace/
│
├── 01-PROJECTS/
│   │
│   ├── work/                                    # ══ PROJETS PROFESSIONNELS ══
│   │   │
│   │   ├── topo-axes/                           # Calcul d'axes routiers & topographie
│   │   │   ├── CalculateurAxes/                 ★ projet principal
│   │   │   ├── axe_routier/
│   │   │   ├── kit_axe_routier/
│   │   │   ├── topoAxis/
│   │   │   └── topoStation/
│   │   │
│   │   ├── topo-projections/                    # Projections géométriques 2D/3D
│   │   │   ├── proj_ligne_2D/
│   │   │   ├── proj_ligne_3D/
│   │   │   ├── projectionPline3D/
│   │   │   ├── comparaisonPolygo/
│   │   │   └── reception_ligne_3D/
│   │   │
│   │   ├── auscultation/                        # Monitoring & suivi de déformations
│   │   │   ├── auscultationCarrefour/           ★ projet principal
│   │   │   ├── TraitementCarnet/
│   │   │   ├── recupDernieresAuscultations/
│   │   │   ├── DeplaceAnciennesAuscultations/
│   │   │   ├── extractionCibles/
│   │   │   └── auscult_carrefour_vba/           (ex vba/auscult carrefour)
│   │   │
│   │   ├── tunnel/                              # Projets spécifiques tunnel
│   │   │   ├── rapportMensuel/
│   │   │   ├── rapportMensuelV2/
│   │   │   ├── developpeeTunnel/
│   │   │   ├── concat_csv_beton/
│   │   │   └── FREJUS/
│   │   │
│   │   ├── extraction-donnees/                  # Extraction & traitement de données
│   │   │   ├── extractPM_PDF/
│   │   │   ├── Fiche_implantation/
│   │   │   ├── csv_tools/
│   │   │   ├── copie_jobs/
│   │   │   ├── remplacerChainesGeobases/
│   │   │   └── scripts_graphiques/              (les .py loose de projets/)
│   │   │       ├── diagnostic_graphiques.py
│   │   │       ├── generateur_donnees_temporelles.py
│   │   │       ├── generateur_graphiques_excel.py
│   │   │       └── optimiseur_graphiques_20_cibles.py
│   │   │
│   │   ├── autocad/                             # Scripts AutoCAD / AutoLISP
│   │   │   ├── calage_coupes/
│   │   │   ├── ConstruitFaces/
│   │   │   ├── eclaircir_cotes/
│   │   │   ├── INClabelTextes/
│   │   │   ├── placePresentations/
│   │   │   ├── place_tcpoint/
│   │   │   ├── vecteursDep/
│   │   │   └── a_classer/
│   │   │
│   │   ├── geodesie-externe/                    # Outils géodésiques externes/référence
│   │   │   ├── jag3d/                           (Java)
│   │   │   ├── StaMPS/                          (C/Matlab)
│   │   │   └── ImporterTCPOINT/                 (.NET)
│   │   │
│   │   └── amberg-tools/                        # Outils Amberg (ex fichiers/ en vrac)
│   │       ├── AmbergExtraitDonnéesMetrés.py
│   │       ├── AmbergLogExtractor.py
│   │       └── données_exemple/
│   │
│   ├── personal/                                # ══ PROJETS PERSONNELS ══
│   │   │
│   │   ├── korg-pa4x/                           # Tout ce qui touche au Korg PA4X
│   │   │   ├── PA4x-setmerger/
│   │   │   ├── PA4x-classement/
│   │   │   ├── PA4x-midi2styles/
│   │   │   └── splitFoldersForInstrument.ps1    (ex powershell/)
│   │   │
│   │   └── midi-tools/                          # Outils MIDI génériques
│   │       ├── midi-tempofollower/
│   │       └── midistyle_toolkit/
│   │
│   └── README.md                                # Index des projets avec descriptions
│
├── 02-TOOLS/                                    # ══ OUTILS & CONFIGURATION ══
│   ├── scripts/
│   │   ├── backup-dev.ps1
│   │   └── install-on-new-machine.ps1
│   ├── configs/
│   ├── docs/
│   ├── autocad-fonctions/                       (renommé de "acad fonctions")
│   ├── excel-calculateurs/                      (renommé de "excel")
│   └── vba-macros/                              (renommé de "VBA")
│
├── 03-SCRIPTS/                                  # ══ SCRIPTS UTILITAIRES (PowerShell) ══
│   ├── gestion-disque/                          # Espace disque, compression, nettoyage
│   │   ├── analyzeDiskSpace.ps1
│   │   ├── cleanBeforeCopy.ps1
│   │   ├── cleanDiskSpace.ps1
│   │   ├── Compress-Folders.ps1
│   │   ├── Compress-Original-Fixed.ps1
│   │   ├── deleteEmptyFiles.ps1
│   │   └── quickDiskAnalysis.ps1
│   ├── gestion-fichiers/                        # Recherche, renommage, doublons
│   │   ├── findDuplicateFiles.ps1
│   │   ├── findDuplicateFiles-Parallel.ps1
│   │   ├── findDuplicates-DupeGuruStyle.ps1
│   │   ├── findDuplicates-LowMemory.ps1
│   │   ├── ListFilesModifiedAtDate.ps1
│   │   ├── renameFiles-ChangeCode.ps1
│   │   ├── renommerFichiers.ps1
│   │   ├── trimEspaces.ps1
│   │   └── trouverFichiersModifies.ps1
│   ├── gestion-repertoires/                     # Création/organisation
│   │   ├── creerRepertoiresLocaux.ps1
│   │   └── creerSousRepertoires.ps1
│   ├── utilitaires-python/                      # Python utilitaires non-projet
│   │   ├── detectGrosFichiers/
│   │   ├── zipRepertoire/
│   │   ├── prog_classement/
│   │   └── scripts_autocad/                     (les .py loose de fichiers/)
│   │       ├── convert_dxf_tms.py
│   │       ├── CorrectionAtmo.py
│   │       ├── creerCalques.py
│   │       ├── impression_niv_excel_vers_pdf.py
│   │       ├── replaceSpaces.py
│   │       └── replace_from_config.py
│   └── system/
│       └── getServices.ps1
│
├── 04-EXTERNAL/                                 # ══ CODE EXTERNE (inchangé) ══
│   ├── documentation/
│   ├── github-devs/
│   └── sources/
│
├── 05-ARCHIVE/                                  # ══ ARCHIVES ══
│   └── (déplacer ici les projets abandonnés comme PA4x-extrait_archives)
│
├── .gitignore
└── README.md
```

---

## Actions concrètes à réaliser

### Étape 1 — Créer la nouvelle arborescence (sans risque)

```powershell
# Créer les nouveaux dossiers
$dirs = @(
    "01-PROJECTS/work/topo-axes",
    "01-PROJECTS/work/topo-projections",
    "01-PROJECTS/work/auscultation",
    "01-PROJECTS/work/tunnel",
    "01-PROJECTS/work/extraction-donnees",
    "01-PROJECTS/work/extraction-donnees/scripts_graphiques",
    "01-PROJECTS/work/autocad",
    "01-PROJECTS/work/geodesie-externe",
    "01-PROJECTS/work/amberg-tools",
    "01-PROJECTS/personal/korg-pa4x",
    "01-PROJECTS/personal/midi-tools",
    "03-SCRIPTS/gestion-disque",
    "03-SCRIPTS/gestion-fichiers",
    "03-SCRIPTS/gestion-repertoires",
    "03-SCRIPTS/utilitaires-python",
    "03-SCRIPTS/system"
)
foreach ($d in $dirs) {
    New-Item -ItemType Directory -Path $d -Force
}
```

### Étape 2 — Déplacer les projets Python BOULOT

```powershell
# Topo-Axes
Move-Item "01-PROJECTS/python/projets/CalculateurAxes" "01-PROJECTS/work/topo-axes/"
Move-Item "01-PROJECTS/python/projets/axe_routier" "01-PROJECTS/work/topo-axes/"
Move-Item "01-PROJECTS/python/projets/kit_axe_routier" "01-PROJECTS/work/topo-axes/"
Move-Item "01-PROJECTS/python/projets/topoAxis" "01-PROJECTS/work/topo-axes/"
Move-Item "01-PROJECTS/python/projets/topoStation" "01-PROJECTS/work/topo-axes/"

# Topo-Projections
Move-Item "01-PROJECTS/python/projets/proj_ligne_2D" "01-PROJECTS/work/topo-projections/"
Move-Item "01-PROJECTS/python/projets/proj_ligne_3D" "01-PROJECTS/work/topo-projections/"
Move-Item "01-PROJECTS/python/projets/projectionPline3D" "01-PROJECTS/work/topo-projections/"
Move-Item "01-PROJECTS/python/projets/comparaisonPolygo" "01-PROJECTS/work/topo-projections/"
Move-Item "01-PROJECTS/python/projets/reception ligne 3D" "01-PROJECTS/work/topo-projections/reception_ligne_3D"

# Auscultation
Move-Item "01-PROJECTS/python/projets/auscultationCarrefour" "01-PROJECTS/work/auscultation/"
Move-Item "01-PROJECTS/python/projets/TraitementCarnet" "01-PROJECTS/work/auscultation/"
Move-Item "01-PROJECTS/python/projets/recupDernieresAuscultations" "01-PROJECTS/work/auscultation/"
Move-Item "01-PROJECTS/python/projets/DeplaceAnciennesAuscultations" "01-PROJECTS/work/auscultation/"
Move-Item "01-PROJECTS/python/projets/extractionCibles" "01-PROJECTS/work/auscultation/"
Move-Item "01-PROJECTS/vba/auscult carrefour" "01-PROJECTS/work/auscultation/auscult_carrefour_vba"

# Tunnel
Move-Item "01-PROJECTS/python/projets/rapportMensuel" "01-PROJECTS/work/tunnel/"
Move-Item "01-PROJECTS/python/projets/rapportMensuelV2" "01-PROJECTS/work/tunnel/"
Move-Item "01-PROJECTS/python/projets/developpeeTunnel" "01-PROJECTS/work/tunnel/"
Move-Item "01-PROJECTS/python/projets/concat_csv_beton" "01-PROJECTS/work/tunnel/"
Move-Item "01-PROJECTS/python/projets/FREJUS" "01-PROJECTS/work/tunnel/"

# Extraction de données
Move-Item "01-PROJECTS/python/projets/extractPM_PDF" "01-PROJECTS/work/extraction-donnees/"
Move-Item "01-PROJECTS/python/projets/Fiche_implantation" "01-PROJECTS/work/extraction-donnees/"
Move-Item "01-PROJECTS/python/projets/csv_tools" "01-PROJECTS/work/extraction-donnees/"
Move-Item "01-PROJECTS/python/projets/copie_jobs" "01-PROJECTS/work/extraction-donnees/"
Move-Item "01-PROJECTS/python/projets/remplacerChainesGeobases" "01-PROJECTS/work/extraction-donnees/"

# Scripts graphiques isolés → extraction-donnees/scripts_graphiques/
Move-Item "01-PROJECTS/python/projets/diagnostic_graphiques.py" "01-PROJECTS/work/extraction-donnees/scripts_graphiques/"
Move-Item "01-PROJECTS/python/projets/generateur_donnees_temporelles.py" "01-PROJECTS/work/extraction-donnees/scripts_graphiques/"
Move-Item "01-PROJECTS/python/projets/generateur_graphiques_excel.py" "01-PROJECTS/work/extraction-donnees/scripts_graphiques/"
Move-Item "01-PROJECTS/python/projets/optimiseur_graphiques_20_cibles.py" "01-PROJECTS/work/extraction-donnees/scripts_graphiques/"
```

### Étape 3 — Déplacer les projets AutoCAD et géodésie

```powershell
# AutoCAD (AutoLISP → work/autocad/)
Move-Item "01-PROJECTS/AutoLISP/calage coupes" "01-PROJECTS/work/autocad/calage_coupes"
Move-Item "01-PROJECTS/AutoLISP/ConstruitFaces" "01-PROJECTS/work/autocad/"
Move-Item "01-PROJECTS/AutoLISP/eclaircir cotes" "01-PROJECTS/work/autocad/eclaircir_cotes"
Move-Item "01-PROJECTS/AutoLISP/INClabelTextes" "01-PROJECTS/work/autocad/"
Move-Item "01-PROJECTS/AutoLISP/placePresentations" "01-PROJECTS/work/autocad/"
Move-Item "01-PROJECTS/AutoLISP/place_tcpoint" "01-PROJECTS/work/autocad/"
Move-Item "01-PROJECTS/AutoLISP/vecteursDep" "01-PROJECTS/work/autocad/"
Move-Item "01-PROJECTS/AutoLISP/a_classer" "01-PROJECTS/work/autocad/"

# Géodésie externe
Move-Item "01-PROJECTS/java/jag3d-20251201" "01-PROJECTS/work/geodesie-externe/jag3d"
Move-Item "01-PROJECTS/cpp/StaMPS-4.1-beta" "01-PROJECTS/work/geodesie-externe/StaMPS"
Move-Item "01-PROJECTS/NB_NET/repos/ImporterTCPOINT" "01-PROJECTS/work/geodesie-externe/"

# Amberg tools (scripts isolés)
Move-Item "01-PROJECTS/python/fichiers/AmbergExtraitDonnéesMetrés.py" "01-PROJECTS/work/amberg-tools/"
Move-Item "01-PROJECTS/python/fichiers/AmbergLogExtractor.py" "01-PROJECTS/work/amberg-tools/"
```

### Étape 4 — Déplacer les projets PERSO

```powershell
# Korg PA4X
Move-Item "01-PROJECTS/python/projets/PA4x-setmerger" "01-PROJECTS/personal/korg-pa4x/"
Move-Item "01-PROJECTS/python/projets/PA4x-classement" "01-PROJECTS/personal/korg-pa4x/"
Move-Item "01-PROJECTS/python/projets/PA4x-midi2styles" "01-PROJECTS/personal/korg-pa4x/"

# MIDI tools
Move-Item "01-PROJECTS/python/projets/midi-tempofollower" "01-PROJECTS/personal/midi-tools/"
Move-Item "01-PROJECTS/python/projets/midistyle_toolkit" "01-PROJECTS/personal/midi-tools/"
```

### Étape 5 — Réorganiser les scripts PowerShell

```powershell
# Gestion disque
$diskScripts = @("analyzeDiskSpace","cleanBeforeCopy","cleanDiskSpace",
    "Compress-Folders","Compress-Original-Fixed","deleteEmptyFiles","quickDiskAnalysis")
foreach ($s in $diskScripts) {
    Move-Item "01-PROJECTS/powershell/$s.ps1" "03-SCRIPTS/gestion-disque/"
}

# Gestion fichiers
$fileScripts = @("findDuplicateFiles","findDuplicateFiles-Parallel",
    "findDuplicates-DupeGuruStyle","findDuplicates-LowMemory",
    "ListFilesModifiedAtDate","renameFiles-ChangeCode","renommerFichiers",
    "trimEspaces","trouverFichiersModifies")
foreach ($s in $fileScripts) {
    Move-Item "01-PROJECTS/powershell/$s.ps1" "03-SCRIPTS/gestion-fichiers/"
}

# Gestion répertoires
Move-Item "01-PROJECTS/powershell/creerRepertoiresLocaux.ps1" "03-SCRIPTS/gestion-repertoires/"
Move-Item "01-PROJECTS/powershell/creerSousRepertoires.ps1" "03-SCRIPTS/gestion-repertoires/"

# Instrument (perso)
Move-Item "01-PROJECTS/powershell/splitFoldersForInstrument.ps1" "01-PROJECTS/personal/korg-pa4x/"

# System
Move-Item "01-PROJECTS/powershell/getServices.ps1" "03-SCRIPTS/system/"
```

### Étape 6 — Utilitaires Python

```powershell
Move-Item "01-PROJECTS/python/projets/detectGrosFichiers" "03-SCRIPTS/utilitaires-python/"
Move-Item "01-PROJECTS/python/projets/zipRepertoire" "03-SCRIPTS/utilitaires-python/"
Move-Item "01-PROJECTS/python/projets/prog_classement" "03-SCRIPTS/utilitaires-python/"
```

### Étape 7 — Archiver les dossiers vides / obsolètes

```powershell
# Dossier vide → archive
Move-Item "01-PROJECTS/python/projets/PA4x-extrait_archives" "05-ARCHIVE/"

# Supprimer l'env virtuel à la racine python (recréer si besoin par projet)
Remove-Item "01-PROJECTS/python/Lib" -Recurse -Force
Remove-Item "01-PROJECTS/python/Scripts" -Recurse -Force
Remove-Item "01-PROJECTS/python/pyvenv.cfg" -Force

# Nettoyer les conteneurs vides restants
# (vérifier qu'ils sont bien vides avant de supprimer)
# Remove-Item "01-PROJECTS/python/projets" -Recurse  # si vide
# Remove-Item "01-PROJECTS/python/fichiers" -Recurse  # si vide
# Remove-Item "01-PROJECTS/AutoLISP" -Recurse         # si vide
# Remove-Item "01-PROJECTS/java" -Recurse              # si vide
# Remove-Item "01-PROJECTS/cpp" -Recurse               # si vide
# Remove-Item "01-PROJECTS/NB_NET" -Recurse            # si vide
# Remove-Item "01-PROJECTS/vba" -Recurse               # si vide
# Remove-Item "01-PROJECTS/powershell" -Recurse        # si vide
# Remove-Item "lisp" -Recurse                          # doublon de 04-EXTERNAL
```

### Étape 8 — Renommer dans 02-TOOLS

```powershell
Rename-Item "02-TOOLS/acad fonctions" "autocad-fonctions"
Rename-Item "02-TOOLS/excel" "excel-calculateurs"
Rename-Item "02-TOOLS/VBA" "vba-macros"
```

---

## Résumé visuel : Avant / Après

### AVANT
```
01-PROJECTS/python/projets/    → 38 dossiers à plat, boulot+perso mélangés
01-PROJECTS/powershell/        → 25 scripts à plat
01-PROJECTS/AutoLISP/          → 8 dossiers
01-PROJECTS/java/              → 1 dossier
01-PROJECTS/cpp/               → 1 dossier
01-PROJECTS/NB_NET/            → 1 dossier
01-PROJECTS/vba/               → 1 dossier
```

### APRÈS
```
01-PROJECTS/work/
    ├── topo-axes/             → 5 projets (calcul d'axes)
    ├── topo-projections/      → 5 projets (projections géom.)
    ├── auscultation/          → 6 projets (monitoring)
    ├── tunnel/                → 5 projets (tunnel)
    ├── extraction-donnees/    → 6 projets + scripts graphiques
    ├── autocad/               → 8 routines AutoLISP
    ├── geodesie-externe/      → 3 outils externes
    └── amberg-tools/          → 2 scripts Amberg

01-PROJECTS/personal/
    ├── korg-pa4x/             → 4 projets Korg + 1 script PS
    └── midi-tools/            → 2 projets MIDI

03-SCRIPTS/
    ├── gestion-disque/        → 7 scripts PowerShell
    ├── gestion-fichiers/      → 9 scripts PowerShell
    ├── gestion-repertoires/   → 2 scripts PowerShell
    ├── utilitaires-python/    → 3 outils Python
    └── system/                → 1 script
```

---

## Points d'attention

1. **Git** : Si les projets individuels ont leur propre `.git`, les `Move-Item` préservent l'historique. Si tout est dans un seul repo (le monorepo `dev-workspace`), utiliser `git mv` au lieu de `Move-Item` pour que Git suive les renommages.

2. **Environnements virtuels** : Chaque projet Python devrait avoir son propre `.venv/` local (ajouté dans `.gitignore`). L'env virtuel global `01-PROJECTS/python/{Lib,Scripts,pyvenv.cfg}` est à supprimer.

3. **Le dossier `lisp/`** à la racine semble être un doublon de `04-EXTERNAL/` — à vérifier et consolider.

4. **Les READMEs** des anciens dossiers (`01-PROJECTS/README.md`, etc.) devront être mis à jour pour refléter la nouvelle structure.

5. **Les fichiers `prog_classement/`** existent en doublon dans `python/fichiers/` et `python/projets/` — à fusionner.
