# 🖥️ Installation sur votre autre machine (Lecteur D:)

## 📋 **Instructions rapides**

### **Méthode automatique (Recommandée)**

```powershell
# 1. Ouvrir PowerShell en tant qu'Administrateur
# 2. Exécuter cette commande :
iex (iwr -UseBasicParsing "https://raw.githubusercontent.com/olivierboissardggc2-max/dev-workspace/main/02-TOOLS/scripts/install-on-new-machine.ps1").Content

# Ou si vous préférez télécharger d'abord :
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/olivierboissardggc2-max/dev-workspace/main/02-TOOLS/scripts/install-on-new-machine.ps1" -OutFile "install.ps1"
.\install.ps1 -Drive "D"
```

### **Méthode manuelle**

```powershell
# 1. Installer Git (si pas déjà fait)
winget install Git.Git

# 2. Cloner le workspace sur lecteur D:
git clone https://github.com/olivierboissardggc2-max/dev-workspace.git D:\data\20-DEVELOPPEMENT

# 3. Se déplacer dans le dossier
cd D:\data\20-DEVELOPPEMENT

# 4. Tester
.\02-TOOLS\scripts\backup-dev.ps1 -Mode git
```

## ⚙️ **Configuration VS Code Settings Sync**

1. **Ouvrir VS Code** dans le workspace : `code .`
2. **Activer Settings Sync** :
   - `Ctrl+Shift+P`
   - Taper : `Settings Sync: Turn On`
   - Se connecter avec le même compte GitHub
   - Choisir de synchroniser :
     - ✅ Settings
     - ✅ Keyboard Shortcuts
     - ✅ Extensions
     - ✅ UI State
     - ✅ Snippets

## 🔄 **Utilisation quotidienne**

### **Commencer la journée :**
```powershell
git pull  # Récupérer les dernières modifications
```

### **Finir la journée :**
```powershell
.\02-TOOLS\scripts\backup-dev.ps1 -Mode all  # Backup + commit + push
```

## 🏆 **C'est tout !**

Votre workspace sera identique sur les deux machines avec :
- ✅ Même configuration VS Code (automatique)
- ✅ Mêmes projets (Git)
- ✅ Même organisation de fichiers
- ✅ Scripts de backup adaptatifs
- ✅ Synchronisation en temps réel

---

**Dépôt GitHub :** https://github.com/olivierboissardggc2-max/dev-workspace
