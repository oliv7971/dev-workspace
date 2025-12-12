# Support du format GSI Leica

## Qu'est-ce que le format GSI ?

Le **GSI** (Geodetic System Interface) est le format standard de Leica Geosystems pour les données de stations totales. Il existe en deux versions :
- **GSI-8** : 8 caractères par valeur
- **GSI-16** : 16 caractères par valeur

## Structure d'un champ GSI

Chaque champ a la structure suivante :
```
WI(2) + INFO(4) + SIGN(1) + VALUE(variable)
```

- **WI** (Word Index) : 2 chiffres identifiant le type de données
- **INFO** : 4 caractères (1er = unité, autres = informations supplémentaires)
- **SIGN** : `+` ou `-`
- **VALUE** : Valeur numérique (points `.` = données non disponibles)

## Codes Word Index principaux

| WI | Description | Unité typique |
|----|-------------|---------------|
| 11 | Numéro de point | - |
| 21 | Direction Hz (horizontal) | gon, deg, mil |
| 22 | Angle vertical V | gon, deg, mil |
| 31 | Distance inclinée | m, ft |
| 32 | Distance horizontale | m, ft |
| 58 | Hauteur instrument | m, mm |
| 59 | Hauteur prisme | m, mm |
| 81 | Coordonnée X (E) | m, mm |
| 82 | Coordonnée Y (N) | m, mm |
| 83 | Coordonnée Z (H) | m, mm |
| 87 | Hauteur prisme (alternative) | m, mm |

## Codes d'unité (1er caractère INFO)

### Pour les angles (WI 21, 22)
- `3` = gon (grades, 400 grad)
- `4` = degrés (360°)
- `5` = mil (6400 mil)

### Pour les distances (WI 31, 32, 33)
- `1` = mètres
- `2` = pieds

### Pour les coordonnées (WI 81, 82, 83)
- `0` = mètres

## Exemples

### Exemple GSI-8 (observations)
```
110001+00001001 21.324+00012345 22.324+00098765 31..00+00012345 87..10+00001500
```

Décodage :
- `110001+00001001` → Point 1001
- `21.324+00012345` → Hz = 123.45 gon
- `22.324+00098765` → V = 987.65 gon
- `31..00+00012345` → Distance = 12.345 m
- `87..10+00001500` → Hauteur prisme = 1.500 m

### Exemple GSI-8 (coordonnées)
```
81..00+01000000 82..00+02000000 83..00+00250000 11....+00001001
```

Décodage :
- `81..00+01000000` → X = 1000.000 m
- `82..00+02000000` → Y = 2000.000 m
- `83..00+00250000` → Z = 250.000 m
- `11....+00001001` → Point 1001

## Utilisation dans le calculateur

1. **Importer un fichier GSI complet**
   - Onglet "Points Connus" → Bouton "📋 Importer GSI"
   - Importe les points avec coordonnées ET les observations

2. **Importer uniquement les observations**
   - Onglet "Observations" → Bouton "📋 Importer GSI"
   - Importe seulement les mesures (Hz, V, distances)

## Conversion automatique

Le parser effectue automatiquement :
- ✅ Conversion de V (angle vertical) en zénith : `Z = 100 - V` (en gon)
- ✅ Conversion des unités (mm → m, gon → gon)
- ✅ Extraction de la hauteur instrument
- ✅ Association des observations aux points

## Fichier exemple

Un fichier `exemple.gsi` est fourni avec 3 points visés depuis une station.

## Notes

- Les angles V sont généralement des angles verticaux (0 = horizon)
- Ils sont automatiquement convertis en zénith pour le calcul
- Si un fichier contient à la fois des observations et des coordonnées, tout est importé
