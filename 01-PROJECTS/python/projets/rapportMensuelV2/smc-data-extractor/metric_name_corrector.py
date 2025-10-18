#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SMC Metric Name Corrector - Correcteur automatique des noms de métriques
Corrige les erreurs de nommage récurrentes dans les fichiers sources Excel
"""

import pandas as pd
from typing import Dict, List
import re

class MetricNameCorrector:
    """Correcteur automatique des noms de métriques SMC"""
    
    def __init__(self):
        # Dictionnaire des corrections automatiques
        self.corrections = {
            # Corrections spécifiques pour les erreurs récurrentes
            'DH bas droit': self._detect_correct_dh_name,  # Fonction dynamique
            
            # Corrections directes
            'DH bas droite': 'DH bas droit',
            'DH haut droite': 'DH haut droit',
            'DH bas gauche ': 'DH bas gauche',  # Espace en trop
            'DH haut gauche ': 'DH haut gauche',
            'DPM bas droite': 'DPM bas droit',
            'DPM haut droite': 'DPM haut droit',
            'DZ bas droite': 'DZ bas droit',
            'DZ haut droite': 'DZ haut droit',
            
            # Corrections de casse
            'dh bas gauche': 'DH bas gauche',
            'dh haut gauche': 'DH haut gauche',
            'dh bas droit': 'DH bas droit',
            'dh haut droit': 'DH haut droit',
            'dpm bas gauche': 'DPM bas gauche',
            'dpm haut gauche': 'DPM haut gauche',
            'dpm bas droit': 'DPM bas droit',
            'dpm haut droit': 'DPM haut droit',
            
            # Corrections d'espaces et caractères
            'DH  bas gauche': 'DH bas gauche',  # Double espace
            'DH  haut gauche': 'DH haut gauche',
            'DH\tbas gauche': 'DH bas gauche',  # Tabulation
            'DH\thaut gauche': 'DH haut gauche',
        }
        
        # Pattern pour détecter les métriques de type DH/DPM/DZ
        self.metric_pattern = re.compile(r'^(DH|DPM|DZ)\s+(bas|haut|centre)\s+(gauche|droit)$', re.IGNORECASE)
    
    def _detect_correct_dh_name(self, metric_name: str, context_metrics: List[str]) -> str:
        """
        Détecte le bon nom pour 'DH bas droit' en analysant le contexte
        Logique améliorée : si on a DPM haut droit et DZ haut droit dans le même contexte,
        alors DH bas droit devrait probablement être DH haut droit.
        """
        # Vérifier s'il y a une incohérence contextuelle
        has_dpm_haut_droit = 'DPM haut droit' in context_metrics
        has_dz_haut_droit = 'DZ haut droit' in context_metrics
        has_dh_haut_droit = 'DH haut droit' in context_metrics
        
        # Pattern d'incohérence : DPM haut droit + DZ haut droit mais DH bas droit
        if has_dpm_haut_droit and has_dz_haut_droit and not has_dh_haut_droit:
            # Le DH devrait probablement être "haut droit" pour être cohérent
            return 'DH haut droit'
        
        # Vérifier les doublons dans le contexte (logique originale)
        dh_bas_droit_count = context_metrics.count('DH bas droit')
        
        # Si c'est la première occurrence et pas d'incohérence détectée, c'est probablement correct
        if dh_bas_droit_count <= 1:
            return 'DH bas droit'
        
        # Si c'est une occurrence supplémentaire, c'est probablement 'DH haut droit'
        # Vérifier qu'on n'a pas déjà 'DH haut droit'
        if not has_dh_haut_droit:
            return 'DH haut droit'
        
        # En cas de doute, garder l'original avec un suffixe
        return f'DH bas droit_{dh_bas_droit_count}'
    
    def correct_metric_name(self, metric_name: str, context_metrics: List[str] = None) -> str:
        """
        Corrige un nom de métrique individuel
        
        Args:
            metric_name: Le nom de la métrique à corriger
            context_metrics: Liste des autres métriques dans le même contexte
            
        Returns:
            Le nom corrigé
        """
        if not metric_name or pd.isna(metric_name):
            return metric_name
        
        # Nettoyer les espaces en début/fin
        cleaned = str(metric_name).strip()
        
        # Vérifier les corrections directes
        if cleaned in self.corrections:
            correction = self.corrections[cleaned]
            
            # Si c'est une fonction (cas spécial)
            if callable(correction):
                return correction(cleaned, context_metrics or [])
            else:
                return correction
        
        # Vérification avec regex pour les cas non mappés
        match = self.metric_pattern.match(cleaned)
        if match:
            prefix, position, side = match.groups()
            # Reconstruire avec la casse correcte
            corrected = f"{prefix.upper()} {position.lower()} {side.lower()}"
            return corrected
        
        # Retourner l'original si aucune correction n'est nécessaire
        return cleaned
    
    def correct_dataframe_metrics(self, df: pd.DataFrame, metric_column: str = 'metric') -> pd.DataFrame:
        """
        Corrige les noms de métriques dans un DataFrame
        
        Args:
            df: DataFrame contenant les données
            metric_column: Nom de la colonne contenant les métriques
            
        Returns:
            DataFrame avec les métriques corrigées
        """
        if metric_column not in df.columns:
            print(f"⚠️ Colonne '{metric_column}' non trouvée")
            return df
        
        # Créer une copie pour éviter de modifier l'original
        df_corrected = df.copy()
        
        # Grouper par contexte (galerie + section) pour analyser les doublons
        corrections_applied = 0
        
        if 'galerie' in df.columns and 'section' in df.columns:
            # Correction contextuelle par galerie/section
            for (galerie, section), group in df.groupby(['galerie', 'section']):
                context_metrics = group[metric_column].tolist()
                corrected_metrics = []
                
                for metric in context_metrics:
                    corrected = self.correct_metric_name(metric, context_metrics)
                    corrected_metrics.append(corrected)
                    
                    if corrected != metric:
                        corrections_applied += 1
                        print(f"🔧 Correction: '{metric}' → '{corrected}' ({galerie} {section})")
                
                # Appliquer les corrections au DataFrame
                mask = (df_corrected['galerie'] == galerie) & (df_corrected['section'] == section)
                df_corrected.loc[mask, metric_column] = corrected_metrics
        else:
            # Correction simple sans contexte
            for idx, metric in df[metric_column].items():
                corrected = self.correct_metric_name(metric)
                if corrected != metric:
                    df_corrected.loc[idx, metric_column] = corrected
                    corrections_applied += 1
                    print(f"🔧 Correction: '{metric}' → '{corrected}'")
        
        if corrections_applied > 0:
            print(f"✅ {corrections_applied} corrections appliquées")
        else:
            print("✅ Aucune correction nécessaire")
        
        return df_corrected
    
    def analyze_duplicates(self, df: pd.DataFrame, metric_column: str = 'metric') -> Dict:
        """
        Analyse les doublons de métriques dans le DataFrame
        
        Returns:
            Dictionnaire avec les statistiques des doublons
        """
        analysis = {
            'duplicates_found': [],
            'suspicious_patterns': [],
            'total_duplicates': 0
        }
        
        if 'galerie' in df.columns and 'section' in df.columns:
            # Analyser par contexte
            for (galerie, section), group in df.groupby(['galerie', 'section']):
                metrics = group[metric_column].tolist()
                metric_counts = pd.Series(metrics).value_counts()
                
                duplicates = metric_counts[metric_counts > 1]
                if not duplicates.empty:
                    for metric, count in duplicates.items():
                        analysis['duplicates_found'].append({
                            'galerie': galerie,
                            'section': section,
                            'metric': metric,
                            'count': count
                        })
                        analysis['total_duplicates'] += count - 1
                        
                        # Détecter les patterns suspects
                        if 'bas droit' in metric and any('haut droit' in m for m in metrics):
                            analysis['suspicious_patterns'].append({
                                'galerie': galerie,
                                'section': section,
                                'issue': f"Possiblement '{metric}' au lieu de 'DH haut droit'"
                            })
        
        return analysis

def correct_csv_files(input_file: str, output_file: str = None) -> bool:
    """
    Fonction utilitaire pour corriger un fichier CSV
    
    Args:
        input_file: Chemin vers le fichier CSV d'entrée
        output_file: Chemin vers le fichier CSV de sortie (optionnel)
        
    Returns:
        True si la correction a réussi
    """
    try:
        print(f"🔄 Correction du fichier: {input_file}")
        
        # Charger le CSV
        df = pd.read_csv(input_file, sep=';', encoding='utf-8-sig')
        
        # Analyser les doublons avant correction
        corrector = MetricNameCorrector()
        analysis = corrector.analyze_duplicates(df)
        
        if analysis['total_duplicates'] > 0:
            print(f"⚠️ {analysis['total_duplicates']} doublons détectés avant correction")
            for duplicate in analysis['duplicates_found']:
                print(f"   - {duplicate['galerie']} {duplicate['section']}: {duplicate['metric']} (×{duplicate['count']})")
        
        # Appliquer les corrections
        df_corrected = corrector.correct_dataframe_metrics(df)
        
        # Analyser après correction
        analysis_after = corrector.analyze_duplicates(df_corrected)
        
        # Sauvegarder
        if output_file is None:
            output_file = input_file  # Écraser l'original
        
        df_corrected.to_csv(output_file, sep=';', index=False, encoding='utf-8-sig')
        
        print(f"✅ Fichier corrigé sauvegardé: {output_file}")
        
        if analysis_after['total_duplicates'] > 0:
            print(f"⚠️ {analysis_after['total_duplicates']} doublons restants après correction")
        else:
            print("✅ Tous les doublons ont été corrigés")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        return False

if __name__ == "__main__":
    # Test avec vos fichiers d'exemple
    import sys
    from pathlib import Path
    
    examples_dir = Path(__file__).parent / "examples" / "format_apres"
    deplacements_file = examples_dir / "Deplacements_SMC.csv"
    
    if deplacements_file.exists():
        print("🧪 Test de correction sur le fichier d'exemple...")
        correct_csv_files(str(deplacements_file))
    else:
        print("❌ Fichier d'exemple non trouvé")