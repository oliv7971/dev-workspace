# Projet de Classement de Dossiers

Ce projet automatise le classement de dossiers et fichiers selon des catégories prédéfinies.

## Structure du projet

```
prog_classement/
├── src/                    # Code source
│   ├── classerDossiersBure.py    # Script principal de classement
│   ├── recupe_donnees.py         # Récupération des données
│   └── deplacer_a_classer.py     # Déplacement des fichiers
├── config/                 # Configuration
│   ├── categories.json           # Définition des catégories
│   └── correspondances.json      # Règles de correspondance
├── docs/                   # Documentation
└── tests/                  # Tests unitaires
```

## Installation

1. Cloner le repository
2. Installer les dépendances : `pip install -r requirements.txt`
3. Configurer les catégories dans `config/categories.json`

## Utilisation

```bash
python src/classerDossiersBure.py
```

## Versioning

Ce projet utilise Git pour le versioning. Les données personnelles ne sont pas incluses dans le repository.