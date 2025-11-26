# Projet : Outils de Projection sur Axe 3D

## Vue d'ensemble

Suite d'outils Python pour la projection de nuages de points sur des axes topographiques 3D, avec gestion des transformations directes et inverses.

**Date de création :** 25 novembre 2025  
**Besoin initial :** Traiter rapidement de gros volumes de scans 3D (millions de points) pour des projections sur axe, impossibles à gérer avec Excel ou Amberg.

---

## 🎯 Outils développés

### 1. `projeter_multi_axes.py` - Projection multi-axes automatique ⭐ NOUVEAU

**Fonction :** Projette automatiquement des points sur différents axes selon un identifiant dans le fichier d'entrée.

**Utilisation :**
```bash
python projeter_multi_axes.py points.csv [options]
```

**Options :**
- `--config fichier.csv` : Fichier de configuration des axes (défaut : `axes_config.csv`)
- `--mode vertical|perpendiculaire` : Mode de projection (défaut : `vertical`)
- `--output|-o fichier` : Fichier de sortie (auto-généré si omis)
- `--colonne-axe nom` : Nom de la colonne identifiant (défaut : `axe`)

**Format fichier d'entrée (CSV/Excel) :**
```
PT,X,Y,Z,axe,description
REF-001,823245.5,1091505.2,-123.5,GRE,Point de référence
SCAN-045,823180.0,1091450.0,-122.0,GVA,Point laser
```

**Format fichier de configuration (`axes_config.csv`) :**
```
axe,PM,X,Y,Z
GRE,0.000,823241.141,1091511.231,-123.794
GRE,9.721,823245.250,1091502.421,-123.697
GVA,0.000,823100.000,1091400.000,-120.000
GVA,50.000,823150.000,1091350.000,-119.500
```
*Minimum 2 points par axe requis*

**Exemples :**
```bash
# Utilisation simple avec fichier Excel
python projeter_multi_axes.py points.xlsx

# Avec config personnalisée et mode perpendiculaire
python projeter_multi_axes.py points.csv --config mes_axes.csv --mode perpendiculaire

# Avec nom de sortie personnalisé
python projeter_multi_axes.py points.xlsx -o resultats_projections.xlsx
```

**Sortie :** Fichier original enrichi avec colonnes PM, H, V calculées pour chaque axe

**Avantages :**
- ✅ Traitement batch de multiples axes en une seule commande
- ✅ Plus besoin de projeter séparément chaque axe
- ✅ Idéal pour laboratoires avec nombreux axes de référence
- ✅ Support CSV et Excel en entrée/sortie
- ✅ Statistiques détaillées par axe

---

### 2. `projection_scan_droite3d.py` - XYZ → H,V,PM

**Fonction :** Projette un nuage de points XYZ sur une droite 3D pour obtenir des coordonnées d'axe.

**Utilisation :**
```bash
python projection_scan_droite3d.py scan.asc [sortie.csv] [mode] [--axe axe.txt]
```

**Options :**
- **Mode de projection :**
  - `vertical` (défaut) : Projection verticale classique (PM calculé en plan, V = différence d'altitude)
  - `perpendiculaire` : Projection perpendiculaire 3D (vraie projection orthogonale)

- **Définition de l'axe :**
  - Par défaut : axe BURE GRE codé en dur
  - `--axe fichier.txt` : fichier PM,X,Y,Z (séparateur auto-détecté)

**Exemples :**
```bash
# Avec axe par défaut, mode vertical
python projection_scan_droite3d.py scan.asc

# Avec axe personnalisé
python projection_scan_droite3d.py scan.asc resultat.csv vertical --axe mon_axe.txt

# Mode perpendiculaire
python projection_scan_droite3d.py scan.asc resultat.csv perpendiculaire
```

**Entrée :** Fichier ASCII avec X,Y,Z (séparateurs acceptés : `,` `;` `tab` espaces)  
**Sortie :** CSV avec H,V,PM

**Performances :**
- ✅ 31 millions de points traités (1 GB) en quelques minutes
- ✅ Traitement par blocs de 500k points (gestion mémoire optimale)
- ✅ Calculs vectorisés numpy (ultra rapide)

---

### 3. `projection_inverse_hvpm_vers_xyz.py` - H,V,PM → XYZ

**Fonction :** Transformation inverse, reconstitue les coordonnées XYZ à partir des coordonnées d'axe.

**Utilisation :**
```bash
python projection_inverse_hvpm_vers_xyz.py hvpm.csv [sortie.csv] [mode] [--axe axe.txt]
```

**Mêmes options** que le script direct (mode, axe personnalisé).

**Cas d'usage :**
- Reconstituer un nuage modifié en coordonnées d'axe
- Placer des objets théoriques sur l'axe
- Export vers CAO/BIM

**Entrée :** CSV avec H,V,PM  
**Sortie :** CSV avec X,Y,Z

---

### 4. `tabuler_axe.py` - Génération de points réguliers sur axe

**Fonction :** Génère des points régulièrement espacés le long d'un axe pour contrôle ou implantation.

**Utilisation :**
```bash
python tabuler_axe.py [--axe fichier] [--pas 0.5] [--debut 10] [--fin 50] [--sortie fichier]
```

**Options :**
- `--pas` : Espacement entre points en mètres (défaut: 1.0 m)
- `--debut` : PM de début (défaut: min de l'axe)
- `--fin` : PM de fin (défaut: max de l'axe)
- `--sortie` : Fichier de sortie (défaut: axe_tabule.csv)

**Exemples :**
```bash
# Tous les mètres
python tabuler_axe.py

# Tous les 25 cm entre PM 10 et 50
python tabuler_axe.py --pas 0.25 --debut 10 --fin 50

# Avec axe personnalisé, tous les 50 cm
python tabuler_axe.py --axe mon_axe.txt --pas 0.5 --sortie controle.csv
```

**Sortie :** CSV avec PM,X,Y,Z

**Cas d'usage :**
- Contrôle de géométrie d'axe
- Points d'implantation théoriques
- Génération de profils en long
- Comparaison avec levés terrain

---

## 📁 Format du fichier axe

Les trois scripts acceptent un fichier de définition d'axe au format :

```
# Commentaires optionnels avec #
PM,X,Y,Z
0.000,823241.141,1091511.231,-123.794
9.721,823245.250,1091502.421,-123.697
56.601,823265.062,1091459.933,-123.228
156.601,823307.323,1091369.302,-122.228
```

**Séparateurs acceptés :** `,` `;` `tab` espaces (détection automatique)

**Note :** L'axe est calculé par régression linéaire 3D sur les points fournis, donnant la meilleure droite moyenne.

---

## 🔧 Caractéristiques techniques

### Performance
- **Calculs vectorisés numpy** : traitement en masse, pas de boucles Python
- **Lecture/écriture par chunks** : gestion de fichiers > RAM disponible
- **Progression en temps réel** : affichage du pourcentage traité

### Robustesse
- **Détection auto du séparateur** : `,` `;` `tab` espaces
- **Gestion des lignes invalides** : skip automatique
- **Filtrage des NaN** : élimination des valeurs manquantes
- **Gestion d'erreurs explicite** : messages clairs en cas de problème

### Formats supportés
- **Entrée XYZ** : ASCII, CSV, séparateur quelconque
- **Sortie** : CSV standard avec en-têtes

---

## 📊 Résultats obtenus

**Projet BURE GRE (25/11/2025) :**
- **Mur** : 5,5 millions de points (220 Mo) → traité en quelques secondes
- **Front** : 25,6 millions de points (1024 Mo) → traité en ~2 minutes
- **Total** : 31 millions de points projetés avec succès

**Axe traité :**
- Gisement : 172.2226 grades
- Pente : 1.00 %
- Longueur : ~157 m

---

## 🚀 Évolutions futures

### Géométrie planimetrique complexe

Actuellement : **Droites 3D uniquement** ✅

À développer :
- [ ] **Arcs circulaires** (rayon, début, fin)
- [ ] **Clothoïdes** (paramètre A, transition progressive)
  - Code existant dans le projet : `clothoide_precise.py`, `gestionnaire_clothoides.py`
  - À intégrer et améliorer
- [ ] **Combinaisons** d'éléments (D-C-A-C-D, etc.)

### Géométrie altimétrique complexe

Actuellement : **Pente constante** ✅

À développer :
- [ ] **Raccordements circulaires** (rayon vertical)
- [ ] **Raccordements paraboliques** (standard en génie civil)
- [ ] **Profils en long complexes**

### Architecture orientée objet

**Proposition de structure :**

```python
class Axe:
    def __init__(self):
        self.elements = []
    
    def ajouter_droite(self, pm_debut, pm_fin, gisement, pente):
        pass
    
    def ajouter_arc(self, pm_debut, pm_fin, rayon, sens):
        pass
    
    def ajouter_clothoide(self, pm_debut, pm_fin, A, sens):
        pass
    
    def projeter_point(self, x, y, z, mode='vertical'):
        # Trouve l'élément concerné et projette
        pass
    
    def tabuler(self, pas, pm_debut=None, pm_fin=None):
        pass
```

**Avantages :**
- Gestion unifiée des axes complexes
- Réutilisation du code existant sur clothoïdes
- Projection automatique sur le bon élément géométrique
- Compatibilité avec les outils actuels (fichiers d'axe étendus)

### Fonctionnalités additionnelles

- [ ] **Import/Export DXF** : lecture d'axes depuis fichiers CAO
- [ ] **Profils en travers** : génération automatique de sections
- [ ] **Cubatures** : calculs de volumes entre profils
- [ ] **Visualisation 3D** : affichage de l'axe et des points projetés
- [ ] **Validation géométrique** : vérification des normes (rayon min, etc.)
- [ ] **Gestion des altérations linéaires** : Lambert, terrain, etc.

---

## 📚 Dépendances

**Requis :**
- Python 3.8+
- numpy
- pandas

**Installation :**
```bash
pip install numpy pandas
```

---

## 💡 Notes d'utilisation

### Choix du mode de projection

**Mode VERTICAL** (recommandé pour la plupart des cas) :
- PM calculé sur la projection horizontale
- H = déport horizontal pur (dans le plan XY)
- V = différence d'altitude
- Idéal pour : métrés, profils en long, applications standard

**Mode PERPENDICULAIRE** :
- Vraie projection orthogonale 3D
- H et V dépendent de la pente de l'axe
- Idéal pour : applications géométriques strictes, contrôles 3D

**Différence :** Pour une pente de 1%, l'écart est négligeable (~0.01%). Pour des pentes fortes (>10%), le choix devient important.

### Performance et mémoire

**Fichiers volumineux :**
- Pas de limite théorique (traitement par chunks)
- RAM nécessaire : ~200 Mo pour traiter n'importe quelle taille
- Vitesse : ~10 millions de points/minute (processeur moderne)

**Si traitement trop lent :**
- Réduire le chunk_size dans le code (ligne 198)
- Augmenter si beaucoup de RAM disponible

### Format des coordonnées

**Attention aux virgules/points décimaux** :
- Format français : `823241,141` (virgule décimale)
- Format anglo-saxon : `823241.141` (point décimal)
- Les scripts gèrent les deux automatiquement

---

## 📞 Support et exemples

**Fichiers d'exemple fournis :**
- `exemple_axe.txt` : Format de fichier axe
- `test_scan.asc` : Petit nuage de test (10 points)

**Tests de validation :**
- Projection aller-retour validée
- Cohérence des modes vertical/perpendiculaire vérifiée
- Performance testée sur 31M points réels

---

## 🏗️ Architecture du projet

```
CalculateurAxes/
├── projection_scan_droite3d.py          # XYZ → H,V,PM
├── projection_inverse_hvpm_vers_xyz.py  # H,V,PM → XYZ
├── tabuler_axe.py                       # Génération points réguliers
├── exemple_axe.txt                      # Format fichier axe
├── test_scan.asc                        # Données de test
│
├── core/                                # Classes géométriques (existant)
│   ├── geometrie.py                     # Point, Vecteur
│   ├── elements.py                      # Éléments d'axe
│   └── axe.py                           # Classe Axe
│
├── clothoide_precise.py                 # Calculs clothoïdes (à intégrer)
├── gestionnaire_clothoides.py           # Gestion clothoïdes (à intégrer)
│
└── README_PROJECTION_AXES.md            # Cette documentation
```

---

## 🎓 Concepts topographiques

### Système de coordonnées d'axe

- **PM (Point Métrique)** : Abscisse curviligne le long de l'axe (origine au PM 0)
- **H (Déport horizontal)** : Distance perpendiculaire à l'axe dans le plan horizontal
  - Positif = à droite de l'axe (dans le sens croissant des PM)
  - Négatif = à gauche
- **V (Déport vertical)** : Différence d'altitude par rapport à l'axe
  - Positif = au-dessus de l'axe
  - Négatif = en dessous

### Gisement et pente

- **Gisement** : Angle horizontal par rapport au Nord, en grades (0-400g)
  - 0g = Nord, 100g = Est, 200g = Sud, 300g = Ouest
- **Pente** : Inclinaison de l'axe en pourcentage
  - Positif = montée, Négatif = descente

---

## 📝 Changelog

**v1.1 - 26/11/2025**
- ⭐ Nouvel outil `projeter_multi_axes.py` pour traitement batch multi-axes
- Configuration centralisée des axes via `axes_config.csv`
- Projection automatique selon colonne identifiant
- Support CSV et Excel en entrée/sortie
- Statistiques détaillées par axe

**v1.0 - 25/11/2025**
- Projection XYZ → H,V,PM sur droite 3D
- Projection inverse H,V,PM → XYZ
- Tabulation d'axe
- Gestion de gros volumes (millions de points)
- Modes vertical et perpendiculaire
- Axes personnalisables via fichier
- Détection automatique des séparateurs

---

**Prêt pour l'évolution vers les axes complexes avec éléments géométriques multiples !** 🚀
