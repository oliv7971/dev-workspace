# Système de Classement Automatique - BURE

## 🎯 Vue d'ensemble

Système intelligent de classement automatique pour gérer la double organisation de vos données BURE :
- **Organisation chronologique** : suivi quotidien par année/mois/jour
- **Organisation thématique** : classement par galerie et type d'activité

## ✨ Fonctionnalités principales

### 🔄 Processus automatisé complet
- **Collecte** : récupération depuis l'organisation chronologique
- **Classification** : détection automatique des galeries et activités
- **Validation** : interface interactive pour vérifier/ajuster
- **Application** : classement final avec gestion des conflits

### 🛡️ Sécurité et fiabilité
- **Backups automatiques** avant toute modification
- **Mode sécurisé** avec confirmations
- **Espace temporaire** pour validation avant application
- **Logging complet** de toutes les opérations

### 🔍 Gestion intelligente des conflits
- **Détection automatique** des doublons et conflits
- **Stratégies multiples** : fusion, écrasement, renommage
- **Interface interactive** pour les cas complexes
- **Comparaison de fichiers** (taille, date, hash)

### 📊 Suivi et monitoring
- **Logs structurés** avec rotation automatique
- **Statistiques détaillées** par session
- **Rapports de validation** sauvegardés
- **Historique des opérations**

## 🏗️ Structure du projet

```
prog_classement/
├── src/                           # Code source
│   ├── main.py                   # Script principal avec menu
│   ├── logger.py                 # Système de logging
│   ├── validation_interactive.py # Validation des classifications
│   ├── gestion_conflits.py      # Résolution des conflits
│   ├── backup_manager.py        # Gestion des sauvegardes
│   ├── classerDossiersBure.py   # Script original (legacy)
│   ├── recupe_donnees.py        # Collecte des données
│   └── deplacer_a_classer.py    # Déplacement (legacy)
├── config/                       # Configuration
│   ├── config.json              # Configuration principale
│   ├── categories.json          # Catégories d'activités
│   └── correspondances.json     # Mapping galeries
├── docs/                        # Documentation
├── tests/                       # Tests unitaires
└── demo.py                      # Script de démonstration
```

## 🚀 Installation et configuration

### 1. Préparation
```bash
git clone <repository>
cd prog_classement
```

### 2. Configuration
Modifiez `config/config.json` selon votre environnement :

```json
{
  "chemins": {
    "source_base": "C:\\data\\11-CHANTIERS\\BURE\\10-ACTIVITES",
    "destination_temp": "C:\\Temp\\activites-par-galerie",
    "destination_finale": "C:\\data\\11-CHANTIERS\\BURE\\11-GALERIES",
    "backup_dir": "C:\\Backup\\classement",
    "logs_dir": "C:\\Temp\\logs\\classement"
  },
  "options": {
    "mode_securise": true,
    "backup_automatique": true,
    "validation_interactive": true
  }
}
```

### 3. Test de l'installation
```bash
python demo.py
```

## 🖥️ Utilisation

### Lancement du système principal
```bash
python src/main.py
```

### Menu principal
- **[1] Collecter les données** : Import depuis organisation chronologique
- **[2] Valider les classifications** : Interface interactive de vérification
- **[3] Appliquer le classement** : Copie finale vers galeries
- **[4] Processus complet** : Exécution automatique 1→2→3
- **[5] Gestion des backups** : Interface de sauvegarde/restauration
- **[6] Statistiques** : Affichage des métriques de session
- **[7] Configuration** : Paramétrage du système
- **[8] Nettoyage** : Suppression des fichiers temporaires

### Processus recommandé pour nouveaux utilisateurs

1. **Premier test** :
   ```bash
   python demo.py  # Créer structure d'exemple
   ```

2. **Configuration** :
   - Adapter les chemins dans `config/config.json`
   - Vérifier `config/categories.json` et `config/correspondances.json`

3. **Test en mode sécurisé** :
   - Lancer `python src/main.py`
   - Utiliser l'option [4] Processus complet
   - Vérifier dans l'espace temporaire avant validation

4. **Application en production** :
   - Une fois satisfait des résultats temporaires
   - Appliquer le classement final

## 🔧 Configuration avancée

### Catégories d'activités (`config/categories.json`)
```json
{
  "IMPLANTATION": ["implant", "imp", "implantation"],
  "AUSCULTATION": ["aus", "auscult", "conv", "convergences"],
  "LEVE": ["levé", "leve", "lev", "lv"],
  "POLYGO": ["poly", "polygo", "refs"]
}
```

### Correspondances galeries (`config/correspondances.json`)
```json
{
  "1631": "ALVEOLE AHA1631",
  "GCS": "GALERIE GCS",
  "GHA": "GALERIE GHA"
}
```

### Options de sécurité
- **mode_securise** : Demande confirmation pour actions critiques
- **backup_automatique** : Sauvegarde avant modifications
- **validation_interactive** : Interface de validation (vs automatique)
- **max_backups** : Nombre de sauvegardes à conserver

## 📝 Logging et monitoring

### Fichiers de log
- **Localisation** : Définie dans `config.json` (`logs_dir`)
- **Rotation** : Automatique (10MB max par fichier)
- **Format** : `classement_YYYYMM.log`

### Types de logs
- **INFO** : Opérations normales
- **WARNING** : Situations nécessitant attention
- **ERROR** : Erreurs nécessitant intervention
- **DEBUG** : Détails techniques (développement)

### Exemple de log
```
2024-10-29 14:30:15 | INFO     | executer_collecte    | OPERATION: COPIE | source=activites/2024/10/29/a | destination=temp/GCS/_a_classer
2024-10-29 14:30:16 | WARNING  | resoudre_conflit     | Conflit détecté pour GALERIE GCS
2024-10-29 14:30:17 | INFO     | backup_avant_operation | Backup créé: auto_classement_20241029_143017
```

## 🔍 Gestion des conflits

### Types de conflits détectés
1. **Fichier vs Fichier** : Même nom, contenus différents
2. **Dossier vs Dossier** : Structures qui se chevauchent
3. **Type différent** : Fichier vs dossier

### Stratégies de résolution
- **Automatique** : Basée sur date, taille, hash
- **Fusion** : Combine le contenu (pour dossiers)
- **Écrasement** : Remplace par la source
- **Renommage** : Garde les deux avec suffixe
- **Interactive** : Demande à l'utilisateur

## 💾 Système de backup

### Types de sauvegarde
- **Copie complète** : Pour dossiers < 100MB
- **Archive ZIP** : Pour dossiers > 100MB
- **Backup automatique** : Avant chaque opération critique

### Gestion des sauvegardes
- **Rétention** : Configurable (défaut: 10 backups max)
- **Nettoyage** : Automatique des plus anciens
- **Index** : Fichier JSON avec métadonnées
- **Restauration** : Interface simple via menu

## 🐛 Dépannage

### Problèmes courants

**Erreur "Fichier de configuration manquant"**
```bash
# Vérifiez l'existence de config/config.json
ls config/
```

**Erreur "Dossier source introuvable"**
- Vérifiez le chemin `source_base` dans config.json
- Assurez-vous que le dossier existe et est accessible

**Classifications incorrectes**
- Vérifiez `config/categories.json` et `config/correspondances.json`
- Utilisez le mode validation interactive
- Consultez les logs pour comprendre la détection

**Conflits non résolus**
- Activez le mode interactif pour les conflits
- Vérifiez les permissions sur les dossiers de destination
- Consultez les backups en cas de problème

### Récupération après erreur

1. **Consultation des logs** :
   ```bash
   # Logs récents
   tail -f C:\Temp\logs\classement\classement_202410.log
   ```

2. **Restauration depuis backup** :
   - Menu [5] Gestion des backups
   - Option [4] Restaurer backup

3. **Nettoyage et redémarrage** :
   - Menu [8] Nettoyage temporaires
   - Relancer le processus depuis le début

## 📈 Évolutions futures

### Améliorations prévues
- **Interface graphique** : GUI avec drag & drop
- **API REST** : Pour intégration avec autres outils
- **Machine Learning** : Amélioration de la classification automatique
- **Synchronisation** : Mode temps réel avec surveillance dossiers
- **Notifications** : Alertes email/Teams pour opérations importantes

### Contributions
Les contributions sont bienvenues ! Voir `CONTRIBUTING.md` pour les guidelines.

## 📄 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

---

**💡 Conseil** : Commencez toujours par un test avec `demo.py` et le mode sécurisé activé!