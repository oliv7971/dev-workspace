#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SMC PDF Generator - Génération de rapports PDF
Crée des rapports PDF à partir des données CSV extraites
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import numpy as np
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
import matplotlib.dates as mdates
import io
import base64

# Configuration matplotlib pour de meilleurs graphiques
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class SMCPDFGenerator:
    """Générateur de rapports PDF pour les données SMC"""
    
    def __init__(self, csv_folder: str, output_folder: str, month: str):
        self.csv_folder = Path(csv_folder)
        self.output_folder = Path(output_folder)
        self.month = month
        
        # Styles pour PDF
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.darkblue,
            spaceAfter=12,
            alignment=1  # Center
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.darkgreen,
            spaceAfter=6
        )

    def load_csv_data(self) -> Dict[str, pd.DataFrame]:
        """Charge les données depuis les fichiers CSV"""
        data = {}
        
        csv_files = {
            'dates': 'Dates_SMC.csv',
            'convergences': 'Convergences_SMC.csv',
            'deplacements': 'Deplacements_SMC.csv'
        }
        
        for key, filename in csv_files.items():
            file_path = self.csv_folder / filename
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path, encoding='utf-8-sig')
                    data[key] = df
                    print(f"✅ Chargé: {filename} ({len(df)} lignes)")
                except Exception as e:
                    print(f"❌ Erreur lecture {filename}: {e}")
                    data[key] = pd.DataFrame()
            else:
                print(f"⚠️ Fichier manquant: {filename}")
                data[key] = pd.DataFrame()
        
        return data

    def create_summary_table(self, df: pd.DataFrame, title: str) -> Table:
        """Crée un tableau de synthèse"""
        if df.empty:
            return Table([['Aucune donnée disponible']])
        
        # Grouper par galerie et section
        summary_data = []
        summary_data.append(['Galerie', 'Section', 'Métrique', 'Évolution mensuelle (mm)', 'Valeur cumulée (mm)'])
        
        for _, row in df.iterrows():
            galerie = row.get('galerie', 'N/A')
            section = row.get('section', 'N/A')
            metric = row.get('metric', 'N/A')
            periodic = row.get('periodic_mm', 'N/A')
            cumulative = row.get('cumulative_mm', 'N/A')
            
            # Formatage des valeurs
            if pd.notna(periodic) and periodic != 'N/A':
                periodic = f"{periodic:.2f}"
            if pd.notna(cumulative) and cumulative != 'N/A':
                cumulative = f"{cumulative:.2f}"
            
            summary_data.append([galerie, section, metric, periodic, cumulative])
        
        # Créer le tableau
        table = Table(summary_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table

    def create_evolution_chart(self, df: pd.DataFrame, chart_type: str) -> Optional[str]:
        """Crée un graphique d'évolution et retourne le chemin du fichier image"""
        if df.empty:
            return None
        
        try:
            # Configuration du graphique
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            fig.suptitle(f'Évolutions {chart_type} - {self.month}', fontsize=14, fontweight='bold')
            
            # Graphique 1: Évolutions mensuelles
            monthly_data = df[df['periodic_mm'].notna()]
            if not monthly_data.empty:
                galleries = monthly_data['galerie'].unique()
                x_pos = np.arange(len(monthly_data))
                
                bars1 = ax1.bar(x_pos, monthly_data['periodic_mm'], 
                               color=plt.cm.Set3(np.linspace(0, 1, len(monthly_data))))
                ax1.set_title('Évolutions Mensuelles (mm)')
                ax1.set_xlabel('Sections')
                ax1.set_ylabel('Évolution (mm)')
                ax1.tick_params(axis='x', rotation=45)
                
                # Étiquettes personnalisées
                labels = [f"{row['galerie']}\n{row['section']}\n{row['metric']}" 
                         for _, row in monthly_data.iterrows()]
                ax1.set_xticks(x_pos)
                ax1.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
                
                # Valeurs sur les barres
                for bar, value in zip(bars1, monthly_data['periodic_mm']):
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                            f'{value:.2f}', ha='center', va='bottom', fontsize=8)
            
            # Graphique 2: Valeurs cumulées
            cumulative_data = df[df['cumulative_mm'].notna()]
            if not cumulative_data.empty:
                x_pos2 = np.arange(len(cumulative_data))
                
                bars2 = ax2.bar(x_pos2, cumulative_data['cumulative_mm'],
                               color=plt.cm.Set2(np.linspace(0, 1, len(cumulative_data))))
                ax2.set_title('Valeurs Cumulées (mm)')
                ax2.set_xlabel('Sections')
                ax2.set_ylabel('Valeur cumulée (mm)')
                
                # Étiquettes personnalisées
                labels2 = [f"{row['galerie']}\n{row['section']}\n{row['metric']}" 
                          for _, row in cumulative_data.iterrows()]
                ax2.set_xticks(x_pos2)
                ax2.set_xticklabels(labels2, rotation=45, ha='right', fontsize=8)
                
                # Valeurs sur les barres
                for bar, value in zip(bars2, cumulative_data['cumulative_mm']):
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                            f'{value:.2f}', ha='center', va='bottom', fontsize=8)
            
            plt.tight_layout()
            
            # Sauvegarder l'image
            chart_path = self.output_folder / f"chart_{chart_type.lower()}_{self.month.replace('-', '_')}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"❌ Erreur création graphique {chart_type}: {e}")
            return None

    def generate_pdf_report(self) -> bool:
        """Génère le rapport PDF complet"""
        try:
            # Charger les données
            print("📊 Chargement des données CSV...")
            data = self.load_csv_data()
            
            # Créer le PDF
            pdf_path = self.output_folder / f"Rapport_SMC_{self.month.replace('-', '_')}.pdf"
            doc = SimpleDocTemplate(str(pdf_path), pagesize=landscape(A4),
                                  rightMargin=1*cm, leftMargin=1*cm,
                                  topMargin=1*cm, bottomMargin=1*cm)
            
            story = []
            
            # Titre principal
            title = Paragraph(f"Rapport SMC - Évolutions {self.month}", self.title_style)
            story.append(title)
            story.append(Spacer(1, 0.3*inch))
            
            # Informations générales
            info_text = f"""
            <b>Date de génération:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
            <b>Période analysée:</b> {self.month}<br/>
            <b>Nombre de fichiers traités:</b> {len(data.get('dates', pd.DataFrame()))} feuilles<br/>
            """
            story.append(Paragraph(info_text, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Section Convergences
            if not data['convergences'].empty:
                story.append(Paragraph("CONVERGENCES", self.heading_style))
                
                # Tableau convergences
                conv_table = self.create_summary_table(data['convergences'], 'Convergences')
                story.append(conv_table)
                story.append(Spacer(1, 0.2*inch))
                
                # Graphique convergences
                conv_chart = self.create_evolution_chart(data['convergences'], 'Convergences')
                if conv_chart and Path(conv_chart).exists():
                    story.append(Image(conv_chart, width=10*inch, height=4*inch))
                
                story.append(PageBreak())
            
            # Section Déplacements
            if not data['deplacements'].empty:
                story.append(Paragraph("DÉPLACEMENTS", self.heading_style))
                
                # Tableau déplacements
                depl_table = self.create_summary_table(data['deplacements'], 'Déplacements')
                story.append(depl_table)
                story.append(Spacer(1, 0.2*inch))
                
                # Graphique déplacements
                depl_chart = self.create_evolution_chart(data['deplacements'], 'Déplacements')
                if depl_chart and Path(depl_chart).exists():
                    story.append(Image(depl_chart, width=10*inch, height=4*inch))
            
            # Générer le PDF
            print("📄 Génération du PDF...")
            doc.build(story)
            
            print(f"✅ PDF généré: {pdf_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur génération PDF: {e}")
            return False

def generate_pdf_from_csv(csv_folder: str, output_folder: str, month: str, log_callback=None) -> bool:
    """Fonction principale pour générer un PDF depuis les CSV"""
    
    if log_callback:
        log_callback("📄 Génération du rapport PDF...")
    
    try:
        generator = SMCPDFGenerator(csv_folder, output_folder, month)
        success = generator.generate_pdf_report()
        
        if success and log_callback:
            log_callback("✅ Rapport PDF généré avec succès!")
        elif log_callback:
            log_callback("❌ Échec de la génération PDF")
        
        return success
        
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Erreur PDF: {str(e)}")
        return False

if __name__ == "__main__":
    # Test
    csv_folder = r"C:\temp\smc_output"
    output_folder = r"C:\temp\smc_output"
    month = "2025-08"
    
    generate_pdf_from_csv(csv_folder, output_folder, month)