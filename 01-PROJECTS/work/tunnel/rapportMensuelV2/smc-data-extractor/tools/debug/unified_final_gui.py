#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface GUI Unifiée FINALE - Extracteurs SMC et Carrure
Logique métier précise implémentée selon les spécifications exactes
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import logging
from pathlib import Path
from datetime import datetime
import sys
import os

# Ajouter le chemin des extracteurs
sys.path.append(str(Path(__file__).parent))

# Import des extracteurs
try:
    from src.smc_evolutions import run_extraction as run_smc_extractions
    SMC_AVAILABLE = True
except ImportError as e:
    print(f"SMC non disponible: {e}")
    SMC_AVAILABLE = False

try:
    from carrure_precise_extractor import run_carrure_precise_extraction
    CARRURE_AVAILABLE = True
except ImportError as e:
    print(f"Carrure non disponible: {e}")
    CARRURE_AVAILABLE = False

class UnifiedFinalExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Extracteur Unifié FINAL - SMC & Carrure")
        self.root.geometry("900x700")

        # Variables
        self.root_folder_var = tk.StringVar()
        self.output_folder_var = tk.StringVar()
        self.month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        self.extract_smc_var = tk.BooleanVar(value=SMC_AVAILABLE)
        self.extract_carrure_var = tk.BooleanVar(value=CARRURE_AVAILABLE)

        # Setup logging
        self.setup_logging()

        # Créer l'interface
        self.create_widgets()

        # Définir les dossiers par défaut si possible
        self.set_default_folders()

    def setup_logging(self):
        """Configure le système de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def create_widgets(self):
        """Crée l'interface utilisateur"""

        # Frame principal avec scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Titre
        title_label = ttk.Label(main_frame, text="🎯 Extracteur Unifié FINAL",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Section Configuration
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))

        # Dossier racine
        ttk.Label(config_frame, text="📁 Dossier racine (contient les fichiers Excel):").pack(anchor=tk.W)
        folder_frame = ttk.Frame(config_frame)
        folder_frame.pack(fill=tk.X, pady=(5, 10))

        ttk.Entry(folder_frame, textvariable=self.root_folder_var, width=80).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="Parcourir", command=self.browse_root_folder).pack(side=tk.RIGHT, padx=(5, 0))

        # Dossier de sortie
        ttk.Label(config_frame, text="💾 Dossier de sortie:").pack(anchor=tk.W)
        output_frame = ttk.Frame(config_frame)
        output_frame.pack(fill=tk.X, pady=(5, 10))

        ttk.Entry(output_frame, textvariable=self.output_folder_var, width=80).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Parcourir", command=self.browse_output_folder).pack(side=tk.RIGHT, padx=(5, 0))

        # Mois cible
        ttk.Label(config_frame, text="📅 Mois cible (YYYY-MM):").pack(anchor=tk.W)
        month_frame = ttk.Frame(config_frame)
        month_frame.pack(fill=tk.X, pady=(5, 10))

        month_entry = ttk.Entry(month_frame, textvariable=self.month_var, width=15)
        month_entry.pack(side=tk.LEFT)

        # Bouton mois actuel
        current_month_btn = ttk.Button(month_frame, text="Mois actuel",
                                     command=self.set_current_month)
        current_month_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Section Types d'extraction
        extract_frame = ttk.LabelFrame(main_frame, text="🔧 Types d'extraction", padding="10")
        extract_frame.pack(fill=tk.X, pady=(0, 10))

        # SMC
        smc_frame = ttk.Frame(extract_frame)
        smc_frame.pack(fill=tk.X, pady=(0, 5))

        smc_cb = ttk.Checkbutton(smc_frame, text="📊 Extractions SMC",
                                variable=self.extract_smc_var,
                                state=tk.NORMAL if SMC_AVAILABLE else tk.DISABLED)
        smc_cb.pack(side=tk.LEFT)

        smc_status = "✅ Disponible" if SMC_AVAILABLE else "❌ Module non trouvé"
        ttk.Label(smc_frame, text=smc_status,
                 foreground="green" if SMC_AVAILABLE else "red").pack(side=tk.LEFT, padx=(10, 0))

        # Carrure
        carrure_frame = ttk.Frame(extract_frame)
        carrure_frame.pack(fill=tk.X, pady=(0, 5))

        carrure_cb = ttk.Checkbutton(carrure_frame, text="🏗️ Extractions Carrure (logique métier précise)",
                                    variable=self.extract_carrure_var,
                                    state=tk.NORMAL if CARRURE_AVAILABLE else tk.DISABLED)
        carrure_cb.pack(side=tk.LEFT)

        carrure_status = "✅ Disponible" if CARRURE_AVAILABLE else "❌ Module non trouvé"
        ttk.Label(carrure_frame, text=carrure_status,
                 foreground="green" if CARRURE_AVAILABLE else "red").pack(side=tk.LEFT, padx=(10, 0))

        # Section Logique métier carrure
        logic_frame = ttk.LabelFrame(main_frame, text="🧠 Logique Métier Carrure Implémentée", padding="10")
        logic_frame.pack(fill=tk.X, pady=(0, 10))

        logic_text = """✅ Structure Excel: En-têtes lignes 8,9,10 + 2 tableaux distincts (GGS: A-AE, GVA: AH-BL)
✅ Déplacements CUMULÉS = Dernière valeur mesurée (toutes périodes)
✅ Déplacements PÉRIODIQUES = Dernière mois - Dernière avant mois
✅ Règle 6 mois: Si dernière avant mois > 6 mois → périodique = vide
✅ Gestion des valeurs manquantes et erreurs Excel (#N/A, etc.)"""

        ttk.Label(logic_frame, text=logic_text, justify=tk.LEFT).pack(anchor=tk.W)

        # Section Actions
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))

        # Bouton d'extraction
        self.extract_btn = ttk.Button(action_frame, text="🚀 Lancer l'Extraction",
                                     command=self.start_extraction, style="Accent.TButton")
        self.extract_btn.pack(side=tk.LEFT)

        # Barre de progression
        self.progress = ttk.Progressbar(action_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # Zone de logs
        log_frame = ttk.LabelFrame(main_frame, text="📋 Logs d'exécution", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Boutons de log
        log_btn_frame = ttk.Frame(log_frame)
        log_btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(log_btn_frame, text="Effacer logs", command=self.clear_logs).pack(side=tk.LEFT)
        ttk.Button(log_btn_frame, text="Sauver logs", command=self.save_logs).pack(side=tk.LEFT, padx=(5, 0))

    def set_default_folders(self):
        """Définit les dossiers par défaut"""

        # Dossier racine par défaut (depuis le chemin de test)
        default_root = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité"
        if Path(default_root).exists():
            self.root_folder_var.set(default_root)

        # Dossier de sortie par défaut
        default_output = Path.home() / "Documents" / "Extractions_Automatiques"
        self.output_folder_var.set(str(default_output))

    def browse_root_folder(self):
        """Sélectionne le dossier racine"""
        folder = filedialog.askdirectory(
            title="Sélectionner le dossier racine contenant les fichiers Excel",
            initialdir=self.root_folder_var.get() or "."
        )
        if folder:
            self.root_folder_var.set(folder)

    def browse_output_folder(self):
        """Sélectionne le dossier de sortie"""
        folder = filedialog.askdirectory(
            title="Sélectionner le dossier de sortie",
            initialdir=self.output_folder_var.get() or "."
        )
        if folder:
            self.output_folder_var.set(folder)

    def set_current_month(self):
        """Définit le mois actuel"""
        self.month_var.set(datetime.now().strftime("%Y-%m"))

    def log_message(self, message):
        """Ajoute un message aux logs"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_logs(self):
        """Efface les logs"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def save_logs(self):
        """Sauvegarde les logs"""
        content = self.log_text.get(1.0, tk.END)
        if content.strip():
            file_path = filedialog.asksaveasfilename(
                title="Sauvegarder les logs",
                defaultextension=".txt",
                filetypes=[("Fichiers texte", "*.txt"), ("Tous fichiers", "*.*")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log_message(f"💾 Logs sauvés: {Path(file_path).name}")

    def validate_inputs(self):
        """Valide les paramètres d'entrée"""
        errors = []

        # Vérifier dossier racine
        root_folder = self.root_folder_var.get().strip()
        if not root_folder:
            errors.append("Dossier racine requis")
        elif not Path(root_folder).exists():
            errors.append("Dossier racine introuvable")

        # Vérifier dossier sortie
        output_folder = self.output_folder_var.get().strip()
        if not output_folder:
            errors.append("Dossier de sortie requis")

        # Vérifier format mois
        month = self.month_var.get().strip()
        if not month:
            errors.append("Mois cible requis")
        else:
            try:
                year, month_num = month.split('-')
                int(year)
                int(month_num)
                if not (1 <= int(month_num) <= 12):
                    errors.append("Mois invalide (01-12)")
            except:
                errors.append("Format mois invalide (YYYY-MM)")

        # Vérifier qu'au moins un type d'extraction est sélectionné
        if not (self.extract_smc_var.get() or self.extract_carrure_var.get()):
            errors.append("Sélectionner au moins un type d'extraction")

        return errors

    def start_extraction(self):
        """Lance l'extraction en arrière-plan"""

        # Validation
        errors = self.validate_inputs()
        if errors:
            messagebox.showerror("Erreurs de validation", "\n".join(errors))
            return

        # Désactiver le bouton et démarrer la progression
        self.extract_btn.config(state=tk.DISABLED)
        self.progress.start()

        # Lancer en thread
        thread = threading.Thread(target=self.run_extraction)
        thread.daemon = True
        thread.start()

    def run_extraction(self):
        """Exécute l'extraction"""

        try:
            root_folder = self.root_folder_var.get().strip()
            output_folder = self.output_folder_var.get().strip()
            month = self.month_var.get().strip()

            self.log_message("🚀 Début de l'extraction unifiée")
            self.log_message(f"📁 Dossier racine: {root_folder}")
            self.log_message(f"💾 Dossier sortie: {output_folder}")
            self.log_message(f"📅 Mois cible: {month}")

            # Créer le dossier de sortie
            Path(output_folder).mkdir(parents=True, exist_ok=True)

            success_count = 0
            total_count = 0

            # Extraction SMC
            if self.extract_smc_var.get() and SMC_AVAILABLE:
                self.log_message("\n📊 === EXTRACTION SMC ===")
                total_count += 1
                try:
                    smc_success = run_smc_extractions(
                        root_folder=root_folder,
                        month=month,
                        output_folder=output_folder,
                        log_callback=self.log_message
                    )
                    if smc_success:
                        success_count += 1
                        self.log_message("✅ Extraction SMC terminée avec succès")
                    else:
                        self.log_message("❌ Échec extraction SMC")
                except Exception as e:
                    self.log_message(f"❌ Erreur extraction SMC: {e}")

            # Extraction Carrure
            if self.extract_carrure_var.get() and CARRURE_AVAILABLE:
                self.log_message("\n🏗️ === EXTRACTION CARRURE ===")
                total_count += 1
                try:
                    carrure_success = run_carrure_precise_extraction(
                        root_folder=root_folder,
                        month=month,
                        output_folder=output_folder,
                        log_callback=self.log_message
                    )
                    if carrure_success:
                        success_count += 1
                        self.log_message("✅ Extraction Carrure terminée avec succès")
                    else:
                        self.log_message("❌ Échec extraction Carrure")
                except Exception as e:
                    self.log_message(f"❌ Erreur extraction Carrure: {e}")

            # Résumé final
            self.log_message(f"\n🎯 === RÉSUMÉ FINAL ===")
            self.log_message(f"✅ Extractions réussies: {success_count}/{total_count}")

            if success_count == total_count:
                self.log_message("🎉 Toutes les extractions ont réussi !")
                self.show_success_message(output_folder)
            else:
                self.log_message("⚠️ Certaines extractions ont échoué")

        except Exception as e:
            self.log_message(f"❌ Erreur critique: {e}")
            import traceback
            self.log_message(f"📋 Détails: {traceback.format_exc()}")

        finally:
            # Réactiver l'interface
            self.root.after(0, self.extraction_finished)

    def extraction_finished(self):
        """Appelé quand l'extraction est terminée"""
        self.progress.stop()
        self.extract_btn.config(state=tk.NORMAL)

    def show_success_message(self, output_folder):
        """Affiche un message de succès avec option d'ouvrir le dossier"""
        def open_folder():
            os.startfile(output_folder)

        response = messagebox.askquestion(
            "Extraction terminée",
            f"Toutes les extractions ont réussi !\n\nOuvrir le dossier de sortie ?\n{output_folder}",
            icon='question'
        )
        if response == 'yes':
            open_folder()

def main():
    """Fonction principale"""
    root = tk.Tk()

    # Configuration du style
    style = ttk.Style()
    style.theme_use('winnative' if os.name == 'nt' else 'clam')

    app = UnifiedFinalExtractorGUI(root)

    # Centrer la fenêtre
    root.eval('tk::PlaceWindow . center')

    root.mainloop()

if __name__ == "__main__":
    main()
