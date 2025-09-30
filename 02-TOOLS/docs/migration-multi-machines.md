# Guide de Migration Multi-Machines

## 🖥️ **Pour votre autre ordinateur (lecteur D:)**

### **Option A : Installation automatique (Recommandée)**

1. **Créer d'abord un dépôt GitHub** (depuis cette machine) :
   ```powershell
   # Sur GitHub.com, créer un dépôt privé : "dev-workspace"
   git remote add origin https://github.com/VotreNom/dev-workspace.git
   git push -u origin main
   ```

2. **Sur l'autre machine** (lecteur D:), télécharger et exécuter :
   ```powershell
   # Télécharger le script d'installation
   Invoke-WebRequest -Uri "URL_DU_SCRIPT" -OutFile "install.ps1"

   # Exécuter l'installation sur lecteur D:
   .\install.ps1 -Drive "D" -GitUrl "https://github.com/VotreNom/dev-workspace.git"
   ```

### **Option B : Installation manuelle**

1. **Cloner le dépôt** :
   ```powershell
   git clone https://github.com/VotreNom/dev-workspace.git D:\data\20-DEVELOPPEMENT
   cd D:\data\20-DEVELOPPEMENT
   ```

2. **Activer VS Code Settings Sync** :
   - Ouvrir VS Code dans le dossier
   - `Ctrl+Shift+P` → `Settings Sync: Turn On`
   - Se connecter avec le même compte

3. **Tester** :
   ```powershell
   .\02-TOOLS\scripts\backup-dev.ps1 -Mode "git"
   ```

## ⚙️ **Configurations automatiquement adaptées :**

### ✅ **Fonctionnent sur tout lecteur :**
- Script de backup (détection automatique du chemin)
- VS Code Settings Sync
- Git (fonctionne partout)
- Configurations relatives

### ⚠️ **À adapter manuellement si nécessaire :**
- Chemins absolus dans vos scripts personnels
- Variables d'environnement spécifiques

## 🔄 **Synchronisation entre machines :**

### **Workflow quotidien :**
1. **Machine 1 (C:)** : Travailler → Commit → Push
2. **Machine 2 (D:)** : Pull → Travailler → Commit → Push
3. **Repeat** 🔄

### **Automatisation possible :**
```powershell
# Script de sync quotidien
git pull                              # Récupérer les dernières modifications
# ... travailler ...
.\02-TOOLS\scripts\backup-dev.ps1     # Backup automatique + commit + push
```

## 🛠️ **Dépannage :**

### **Problème de chemin ?**
- Vérifier que le script utilise des chemins relatifs
- Adapter les variables d'environnement si nécessaire

### **Conflit de merge ?**
```powershell
git status                  # Voir les conflits
git add .                   # Après résolution
git commit -m "Résolution conflits"
git push
```

### **VS Code ne synchronise pas ?**
- Vérifier la connexion internet
- Re-activer Settings Sync
- Vérifier le compte connecté

## 📁 **Structure adaptative :**

```
{LECTEUR}:\data\20-DEVELOPPEMENT\
├── .vscode\              # Configs VS Code (sync auto)
├── 01-PROJECTS\          # Vos projets
├── 02-TOOLS\
│   ├── scripts\
│   │   ├── backup-dev.ps1           # ✅ Adaptatif
│   │   └── install-on-new-machine.ps1  # ✅ Aide installation
│   └── docs\
└── 05-ARCHIVE\backup\    # Backups locaux
```

## 🎯 **Avantages de cette approche :**
- **Indépendant du lecteur** (C:, D:, E:, etc.)
- **Synchronisation automatique** des paramètres VS Code
- **Historique complet** avec Git
- **Backup local** + **sauvegarde cloud**
- **Installation en 1 commande** sur nouvelle machine
