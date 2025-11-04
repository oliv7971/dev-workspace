# 🚀 GUIDE DE DÉMARRAGE RAPIDE

## ⚡ Comment lancer le programme

### 🎯 SOLUTION SIMPLE (RECOMMANDÉE)

1. **Ouvrir PowerShell dans le dossier du projet**
2. **Utiliser `py` au lieu de `python`** :

```bash
# Test du système
py demo.py

# Programme principal
py src/main.py

# Diagnostic de configuration
py diagnostic.py
```

### 🔧 POURQUOI `py` et pas `python` ?

Sur Windows, Python s'installe avec un lanceur spécial `py` qui :
- ✅ Fonctionne toujours (même si Python pas dans PATH)
- ✅ Gère automatiquement les versions multiples
- ✅ Est la méthode officielle Microsoft/Python

### 📋 ÉTAPES DE PREMIÈRE UTILISATION

#### 1️⃣ **Test initial**
```bash
py demo.py
```
→ Vérifie que tout fonctionne

#### 2️⃣ **Configuration** 
Modifier `config/config.json` selon vos chemins :
```json
{
  "chemins": {
    "source_base": "VOTRE_DOSSIER_ACTIVITES",
    "destination_temp": "VOTRE_DOSSIER_TEMP",
    "destination_finale": "VOTRE_DOSSIER_GALERIES",
    "backup_dir": "VOTRE_DOSSIER_BACKUP"
  }
}
```

#### 3️⃣ **Lancement**
```bash
py src/main.py
```

### 🎛️ MENU PRINCIPAL

Quand vous lancez `py src/main.py`, vous avez :

```
[1] 📥 Collecter les données (depuis chronologique)
[2] 🔍 Valider les classifications  
[3] 📁 Appliquer le classement final
[4] 🔄 Processus complet (1→2→3)
[5] 💾 Gestion des backups
[6] 📊 Statistiques
[0] ❌ Quitter
```

### 🛡️ MODE SÉCURISÉ (PREMIÈRE FOIS)

Pour tester sans risque :

1. **Option [4] Processus complet**
2. Le système va :
   - Copier dans un dossier temporaire
   - Vous demander validation
   - **NE RIEN modifier dans vos vrais dossiers**
3. Vérifier les résultats temporaires
4. Si OK → appliquer définitivement

### 📁 STRUCTURE DES FICHIERS IMPORTANTS

```
prog_classement/
├── lancer.bat              ← Lanceur Windows (double-clic)
├── demo.py                 ← Test du système  
├── diagnostic.py           ← Vérification config
├── src/main.py            ← Programme principal
├── config/
│   ├── config.json        ← Configuration principale ⚙️
│   ├── categories.json    ← Types d'activités
│   └── correspondances.json ← Codes galeries
```

### 🔧 PARAMÉTRAGE ESSENTIEL

#### **config.json** - À adapter OBLIGATOIREMENT :
```json
{
  "chemins": {
    "source_base": "C:\\MES_DONNEES\\ACTIVITES",     ← VOS activités chronologiques
    "destination_temp": "C:\\Temp\\test-classement", ← Dossier de test
    "destination_finale": "C:\\MES_DONNEES\\GALERIES", ← VOS galeries finales
    "backup_dir": "C:\\Backup\\classement"           ← VOS sauvegardes
  },
  "options": {
    "mode_securise": true,        ← Laissez à true au début !
    "backup_automatique": true,   ← Sauvegardes automatiques
    "validation_interactive": true ← Vous demande confirmation
  }
}
```

#### **categories.json** - Types d'activités :
```json
{
  "IMPLANTATION": ["implant", "imp"],
  "LEVE": ["levé", "leve", "lv"], 
  "AUSCULTATION": ["aus", "auscult"]
}
```

#### **correspondances.json** - Codes galeries :
```json
{
  "GCS": "GALERIE GCS",
  "1631": "ALVEOLE AHA1631"
}
```

### 🚨 DÉPANNAGE

**Erreur "python n'est pas reconnu"** :
→ Utiliser `py` au lieu de `python`

**Erreur "fichier manquant"** :
→ Lancer `py diagnostic.py` pour voir ce qui manque

**Programme se bloque** :
→ Vérifier les chemins dans config.json

**Pas de backup créé** :
→ Vérifier que le dossier backup_dir est accessible

### ✅ CHECKLIST AVANT PREMIÈRE UTILISATION

- [ ] `py demo.py` fonctionne
- [ ] config.json adapté à vos chemins  
- [ ] categories.json correspond à vos activités
- [ ] correspondances.json correspond à vos galeries
- [ ] mode_securise = true
- [ ] Dossier de backup accessible

### 🎯 UTILISATION RECOMMANDÉE

1. **Test** : `py demo.py`
2. **Configuration** : Adapter les JSON
3. **Premier run** : `py src/main.py` → Option [4]
4. **Vérification** : Contrôler résultats temporaires  
5. **Application** : Si OK → classement définitif

**📞 En cas de problème** : Tous les logs sont dans `C:\Temp\logs\classement\`