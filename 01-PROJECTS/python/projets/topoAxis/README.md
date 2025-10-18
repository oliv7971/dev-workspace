
# topo_axis — Remplacement Python de votre calculateur Excel (axe en plan + profil en long)

**Objectif** : fournir un moteur Python propre et testable qui reprend la logique de votre classeur Excel :
- **Plan** : DROITE / ARC (rayon signé) / CLOTHOÏDE (k(s)=± s/A²) ;
- **Profil** : PENTE constante / **Raccord PARABOLIQUE** ;
- **Lookup PK→élément**, calcul des **abscisses locales**, chaînes **continues** entre éléments ;
- **CLI** pour générer rapidement un profil XYZ à pas régulier ;
- **Comparateur** pour confronter les résultats au classeur Excel existant.

## Installation / utilisation rapide

1. Placez ce dossier `topo_axis/` quelque part sur votre machine (ou ajoutez-le au `PYTHONPATH`).
2. Préparez votre fichier Excel **converti en .xlsx**.
3. (Optionnel) Dans Python :

```python
from topo_axis.parser_excel import build_from_workbook
from topo_axis.engine import AxisModel

plan, vert, defs = build_from_workbook("CALCULATEUR AXE GGS exe.xlsx")
model = AxisModel(plan=plan, vertical=vert)

# Exemple : coordonnées tous les 5 m
s_vals = [i*5 for i in range(int(model.L//5)+1)]
xyz = [model.xyz(s) for s in s_vals]
```

4. En **ligne de commande** :

```bash
python -m topo_axis.cli CALCULATEUR\ AXE\ GGS\ exe.xlsx --from 0 --to 1000 --step 5 --out profil_xyz.csv
```

## Hypothèses et conventions

- **Azimut** en degrés (si présent sur le 1er élément plan), sinon 0 rad.
- **Arc** : rayon **signé** `R` (R>0 = virage à gauche ; R<0 = virage à droite).
- **Clothoïde** : paramètre `A` (m) et `k_sign` = +1 (gauche) / -1 (droite). Intégration **Simpson** interne (paramétrable).
- **Pentes** en **%** dans le parsing Excel ; en interne c'est un **ratio**.
- Le **profil** utilise la parabole standard : `Z = Z0 + g0*s + (g1-g0)*s²/(2L)`.

> Si votre classeur a des champs/entêtes différents, ajustez les heuristiques dans `parser_excel.py` ou préparez un CSV de définitions.

## Comparaison avec le classeur Excel

Vous pouvez évaluer les écarts **X/Y/Z** vs vos feuilles `Calcul XY` et `Calcul Z` :

```python
from topo_axis.compare_with_excel import compare_xyZ_with_workbook
df = compare_xyZ_with_workbook("CALCULATEUR AXE GGS exe.xlsx")
df.to_csv("ecarts_vs_excel.csv", index=False)
```

## Tests

De petits tests existent dans `tests/test_geometry.py` :

```bash
python -m pytest -q
```

## Prochaines améliorations possibles

- Détection plus robuste des colonnes (`parser_excel.py`) selon vos entêtes réels.
- Ajout du **rabattement** / changement de repère si besoin (repères chantier vs absolus).
- Support des **unités** (gon vs degrés) selon votre convention Covadis.
- Optimisation/validation de la **clothoïde** (Fresnel analytique vs Simpson).
