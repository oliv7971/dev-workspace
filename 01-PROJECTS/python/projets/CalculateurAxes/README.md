# Calculateur d'Axes v1.0

Application Python pour calculs topographiques d'axes routiers et ferroviaires avec gestion des projections cartographiques.

## 🚀 Fonctionnalités principales

- **Géométrie d'axe** : Alignements droits, arcs circulaires, clothoïdes
- **Calculs par lots** : Import/Export Excel, projections de masse
- **Projections cartographiques** : Lambert, altérations linéaires, grilles IGN
- **Export CAO** : Export DXF pour AutoCAD/MicroStation
- **Interface intuitive** : Menu interactif avec démonstrations

## 📋 Pré-requis

- Python 3.8 ou supérieur
- Environnement virtuel recommandé

## 🔧 Installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd CalculateurAxes
```

2. **Créer un environnement virtuel**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

## 🏃 Utilisation

### Lancement de l'application
```bash
python main.py
```

### Menu principal
1. **Créer axe d'exemple** - Génère un axe de démonstration
2. **Calculs par lots** - Tabulation et projections de masse
3. **Projections** - Test des modes de projection
4. **Exports** - Génération Excel et DXF
5. **Informations axe** - Détails de l'axe actuel

### Tests unitaires
```bash
python tests/run_tests.py
```

## 📊 Structure du projet

```
CalculateurAxes/
├── main.py                 # Application principale
├── config.py              # Configuration centralisée
├── logging_utils.py       # Système de logging
├── validation.py          # Validation des données
├── cache_utils.py         # Optimisation par cache
├── core/                  # Classes géométriques
│   ├── geometrie.py       # Point, Vecteur, conversions
│   ├── elements.py        # Éléments d'axe
│   ├── axe.py            # Axe en plan et profil
│   └── projections.py    # Gestion projections
├── calculs/              # Algorithmes de calcul
│   ├── batch.py          # Calculs par lots
│   └── transformations.py # Transformations coordonnées
├── data_io/              # Import/Export
│   ├── excel.py          # Gestion Excel
│   └── dxf.py           # Export DXF
├── tests/               # Tests unitaires
│   ├── test_geometrie.py
│   ├── test_elements.py
│   └── run_tests.py
├── logs/                # Fichiers de log
├── exemples/           # Fichiers de démonstration
└── requirements.txt    # Dépendances Python
```

## 🎯 Conventions métier

### Systèmes de coordonnées
- **Grades** : 0-400g (convention française)
- **Gisements** : Nord = 0g, sens horaire
- **PM** : Point Métrique depuis origine d'axe
- **Déports** : Positif = droite, négatif = gauche

### Projections supportées
- **Aucune** : Distances terrain directes
- **Manuelle** : Altération spécifiée (ppm)
- **Calibrée** : Calculée depuis points de référence
- **IGN** : Grilles officielles (nécessite pyproj)

## 📄 Formats supportés

### Import Excel
- **Points** : `ID | X | Y | Z | PM`
- **Éléments** : `Type | Param1 | Param2 | Param3`
- **Profil** : `PM | Z | Pente`

### Export
- **Excel** : Tabulations complètes avec statistiques
- **DXF** : Compatible AutoCAD/MicroStation

## ⚙️ Configuration

Le fichier `config.py` centralise tous les paramètres :

```python
# Précisions de calcul
PRECISION_CALCUL = 1e-6
TOLERANCE_PROJECTION = 0.001

# Limites de sécurité
RAYON_MIN = 10     # mètres
RAYON_MAX = 100000 # mètres
```

## 📊 Logging et monitoring

L'application génère automatiquement :
- `logs/calculateur_axes.log` : Log général
- `logs/erreurs.log` : Erreurs critiques uniquement

Niveaux de log configurables selon l'environnement.

## 🧪 Tests et qualité

### Couverture des tests
- Classes géométriques de base
- Éléments d'axe (alignements, arcs)
- Validation des données
- Système de cache

### Lancement des tests
```bash
cd tests
python run_tests.py
```

## 🔍 Dépannage

### Problèmes courants

1. **Module pyproj non trouvé**
   - Fonctionnalité optionnelle, les calculs IGN seront désactivés
   - Installation : `pip install pyproj`

2. **Erreur import ezdxf**
   - Export DXF désactivé
   - Installation : `pip install ezdxf`

3. **Erreurs de validation Excel**
   - Vérifier format des colonnes (X, Y obligatoires)
   - Contrôler cohérence des données

### Logs utiles
```bash
# Voir les erreurs récentes
cat logs/erreurs.log

# Monitoring en temps réel
tail -f logs/calculateur_axes.log
```

## 🚧 Développement

### Extensions possibles
- Interface graphique (tkinter/PyQt)
- Export PDF de rapports
- Module de visualisation 3D
- API REST pour intégration

### Architecture modulaire
Le code respecte les principes SOLID et permet facilement :
- Ajout nouveaux éléments géométriques
- Extensions des formats I/O
- Intégration nouveaux systèmes de projection

## 📝 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

## 👥 Contribution

Les contributions sont bienvenues ! Merci de :
1. Fork le projet
2. Créer une branche feature
3. Commiter les changements
4. Pousser la branche
5. Ouvrir une Pull Request

## 📞 Support

Pour questions ou problèmes :
- Créer une issue sur GitHub
- Consulter la documentation dans `docs/`
- Vérifier les logs d'application

---

**Calculateur d'Axes v1.0** - Outil professionnel pour topographes et ingénieurs VRD 🛣️