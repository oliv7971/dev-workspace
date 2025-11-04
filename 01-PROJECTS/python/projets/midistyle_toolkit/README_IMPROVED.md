# MidiStyle Toolkit - Version Améliorée

Outil Python pour auditer, préparer et baliser des fichiers SMF (Standard MIDI File) en vue d'une conversion vers Korg PA4X.

## Améliorations Apportées

### 🎯 **Détection de Basse Intelligente**
- Algorithme sophistiqué basé sur la médiane des notes, la gamme et la densité
- Score de confiance pour éviter les fausses détections
- Prise en compte des patterns rythmiques typiques de la basse

### 🔧 **Gestion du Temps Robuste**  
- Classe `TimeTracker` pour gérer proprement les conversions temps absolu/delta
- Élimination des hacks avec `_last_abs` sur les objets MidiTrack
- Meilleure précision dans la quantification

### ✅ **Validation et Gestion d'Erreurs**
- Validation automatique des fichiers MIDI avant traitement
- Système de logging complet avec niveaux configurables
- Messages d'erreur détaillés et informatifs
- Statistiques de traitement en fin d'audit

### 🎵 **Mapping de Canaux Intelligent**
- Fonction `map_channel_to_role()` claire et configurable
- Analyse contextuelle basée sur les notes et les patterns
- Mapping automatique vers les rôles Korg (DRUM, BASS, ACC1-5)

### 📊 **Métriques Avancées**
- Scores de confiance pour la détection de basse
- Analyse de la monophonie améliorée
- Seuils configurables pour tous les critères d'audit

## Installation

```bash
pip install mido pyyaml
```

## Utilisation

### 1. Audit de fichiers MIDI

```bash
python midistyle_toolkit.py audit /chemin/vers/fichiers --config config_advanced.yaml
```

**Nouvelles fonctionnalités d'audit :**
- Validation automatique des fichiers
- Détection intelligente de la basse
- Logging détaillé du processus
- Statistiques en fin de traitement

### 2. Préparation de fichiers

```bash  
python midistyle_toolkit.py prepare fichier.mid --config config_advanced.yaml --out prepared.mid
```

**Améliorations de la préparation :**
- Mapping intelligent des canaux basé sur l'analyse des notes
- Gestion robuste du temps avec TimeTracker
- Préservation optionnelle du groove original
- Validation d'entrée et gestion d'erreurs

### 3. Construction de packs Korg

```bash
python midistyle_toolkit.py build-korg-pack /dossier/sections --config config_advanced.yaml
```

**Améliorations de la construction :**
- Validation de la structure des dossiers
- Comptage et rapport des sections trouvées
- Gestion d'erreurs pour fichiers corrompus
- Logging du processus de construction

## Configuration Avancée

Le fichier `config_advanced.yaml` inclut de nouvelles options :

```yaml
# Nouvelles options pour l'amélioration
prepare:
  smart_bass_detection: true      # Utilise la nouvelle détection de basse
  preserve_groove: true           # Quantification plus douce  
  auto_channel_mapping: true      # Mapping intelligent des canaux

# Nouveaux seuils pour la détection de basse
audit_thresholds:
  bass_detection_confidence: 3    # Score minimum pour considérer un canal comme basse
  bass_note_range_max: 24         # Gamme max pour une basse (demi-tons)
  bass_median_note_max: 55        # Note médiane max pour une basse

# Configuration du logging
logging:
  level: "INFO"                   # DEBUG, INFO, WARNING, ERROR
  show_progress: true             # Affiche le progrès lors du traitement
  detailed_bass_analysis: false   # Logs détaillés pour la détection de basse
```

## Architecture du Code

### Classes Principales

- **`TimeTracker`** : Gestion robuste du temps absolu/delta
- **`map_channel_to_role()`** : Mapping intelligent des canaux
- **`detect_bass_channel()`** : Détection sophistiquée de la basse
- **`validate_midi_file()`** : Validation des fichiers d'entrée

### Fonctions Améliorées

- **`audit_midi()`** : Analyse complète avec nouvelles métriques
- **`cmd_prepare()`** : Préparation avec mapping intelligent
- **`cmd_audit()`** : Audit avec logging et statistiques
- **`cmd_build_korg()`** : Construction avec validation

## Avantages des Améliorations

1. **Fiabilité** : Validation d'entrée et gestion d'erreurs robuste
2. **Précision** : Détection de basse et mapping de canaux plus intelligents  
3. **Maintenabilité** : Code mieux structuré avec classes et fonctions claires
4. **Observabilité** : Logging complet pour debug et suivi
5. **Configurabilité** : Paramètres avancés dans le fichier de configuration

## Compatibilité

- ✅ Compatible avec le code original
- ✅ Même interface CLI
- ✅ Mêmes fichiers de sortie
- ✅ Configuration étendue mais rétro-compatible

## Prochaines Améliorations Possibles

- Tests unitaires automatisés
- Interface graphique optionnelle  
- Support de formats MIDI étendus
- Analyse harmonique avancée
- Export vers d'autres formats d'arrangeurs