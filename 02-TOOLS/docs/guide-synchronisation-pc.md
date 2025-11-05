# Guide de Synchronisation entre PCs

## Problème rencontré
La synchronisation entre les machines n'a pas fonctionné correctement, causant des fichiers manquants sur l'autre PC.

## Solution 1: Mise à jour simple (si le repository existe)
```powershell
cd d:\developpement\dev-workspace
git pull origin main
```

## Solution 2: Clone complet (recommandé pour éviter les conflits)
```powershell
# Créer le répertoire de développement si nécessaire
New-Item -ItemType Directory -Path "d:\developpement\GITHUB" -Force

# Aller dans le répertoire
cd d:\developpement\GITHUB

# Cloner le repository
git clone https://github.com/olivierboissardggc2-max/dev-workspace.git

# Vérifier le contenu
Get-ChildItem dev-workspace
```

## Solution 3: Forcer la synchronisation (si des conflits existent)
```powershell
cd d:\developpement\dev-workspace
git fetch origin
git reset --hard origin/main
```

## Vérification post-synchronisation
```powershell
# Vérifier l'état
git status

# Vérifier les derniers commits
git log --oneline -5

# Comparer les dossiers
Get-ChildItem -Recurse | Measure-Object
```

## Date de création
Créé le: {{ date }}
Résolution du problème: Synchronisation manquée entre les PCs