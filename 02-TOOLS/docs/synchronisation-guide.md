# Guide de Synchronisation - Environnement de Développement

## 🔧 Configuration VS Code Settings Sync

### Activation :
1. Ouvrir VS Code
2. Ctrl+Shift+P → "Settings Sync: Turn On"
3. Connecter avec compte GitHub ou Microsoft
4. Choisir ce qu'on synchronise

### Avantages :
- ✅ Synchronisation automatique des paramètres
- ✅ Extensions identiques sur toutes les machines
- ✅ Configurations de débogage partagées
- ✅ Gratuit et intégré

## 📁 Stratégie de Synchronisation des Projets

### Option 1: Git + GitHub/GitLab (Recommandé)
```powershell
# Installation Git (si pas déjà fait)
winget install Git.Git

# Initialiser le dépôt principal
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/votre-nom/dev-workspace.git
git push -u origin main
```

### Option 2: Cloud Storage avec exclusions intelligentes
- **OneDrive/Google Drive** pour backup général
- **Exclusions**: `.venv/`, `node_modules/`, `__pycache__/`, etc.

### Option 3: Synchronisation hybride
- **Git** pour code source et configs importantes
- **Cloud** pour documentation et ressources
- **Backup local** pour tout le reste

## 🔄 Scripts de Synchronisation

### Script PowerShell de backup automatique :
```powershell
# backup-dev.ps1
$source = "C:\data\20-DEVELOPPEMENT"
$backup = "D:\Backup\DEV-$(Get-Date -Format 'yyyyMMdd')"
$cloud = "$env:OneDrive\DEV-Sync"

# Backup local
robocopy $source $backup /MIR /XD .git __pycache__ .venv node_modules

# Sync vers cloud (fichiers importants seulement)
robocopy "$source\01-PROJECTS" "$cloud\01-PROJECTS" /MIR /XD .venv __pycache__
robocopy "$source\.vscode" "$cloud\.vscode" /MIR
```

## 🛡️ Stratégie de Sauvegarde

### Règle 3-2-1 :
- **3** copies de vos données importantes
- **2** supports différents (local + cloud)
- **1** copie hors site (GitHub/cloud)

### Fréquence :
- **Temps réel** : VS Code Settings + Auto-save
- **Quotidien** : Push Git des modifications
- **Hebdomadaire** : Backup complet local
- **Mensuel** : Vérification intégrité backups

## 🚀 Plan de Migration

### Phase 1 : Immediate
1. Activer VS Code Settings Sync
2. Installer Git si nécessaire
3. Créer compte GitHub/GitLab

### Phase 2 : Court terme
1. Initialiser dépôt Git principal
2. Configurer .gitignore optimisé
3. Premier push vers remote

### Phase 3 : Long terme
1. Scripts automatisés
2. CI/CD pour projets importants
3. Backup automatique cloud

## 🔧 Outils Recommandés

### Gratuits :
- **Git** + **GitHub** (illimité privé)
- **VS Code Settings Sync**
- **OneDrive/Google Drive** (avec exclusions)

### Payants (optionnel) :
- **GitHub Pro** (fonctionnalités avancées)
- **Dropbox/Box** (meilleure sync selective)
- **BackBlaze** (backup cloud automatique)

## 📱 Accès Mobile

Pour consulter/éditer en déplacement :
- **GitHub Mobile** (lecture code)
- **VS Code Web** (github.dev)
- **Termux** (Android, environnement Linux)
