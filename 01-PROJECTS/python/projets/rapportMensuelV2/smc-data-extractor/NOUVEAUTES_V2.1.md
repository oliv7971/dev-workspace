# SMC Data Extractor - Nouvelles fonctionnalités v2.1

## 🆕 Récapitulatifs en ligne

Nouvelle fonctionnalité ajoutée au SMC Data Extractor pour générer des récapitulatifs horizontaux de toutes les métriques par élément mesuré.

### ✨ Caractéristiques

- **Format horizontal** : Toutes les métriques d'un élément sur une seule ligne
- **Périodique et cumulé** : Distinction claire entre les évolutions mensuelles et les valeurs cumulées
- **Multi-format** : Sortie en texte (.txt) et CSV (.csv)
- **Intégration complète** : Disponible dans l'interface graphique et le code

### 📊 Exemple de sortie

```
GGS C007 (Convergences - périodique)
  BG:-1.11 | HG:-0.11 | HD:N/A | BD:-1.65 | LH:N/A | LB:-1.07

GGS C007 (Convergences - cumulé)
  BG:-35.04 | HG:-30.44 | HD:-9.72 | BD:-7.96 | LH:-10.64 | LB:-25.16

GGS C007 (Déplacements - périodique)
  DH BD:-0.77 | DH BG:0.30 | DPM BD:-1.18 | DPM BG:-1.02 | DZ BD:-0.20

GGS C007 (Déplacements - cumulé)
  DH BD:-13.46 | DH BG:11.63 | DPM BD:-2.60 | DPM BG:-6.30 | DZ BD:-8.20
```

### 📁 Fichiers générés

1. **`Recapitulatifs_Ligne_SMC_YYYY_MM.txt`** - Récapitulatif complet format texte
2. **`Convergences_Ligne_SMC_YYYY_MM.csv`** - Convergences en format CSV ligne
3. **`Deplacements_Ligne_SMC_YYYY_MM.csv`** - Déplacements en format CSV ligne

### 🚀 Utilisation

#### Interface graphique
- Cocher "Générer récapitulatifs en ligne" dans l'interface
- Lancer l'extraction normalement

#### Code Python
```python
options = {
    'generate_csv': True,
    'generate_ligne_summaries': True  # Nouvelle option
}
run_extraction(root_folder, month, output_folder, options)
```

#### Module dédié
```python
from ligne_summary_generator import generate_ligne_summaries
generate_ligne_summaries(csv_folder, output_folder, month)
```

### 🔧 Installation/Mise à jour

1. **Nouveaux utilisateurs** : Tous les fichiers sont déjà inclus
2. **Utilisateurs existants** : Exécuter `python update_recap_ligne.py`
3. **Test** : Exécuter `python demo_recap_ligne.py`

### 📚 Documentation

- **Guide complet** : `docs/recap_ligne_guide.md`
- **Démonstration** : `demo_recap_ligne.py`
- **Script de mise à jour** : `update_recap_ligne.py`

### 🔄 Compatibilité

- ✅ Compatible avec toutes les versions existantes
- ✅ Ne modifie pas les fonctionnalités existantes
- ✅ Ajout transparent d'options
- ✅ Activé par défaut, peut être désactivé

### 🎯 Avantages

1. **Lecture facilitée** : Format horizontal plus compact
2. **Import Excel direct** : CSV prêt pour Excel/Google Sheets
3. **Rapports de synthèse** : Format idéal pour les présentations
4. **Traçabilité** : Garde la distinction périodique/cumulé

### 📈 Types de données supportées

#### Convergences
- BG (Bas Gauche), HG (Haut Gauche), HD (Haut Droit)
- BD (Bas Droit), LH, LB

#### Déplacements
- **DPM** : Déplacements permanents (toutes positions)
- **DH** : Déplacements horizontaux (toutes positions)  
- **DZ** : Déplacements verticaux (toutes positions)

### 🔍 Format CSV détaillé

```csv
galerie,section,type,mode,BG,HG,HD,BD,LH,LB
GGS,C007,Convergences,périodique,-1.11,-0.11,,-1.65,,-1.07
GGS,C007,Convergences,cumulé,-35.04,-30.44,-9.72,-7.96,-10.64,-25.16
```

### ⚙️ Configuration

La fonctionnalité est activée par défaut. Pour la désactiver :

```python
options = {'generate_ligne_summaries': False}
```

---

## 📞 Support

- **Documentation** : Consulter `docs/recap_ligne_guide.md`
- **Démonstration** : Exécuter `demo_recap_ligne.py`
- **Test** : Exécuter `update_recap_ligne.py`

Cette nouvelle fonctionnalité enrichit le SMC Data Extractor sans affecter les fonctionnalités existantes, offrant une nouvelle perspective sur les données extraites.
