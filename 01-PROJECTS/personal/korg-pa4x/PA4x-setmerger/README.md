# PA4x Set Merger

Outil de fusion de fichiers SET et STY pour claviers Korg PA4x.

## Fonctionnalités

- 📂 **Importer des sources** : fichiers STY isolés, dossiers de STY, ou SET existants
- 🔀 **Fusionner** : combinez plusieurs sources en un seul SET
- 💾 **Exporter** : créez un SET complet prêt à charger sur votre PA4x

## Structure d'un SET Korg PA4x

```
MonSet.SET/
├── STYLE/
│   ├── FAVORITE01.STY  à  FAVORITE10.STY  (10 banques Favorites)
│   └── USER01.STY  à  USER03.STY          (3 banques Users)
├── GLOBAL/
│   └── SETUP.GBL
├── SOUND/
│   └── USER01.PCG
├── PCM/
│   └── RAM*.PCM
└── MULTISMP/
    └── RAM.KMP
```

## Installation

```bash
# Cloner le dépôt
git clone <repo-url>
cd PA4x-setmerger

# Installer les dépendances (optionnel, tkinter est inclus avec Python)
pip install -r requirements.txt

# Lancer l'application
python main.py
```

## Utilisation

### Interface graphique

1. **Ajouter des sources** :
   - Cliquez sur `+ STY` pour ajouter des fichiers STY individuels
   - Cliquez sur `+ Dossier` pour ajouter tous les STY d'un répertoire
   - Cliquez sur `+ SET` pour importer les banques d'un SET existant

2. **Assigner les banques** :
   - Double-cliquez sur une source pour choisir son slot de destination
   - Ou utilisez `Auto-Assign` pour un placement automatique
   - Les noms FAVORITE01-10 et USER01-03 sont respectés

3. **Enregistrer** :
   - Donnez un nom à votre SET
   - Cliquez sur `Enregistrer SET`
   - Choisissez le dossier de destination

### Ligne de commande (CLI)

```bash
# Lister le contenu d'un SET
python -m src.cli info MonSet.SET

# Fusionner des STY en un SET
python -m src.cli merge -o Output.SET source1.STY source2.STY

# Extraire les STY d'un SET
python -m src.cli extract MonSet.SET -o ./output/
```

## Types de banques

| Type | Nombre | Fichiers |
|------|--------|----------|
| Favorites | 10 | FAVORITE01.STY - FAVORITE10.STY |
| Users | 3 | USER01.STY - USER03.STY |

## Licence

MIT License
