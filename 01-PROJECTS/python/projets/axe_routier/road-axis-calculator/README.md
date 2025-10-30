# Calculateur d'Axes Routiers et Tunnels

## Vue d'ensemble
Application Python complète pour la gestion et le calcul d'axes routiers, particulièrement adaptée aux tunnels. L'application permet de :
- Définir des axes en plan (droites, arcs circulaires, clothoïdes)
- Définir des profils en long (droites, arcs verticaux, paraboles)
- Calculer des points 3D sur l'axe
- Projeter des points sur l'axe
- Calculer des déports latéraux

## Fonctionnalités

### Axe en Plan (Horizontal)
- **Droites** (`LineElement`) : segments rectilignes
- **Arcs circulaires** (`CircularArcElement`) : courbes à rayon constant
- **Clothoïdes** (`ClothoidElement`) : courbes de transition à courbure variable

### Profil en Long (Vertical)
- **Droites** (`LineProfile`) : pentes constantes
- **Arcs verticaux** (`CircularVerticalCurve`) : raccordements à courbure constante
- **Paraboles** (`ParabolicVerticalCurve`) : raccordements paraboliques du 2e degré

### Calculs disponibles
- Calcul de points (X, Y, Z) à une station donnée
- Projection de points sur l'axe (plan et profil)
- Calcul d'offsets (déports latéraux)
- Calcul de pentes à n'importe quelle station
- Export de données pour visualisation

## Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/yourusername/road-axis-calculator.git
   cd road-axis-calculator
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation

### Exemple rapide - Axe en plan

```python
from src.models import Axis, LineElement, CircularArcElement, Point
from math import radians

# Créer un axe
axe = Axis()

# Ajouter une ligne droite de 100m
axe.add_element(LineElement(Point(0, 0), Point(100, 0)))

# Ajouter un arc de cercle (rayon 50m, quart de cercle)
axe.add_element(CircularArcElement(
    center=Point(100, 50),
    radius=50,
    start_angle=radians(270),
    end_angle=radians(360),
    ccw=True
))

# Calculer un point à la station 120m
point = axe.point_at(120)
print(f"Point à PK 120 : {point}")

# Projeter un point sur l'axe
resultat = axe.project_point(Point(50, 10))
print(f"Station : {resultat['station']:.2f}m")
print(f"Déport : {resultat['offset']:.2f}m")
```

### Exemple rapide - Profil en long

```python
from src.models import VerticalProfile, LineProfile, ParabolicVerticalCurve

# Créer un profil
profil = VerticalProfile()

# Rampe montante de 5% sur 100m
profil.add_element(LineProfile(
    start_station=0,
    start_elevation=100.0,
    end_station=100,
    end_elevation=105.0
))

# Raccordement parabolique
profil.add_element(ParabolicVerticalCurve(
    start_station=100,
    start_elevation=105.0,
    length=60,
    slope_in=0.05,   # 5%
    slope_out=-0.02  # -2%
))

# Obtenir l'altitude à une station
altitude = profil.elevation_at(130)
pente = profil.slope_percent_at(130)
print(f"À PK 130 : Z={altitude:.2f}m, pente={pente:.2f}%")
```

### Exemples complets

Exécuter les exemples fournis :

```bash
# Exemples d'axes en plan
python exemple_utilisation.py

# Exemples de profils en long
python exemple_profil_en_long.py
```

## Tests

Lancer tous les tests unitaires :

```bash
# Tests des éléments d'axe en plan
python -m unittest tests.test_elements -v

# Tests du profil en long
python -m unittest tests.test_profile -v

# Tous les tests
python -m unittest discover tests -v
```

**Résultats attendus :**
- ✅ 15 tests pour l'axe en plan
- ✅ 14 tests pour le profil en long
- ✅ Total : 29 tests réussis

## Structure du projet

```
road-axis-calculator/
├── src/
│   ├── models/
│   │   ├── __init__.py          # Exports des classes
│   │   ├── point.py             # Classe Point (2D/3D)
│   │   ├── axis.py              # Axe en plan complet
│   │   ├── elements.py          # Éléments d'axe (droites, arcs, clothoïdes)
│   │   ├── profile.py           # Profil en long complet
│   │   ├── tunnel.py            # Modèle tunnel (à développer)
│   │   └── element.py           # Ancien fichier (à migrer)
│   ├── calculations/            # Fonctions de calcul avancées
│   ├── ui/                      # Interface utilisateur (à développer)
│   ├── utils/                   # Utilitaires et validateurs
│   └── config/                  # Configuration
├── tests/
│   ├── test_elements.py         # Tests axe en plan (15 tests)
│   └── test_profile.py          # Tests profil en long (14 tests)
├── exemple_utilisation.py       # Exemples axes en plan
├── exemple_profil_en_long.py    # Exemples profils en long
├── requirements.txt             # Dépendances
├── setup.py                     # Installation
└── README.md                    # Cette documentation
```

## Concepts techniques

### Clothoïde
La clothoïde est implémentée par intégration numérique (méthode d'Euler). La courbure varie linéairement le long de l'élément, ce qui permet des transitions douces entre droites et arcs.

### Raccordements verticaux
Les raccordements verticaux utilisent des paraboles du 2e degré, qui sont la norme en génie routier. L'équation générale est :
```
z(s) = a·s² + b·s + c
```
où les coefficients sont calculés pour assurer la continuité de l'altitude et de la pente.

### Système de coordonnées
- **Station (PK)** : distance curviligne le long de l'axe depuis l'origine (m)
- **Offset** : distance perpendiculaire à l'axe (m)
- **Altitude (Z)** : élévation par rapport au niveau de référence (m)

## Applications pratiques

### Tunnels
- Définition de l'axe théorique du tunnel
- Calcul des points pour l'implantation
- Projection des points de levé topographique
- Calcul des déports pour contrôle qualité
- Analyse du profil en long (pentes, raccordements)

### Routes
- Tracé d'axes routiers complets
- Calcul de volumes de terrassement
- Vérification des rayons et pentes réglementaires
- Export vers logiciels de dessin (AutoCAD, Civil 3D)

## Contributions

Les contributions sont les bienvenues ! Pour contribuer :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commit vos changements
4. Push vers la branche
5. Ouvrir une Pull Request

## Développements futurs

- [ ] Interface graphique complète (PyQt/Tkinter)
- [ ] Import/Export Excel et CSV
- [ ] Visualisation 3D avec matplotlib
- [ ] Calcul de volumes de terrassement
- [ ] Vérification des normes routières
- [ ] Support des clothoïdes analytiques (Fresnel)
- [ ] Gestion des dévers
- [ ] Cubatures

## Licence
This project is licensed under the MIT License. See the LICENSE file for more details.