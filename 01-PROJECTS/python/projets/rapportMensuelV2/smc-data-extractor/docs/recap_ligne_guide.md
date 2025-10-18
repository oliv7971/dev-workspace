# SMC Data Extractor - Récapitulatifs en ligne

## Nouvelle fonctionnalité : Génération de récapitulatifs en ligne

Cette fonctionnalité génère des récapitulatifs horizontaux pour chaque élément mesuré, avec les convergences et déplacements (périodiques et cumulés) présentés sur une seule ligne par fichier/type.

### Format de sortie

#### Convergences
```
GGS C007 (Convergences - périodique)
  BG:-1.11 | HG:-0.11 | HD:N/A | BD:-1.65 | LH:N/A | LB:-1.07

GGS C007 (Convergences - cumulé)
  BG:-35.04 | HG:-30.44 | HD:-9.72 | BD:-7.96 | LH:-10.64 | LB:-25.16
```

#### Déplacements
```
GGS C007 (Déplacements - périodique)
  DH BD:-0.77 | DH BG:0.30 | DH CH:0.27 | DPM BD:-1.18 | DPM BG:-1.02 | DPM CH:-1.56 | DZ BD:-0.20 | DZ BG:-0.10

GGS C007 (Déplacements - cumulé)
  DH BD:-13.46 | DH BG:11.63 | DH CH:-17.08 | DPM BD:-2.60 | DPM BG:-6.30 | DPM CH:-11.07 | DZ BD:-8.20 | DZ BG:-10.00
```

### Fichiers générés

1. **Récapitulatifs_Ligne_SMC_YYYY_MM.txt** : Fichier texte complet avec tous les récapitulatifs
2. **Convergences_Ligne_SMC_YYYY_MM.csv** : Format CSV avec convergences en ligne
3. **Deplacements_Ligne_SMC_YYYY_MM.csv** : Format CSV avec déplacements en ligne

### Structure CSV

#### Convergences CSV
```csv
galerie,section,type,mode,BG,HG,HD,BD,LH,LB
GGS,C007,Convergences,périodique,-1.11,-0.11,,-1.65,,-1.07
GGS,C007,Convergences,cumulé,-35.04,-30.44,-9.72,-7.96,-10.64,-25.16
```

#### Déplacements CSV
```csv
galerie,section,type,mode,DH BD,DH BG,DH CH,DPM BD,DPM BG,DPM CH,DZ BD,DZ BG
GGS,C007,Déplacements,périodique,-0.77,0.30,0.27,-1.18,-1.02,-1.56,-0.20,-0.10
GGS,C007,Déplacements,cumulé,-13.46,11.63,-17.08,-2.60,-6.30,-11.07,-8.20,-10.00
```

## Utilisation

### Via l'interface graphique
1. Lancez `smc_gui.py`
2. Cochez l'option "Générer récapitulatifs en ligne"
3. Lancez l'extraction

### Via le code Python
```python
from ligne_summary_generator import generate_ligne_summaries

# Générer uniquement les récapitulatifs
generate_ligne_summaries(
    csv_folder="path/to/csv", 
    output_folder="path/to/output", 
    month="2025-08"
)
```

### Via l'extraction complète
```python
from smc_evolutions import run_extraction

options = {
    'generate_csv': True,
    'generate_pdf': False,
    'generate_ligne_summaries': True  # Nouvelle option
}

run_extraction(root_folder, month, output_folder, options)
```

## Intégration

La fonctionnalité est automatiquement intégrée dans :
- ✅ `smc_evolutions.py` (module principal)
- ✅ `smc_gui.py` (interface graphique)
- ✅ Processus d'extraction complet

## Configuration

L'option `generate_ligne_summaries` est activée par défaut. Pour la désactiver :

```python
options = {'generate_ligne_summaries': False}
```

## Avantages

1. **Format compact** : Toutes les métriques d'un élément sur une ligne
2. **Facilité de lecture** : Format horizontal plus lisible pour les rapports
3. **Compatibilité Excel** : CSV directement importable dans Excel
4. **Complémentaire** : S'ajoute aux fonctionnalités existantes sans les remplacer

## Métriques supportées

### Convergences
- **BG** : Bas Gauche
- **HG** : Haut Gauche  
- **HD** : Haut Droit
- **BD** : Bas Droit
- **LH** : ?
- **LB** : ?

### Déplacements
- **DPM** : Déplacement Permanent (diverses positions)
- **DH** : Déplacement Horizontal (diverses positions)
- **DZ** : Déplacement Vertical (diverses positions)

## Exemple complet

Pour un fichier `GGS_SMC_C007.xlsm`, la sortie sera :

```
GGS C007 (Convergences - périodique)
  BG:-1.11 | HG:-0.11 | HD:N/A | BD:-1.65 | LH:N/A | LB:-1.07
GGS C007 (Convergences - cumulé)  
  BG:-35.04 | HG:-30.44 | HD:-9.72 | BD:-7.96 | LH:-10.64 | LB:-25.16

GGS C007 (Déplacements - périodique)
  DH BD:-0.77 | DH BG:0.30 | DPM BD:-1.18 | DPM BG:-1.02 | DZ BD:-0.20 | DZ BG:-0.10
GGS C007 (Déplacements - cumulé)
  DH BD:-13.46 | DH BG:11.63 | DPM BD:-2.60 | DPM BG:-6.30 | DZ BD:-8.20 | DZ BG:-10.00
```

Cette présentation permet une lecture rapide des évolutions par élément et facilite l'intégration dans des rapports de synthèse.
