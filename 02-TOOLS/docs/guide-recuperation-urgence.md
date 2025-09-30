# 🚨 GUIDE DE RÉCUPÉRATION D'URGENCE

## 🛡️ **VOS FICHIERS SONT EN SÉCURITÉ !**

### **📍 EMPLACEMENTS DE VOS SAUVEGARDES :**

#### **1. 🌐 GitHub (Principal - Accessible partout)**
**URL :** https://github.com/olivierboissardggc2-max/dev-workspace

**Récupération :**
- 💻 **Via navigateur** : Cliquer sur "Code" → "Download ZIP"
- 📱 **Via mobile** : App GitHub ou navigateur mobile
- 🖥️ **Via terminal** : `git clone https://github.com/olivierboissardggc2-max/dev-workspace.git`

#### **2. 💾 Backup Local Automatique**
**Emplacement :** `C:\data\20-DEVELOPPEMENT\05-ARCHIVE\backup\`
**Format :** `DEV-AAAAMMJJ-HHMM` (ex: `DEV-20250930-1640`)

#### **3. 🖥️ Votre autre machine (Lecteur D:)**
**Emplacement :** `D:\data\20-DEVELOPPEMENT\` (une fois installé)

---

## 🚨 **PROCÉDURES D'URGENCE :**

### **💥 ORDINATEUR HS - RÉCUPÉRATION IMMÉDIATE**

#### **Méthode 1 : Nouveau PC (5 min)**
```powershell
# 1. Installer Git
winget install Git.Git

# 2. Récupérer TOUT le workspace
git clone https://github.com/olivierboissardggc2-max/dev-workspace.git C:\data\20-DEVELOPPEMENT

# 3. Continuer à travailler normalement
cd C:\data\20-DEVELOPPEMENT
```

#### **Méthode 2 : Accès web immédiat (30 sec)**
1. Aller sur https://github.com/olivierboissardggc2-max/dev-workspace
2. Cliquer sur le bouton vert **"Code"**
3. **"Download ZIP"**
4. Décompresser → Tous vos fichiers récupérés !

#### **Méthode 3 : Depuis mobile**
1. Installer l'app GitHub
2. Se connecter avec votre compte
3. Naviguer dans olivierboissardggc2-max/dev-workspace
4. Voir/télécharger n'importe quel fichier

---

## 🔍 **RÉCUPÉRATION DE FICHIERS SPÉCIFIQUES :**

### **📁 Fichier supprimé par erreur**
```powershell
# Voir l'historique du fichier
git log --oneline -- chemin/vers/fichier.ext

# Restaurer depuis un commit précédent
git checkout COMMIT_ID -- chemin/vers/fichier.ext
```

### **📅 Retour à une version antérieure**
```powershell
# Voir tous les commits
git log --oneline

# Revenir à un commit spécifique
git checkout COMMIT_ID
```

### **🔍 Rechercher dans l'historique**
```powershell
# Chercher dans tous les commits
git log --grep="mot-clé"

# Chercher des modifications de contenu
git log -S "texte recherché"
```

---

## 📱 **ACCÈS MOBILE/WEB :**

### **Depuis n'importe quel appareil :**
1. **GitHub Web** : https://github.com/olivierboissardggc2-max/dev-workspace
2. **Édition en ligne** : Cliquer sur un fichier → bouton "Edit" (crayon)
3. **VS Code Web** : https://github.dev/olivierboissardggc2-max/dev-workspace
4. **Download individuel** : Cliquer sur fichier → "Raw" → Ctrl+S

---

## 🛠️ **OUTILS DE RÉCUPÉRATION :**

### **Si Git n'est pas disponible :**
- **Direct download** : ZIP depuis GitHub
- **Browser** : Parcourir les fichiers en ligne
- **Mobile app** : GitHub app pour smartphone

### **Si GitHub est inaccessible :**
- **Backup local** : `05-ARCHIVE\backup\`
- **Autre machine** : Votre workspace sur lecteur D:
- **Historique Git local** : `git log` même hors ligne

---

## ✅ **VÉRIFICATIONS RÉGULIÈRES :**

### **Test mensuel recommandé :**
```powershell
# 1. Vérifier que GitHub est à jour
git status
git push

# 2. Vérifier les backups locaux
ls 05-ARCHIVE\backup\

# 3. Tester une récupération
git clone https://github.com/olivierboissardggc2-max/dev-workspace.git C:\temp\test-recovery
```

---

## 🎯 **RÉSUMÉ - VOS GARANTIES :**

- ✅ **Accès web 24/7** depuis n'importe où
- ✅ **Historique complet** de toutes les modifications
- ✅ **Backups automatiques** quotidiens
- ✅ **Récupération en 30 secondes** (web) ou 5 minutes (complet)
- ✅ **Indépendant de l'OS** (Windows, Mac, Linux, mobile)
- ✅ **Gratuit et illimité** avec GitHub

**🛡️ VOS FICHIERS SONT PLUS EN SÉCURITÉ QUE DANS UN COFFRE-FORT !**
