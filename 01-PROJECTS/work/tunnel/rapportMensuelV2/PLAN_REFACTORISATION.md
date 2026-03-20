# 🔧 PLAN DE REFACTORISATION - Rapport Mensuel V2

## 🎯 OBJECTIFS
1. **Éliminer** les chemins hardcodés
2. **Consolider** les fichiers éparpillés
3. **Améliorer** la robustesse du code
4. **Simplifier** l'architecture

## 📋 ÉTAPES DE REFACTORISATION

### ⚡ **PHASE 1 : NETTOYAGE IMMÉDIAT (30 min)**

#### 1.1 Corriger les chemins obsolètes
```python
# ❌ AVANT (hardcodé)
default_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250901-rapport mensuel aout\1-tableaux"

# ✅ APRÈS (configurable)
default_path = os.path.join(os.path.expanduser("~"), "Documents", "SMC_Reports")
```

#### 1.2 Nettoyer requirements.txt
```diff
- tkinter  # Déjà inclus dans Python
+ python-dateutil  # Pour parsing dates robuste
```

#### 1.3 Supprimer fichiers de debug éparpillés
- Consolider dans `tests/debug/`
- Garder seulement les fonctionnels

### 🔧 **PHASE 2 : RESTRUCTURATION (1h)**

#### 2.1 Créer fichier de configuration central
```python
# config/app_config.py
class AppConfig:
    DEFAULT_INPUT_DIR = os.path.join(os.path.expanduser("~"), "Documents", "SMC_Input")
    DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Documents", "SMC_Output")
    DEFAULT_MONTH = datetime.now().strftime("%Y-%m")
```

#### 2.2 Améliorer gestion d'erreurs
```python
# Wrapping robuste pour threading
def safe_extraction_wrapper(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Erreur extraction: {e}")
        return False
```

#### 2.3 Consolider les utilitaires
```
src/
├── core/           # Modules principaux
├── utils/          # Utilitaires consolidés
├── tests/          # Tests unifiés
├── config/         # Configuration
└── main.py         # Point d'entrée unique
```

### 🚀 **PHASE 3 : AMÉLIORATIONS (1h)**

#### 3.1 Configuration dynamique
- Lecture depuis `settings.yaml`
- Variables d'environnement
- Interface pour modifier config

#### 3.2 Validation robuste
- Vérification existence dossiers
- Validation format mois
- Gestion permissions fichiers

#### 3.3 Logging amélioré
- Fichier de log rotatif
- Niveaux de log configurables
- Interface log en temps réel

## 🎯 RÉSULTAT ATTENDU

### ✅ **APRÈS REFACTORISATION**
```
smc-data-extractor/
├── 📁 src/
│   ├── main.py              # 🎯 Point d'entrée unique
│   ├── config/
│   │   └── app_config.py    # 🔧 Configuration centralisée
│   ├── core/                # 💾 Logique métier
│   ├── gui/                 # 🖥️ Interface utilisateur
│   ├── utils/               # 🛠️ Utilitaires consolidés
│   └── tests/               # 🧪 Tests unifiés
├── 📁 config/
│   ├── settings.yaml        # ⚙️ Configuration globale
│   └── paths.yaml          # 📂 Chemins configurables
├── 📁 logs/                 # 📝 Logs de l'application
└── 📁 output/              # 📤 Sorties générées
```

### 🏆 **BÉNÉFICES**
- ✅ **Portable** : Fonctionne sur n'importe quelle machine
- ✅ **Maintenable** : Code organisé et documenté
- ✅ **Robuste** : Gestion d'erreurs améliorée
- ✅ **Configurable** : Paramètres externalisés
- ✅ **Testable** : Tests consolidés et exécutables

## ⚡ **ACTIONS IMMÉDIATES RECOMMANDÉES**

1. **SAUVEGARDER** l'état actuel
2. **CORRIGER** les chemins hardcodés (5 min)
3. **NETTOYER** les fichiers inutiles (10 min)
4. **TESTER** que tout fonctionne encore
5. **IMPLÉMENTER** les améliorations par phases

## 🔥 **PRIORITÉ ABSOLUE**
**Remplacer IMMÉDIATEMENT** les chemins obsolètes pour éviter les erreurs de production !
