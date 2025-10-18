# topo_station_ls.py — Ajustement station libre (Moindres Carrés) avec pondérations

## Objectif
Caler une station (X0, Y0, Z0, omega) à partir de visées vers des points connus, en Moindres Carrés, avec :
- **Pondération par type** d'observation (direction, zénith, distance),
- **Pondération par visée (rayon)** via un facteur kappa ≥ 1,
- Option d'estimation **EDM** : échelle (mu) et constante additive (c),
- Sorties : paramètres + écarts-types, résidus, résidus normalisés, redondances, sigma0.

Angles attendus par défaut en **gon** (configurable), distances en **m**.

## Fichiers d'entrée
### 1) Points connus (`controls.csv`)
Colonnes : `pid,X,Y,Z`

### 2) Observations (`observations.csv`)
Colonnes : `ray_id,pid,obs_type,value,unit,n_series,h_target`

- `obs_type` ∈ {`dir`, `zen`, `dist`}
- `unit` : `gon` | `deg` | `rad` (pour dir/zen) ou `m` (pour dist)
- `n_series` : nb de lectures moyennées (divise la variance)
- `h_target` : hauteur de prisme (m) au point visé

### 3) Pondération par visée (`rays.csv`, optionnel)
Colonnes : `ray_id,kappa` (kappa ≥ 1 ; 1 = visée "normale", 2.5 = visée dégradée, etc.)

### 4) Configuration (`config.json`, optionnel)
Clés possibles (valeurs par défaut entre parenthèses) :
```json
{
  "sigma_dir_mgon": 0.5,
  "sigma_zen_mgon": 1.0,
  "edm_a_mm": 1.5,
  "edm_b_ppm": 2.0,
  "h_instrument": 0.0,
  "estimate_mu": false,
  "estimate_c": false,
  "angles_unit": "gon",
  "max_iter": 10,
  "tol": 1e-10
}
```

## Lancer (CLI)
```bash
python topo_station_ls.py \
  --controls /chemin/controls.csv \
  --observations /chemin/observations.csv \
  --rays /chemin/rays.csv \
  --config /chemin/config.json \
  --out /chemin/sortie/resultats
```

Produits :
- `resultats.params.csv` : paramètres estimés + écarts-types
- `resultats.residuals.csv` : résidus, résidus normalisés, redondances, diag(Qvv)
- `resultats.meta.json` : sigma0, ddl, config utilisée

## Hypothèses & conventions
- Azimut géométrique `alpha = atan2(dX, dY)` (Nord→Est). Direction observée modélisée par `D = alpha + omega`.
- Zénith `z = acos(dZ / rho)` ; dérivées via angle d'élévation pour stabilité.
- Distances : modèle EDM `rho_obs ≈ (1 + mu)*rho + c` (si activés).
- Hauteurs : visée de `Z0 + hI` vers `Z + h_target`.

## À venir / extensions possibles
- Tests statistiques (Baarda/Pope) avec seuils configurables
- Gestion des coordonnées connues "souples" (GLS sur points connus)
- Option robuste (Huber) si nécessaire
- Import/Export DXF/CSV supplémentaires
