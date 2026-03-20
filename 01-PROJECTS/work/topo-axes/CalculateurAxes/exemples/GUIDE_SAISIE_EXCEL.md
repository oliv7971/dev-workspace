
# Guide de Saisie d'Axes via Excel

## 📋 Formats Supportés

### 1. Saisie par Éléments Géométriques

**Fichier**: `modele_saisie_elements.xlsx`

#### Feuille "Elements"
| Colonne | Description | Exemples |
|---------|-------------|----------|
| Element | Numéro d'ordre | 1, 2, 3, ... |
| Type | Type d'élément | AD, C, CL |
| Param1 | Premier paramètre | Gisement (AD), Rayon (C), R_début (CL) |
| Param2 | Second paramètre | Longueur (AD), Déviation (C), R_fin (CL) |
| Param3 | Troisième paramètre | - (AD), - (C), Longueur (CL) |

**Types d'éléments:**
- **AD** (Alignement Droit): Param1=Gisement(g), Param2=Longueur(m)
- **C** (Arc Circulaire): Param1=Rayon(m), Param2=Déviation(g) ou Longueur(m)
- **CL** (Clothoïde): Param1=R_début(m), Param2=R_fin(m), Param3=Longueur(m)

#### Feuille "Profil"
| Colonne | Description | Unité |
|---------|-------------|-------|
| PM | Point métrique | m |
| Z | Altitude | m |
| Pente | Pente locale | % |

#### Feuille "Parametres"
| Paramètre | Description |
|-----------|-------------|
| PM_Debut | PM de début d'axe |
| X_Debut | Coordonnée X de début |
| Y_Debut | Coordonnée Y de début |
| Z_Debut | Altitude de début |
| Nom_Axe | Nom de l'axe |

### 2. Saisie par Points à Projeter

**Fichier**: `modele_points_a_traiter.xlsx`

| Colonne | Description | Obligatoire |
|---------|-------------|-------------|
| ID | Identifiant unique | Oui |
| X | Coordonnée X | Oui |
| Y | Coordonnée Y | Oui |
| Z | Altitude | Non |
| Type | Type de point | Non |
| Description | Description | Non |

### 3. Fichier de Résultats

**Fichier**: `resultats_calculs.xlsx`

| Colonne | Description |
|---------|-------------|
| ID | Identifiant du point |
| X, Y, Z | Coordonnées originales |
| PM | Point métrique sur l'axe |
| Deport_H | Déport horizontal (+ = droite) |
| Deport_V | Déport vertical |
| Distance_3D | Distance 3D au point projeté |

## 🔄 Workflow de Travail

1. **Préparation**: Utiliser les modèles Excel fournis
2. **Saisie géométrie**: Remplir la définition d'axe
3. **Import**: Charger l'axe dans le calculateur
4. **Points**: Ajouter les points à traiter
5. **Calculs**: Lancer les projections
6. **Export**: Récupérer les résultats Excel

## ⚠️ Conventions Importantes

- **Gisements**: En grades (0-400g), Nord = 0g, sens horaire
- **Coordonnées**: Système Lambert ou local
- **Déports**: Positifs à droite de l'axe
- **Rayons**: Positifs = virage droite, négatifs = virage gauche
- **Clothoïdes**: Rayon infini = alignement (laisser vide)

## 🎯 Exemples Pratiques

Les fichiers modèles contiennent des données réalistes pour tester le système.
