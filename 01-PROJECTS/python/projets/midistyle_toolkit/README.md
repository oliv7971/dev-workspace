# midistyle_toolkit

Outils (Python) pour :
1) **Détecter** les fichiers MIDI "à risque" et les "bons candidats" pour la conversion en style PA4X.
2) **Préparer** automatiquement un MIDI pour le **Style Creator Bot** du PA4X (nettoyage, normalisation GM, canaux, quantification douce, limites de CC/PB, etc.).
3) **Baliser** un MIDI avec des marqueurs de sections (Intro/Var/Fill/Break/Ending) et nommer les pistes BASS/DRUM/PERC/ACC1..ACC5 pour faciliter l'import Korg.
4) **Pipeline Yamaha→Korg (via MIDI)** : extraire les patterns d’un style Yamaha (SFF1/SFF2) *via export en MIDI*, puis mapper vers les éléments Korg.

> Remarque : le parsing natif des `.sty` Yamaha est complexe (CASM/OTS, NTR/NTT). Le chemin robuste et universel reste de **rendre** chaque pattern en MIDI autour de l’accord **C majeur** (et éventuellement **C mineur**) puis de mapper vers Korg.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install mido python-rtmidi pyyaml
```

## Usage rapide

### 1) Audit d’un dossier de MIDIs
```bash
python midistyle_toolkit.py audit /chemin/vers/midis --out report.csv
```

### 2) Préparation d’un MIDI unique (nettoyage + remap + quantif + marqueurs)
```bash
python midistyle_toolkit.py prepare input.mid --out prepared.mid --config config.yaml
```

### 3) Yamaha → Korg (via MIDI export)
- Exportez les **patterns** Yamaha (Intro A/B, Main A–D, Fills, Ending…) en **SMF** (accords joués en **C**).
- Placez les fichiers exportés dans des sous-dossiers nommés `Intro1`, `Var1`… (voir `config.yaml`).
```bash
python midistyle_toolkit.py build-korg-pack ./yamaha_exports --out korg_ready.mid --config config.yaml
```

## Heuristiques (détection bon/mauvais candidats)

**Bons candidats** (score élevé) :
- Tempo **constant** (≤ 1 changement) ; métrique **4/4**, **2/4** ou **6/8**.
- Drum clair sur **Canal 10** (GM), peu de SysEx propriétaires.
- Basse **monophonique** sur 1 canal dédié (notes 36–60), motif répétitif **1–8 mesures**.
- Pistes d’“accompagnement” (pads/guitares/sections) **2–5 canaux** max, accords joués **autour de C**.
- Peu/aucun Program Change/Bank Select en cours de route.
- Peu de flood CC (≤ 200 événements total par piste), Pitch Bend dans une plage raisonnable (±2 à ±4 demi-tons).

**Mauvais candidats** (score faible) :
- > 3 changements de tempo, métriques instables, **pas de batterie**,
- multiples Program Changes, Key Changes, flood CC (modulation/expression), Aftertouch poly en masse,
- Drum éparpillé sur plusieurs canaux, ou mapping exotique non GM,
- polyrythmies/mesures impaires non répétitives, patterns > 16 mesures sans boucles claires,
- notes de basse polyphoniques, slides PB extrêmes (±12), SysEx lourds.

Les règles sont **configurables** dans `config.yaml`.
