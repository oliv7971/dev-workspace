#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface GUI pour le système unifié d'extraction SMC & Carrure
Version COMPLÈTE avec logique métier : dernières valeurs + valeurs périodiques + graphiques
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import re
from pathlib import Path

class UnifiedExtractionGui:
    def __init__(self, master):
        self.master = master
        master.title("🎯 Extracteur Unifié SMC & Carrure - Version COMPLÈTE")
        master.geometry("900x700")

        # Frame principal
        main_frame = ttk.Frame(master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === TITRE ET DESCRIPTION ===
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(title_frame, text="🎯 EXTRACTEUR UNIFIÉ SMC & CARRURE",
                 font=("Arial", 14, "bold")).pack()
        ttk.Label(title_frame, text="📊 Dernières valeurs cumulatives + 📈 Valeurs périodiques + 🎨 Graphiques par zones",
                 font=("Arial", 10)).pack()

        # === SECTION TYPE DE DONNÉES ===
        type_frame = ttk.LabelFrame(main_frame, text="🔍 Type de données à extraire", padding="10")
        type_frame.pack(fill=tk.X, pady=(0, 15))

        self.data_type_var = tk.StringVar(value="auto")

        ttk.Radiobutton(type_frame, text="🤖 Détection automatique (SMC + Carrure) [RECOMMANDÉ]",
                       variable=self.data_type_var, value="auto").pack(anchor=tk.W)
        ttk.Radiobutton(type_frame, text="🔧 SMC uniquement (convergences, déplacements)",
                       variable=self.data_type_var, value="smc").pack(anchor=tk.W)
        ttk.Radiobutton(type_frame, text="🏗️ Carrure uniquement (auscultation double carrure)",
                       variable=self.data_type_var, value="carrure").pack(anchor=tk.W)

        # === SECTION DOSSIER RACINE ===
        ttk.Label(main_frame, text="📁 Dossier racine des fichiers Excel:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 15))

        self.root_folder_entry = ttk.Entry(folder_frame, width=80)
        self.root_folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Pré-remplir avec le chemin septembre 2025
        default_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250902-rapport mensuel septembre\1-tableaux"
        self.root_folder_entry.insert(0, default_path)

        ttk.Button(folder_frame, text="📂 Parcourir", command=self.browse_root_folder).pack(side=tk.RIGHT)

        # === SECTION MOIS ===
        month_frame = ttk.Frame(main_frame)
        month_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(month_frame, text="📅 Mois à traiter (YYYY-MM):", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.month_entry = ttk.Entry(month_frame, width=15)
        self.month_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.month_entry.insert(0, "2025-09")

        ttk.Label(month_frame, text="⚠️ Calcul: Valeurs périodiques = Valeur mois - Valeur mois précédent",
                 font=("Arial", 9), foreground="blue").pack(side=tk.LEFT, padx=(20, 0))

        # === SECTION DOSSIER DE SORTIE ===
        ttk.Label(main_frame, text="💾 Dossier de sortie:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(0, 15))

        self.output_folder_entry = ttk.Entry(output_frame, width=80)
        self.output_folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.output_folder_entry.insert(0, r"C:\temp\extraction_unifiee_complete")

        ttk.Button(output_frame, text="📂 Parcourir", command=self.browse_output_folder).pack(side=tk.RIGHT)

        # === SECTION OPTIONS AVANCÉES ===
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Options d'extraction avancées", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 15))

        # Première ligne d'options
        options_row1 = ttk.Frame(options_frame)
        options_row1.pack(fill=tk.X, pady=(0, 5))

        self.generate_csv_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_row1, text="📊 Générer rapport CSV unifié", variable=self.generate_csv_var).pack(side=tk.LEFT)

        self.generate_graphs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_row1, text="📈 Générer graphiques par zones colorées", variable=self.generate_graphs_var).pack(side=tk.LEFT, padx=(20, 0))

        # Deuxième ligne d'options
        options_row2 = ttk.Frame(options_frame)
        options_row2.pack(fill=tk.X, pady=(0, 5))

        self.generate_ligne_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_row2, text="📝 Générer récapitulatifs en ligne", variable=self.generate_ligne_var).pack(side=tk.LEFT)

        self.separate_by_type_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_row2, text="📁 Séparer SMC et Carrure", variable=self.separate_by_type_var).pack(side=tk.LEFT, padx=(20, 0))

        # Troisième ligne - options métier
        options_row3 = ttk.Frame(options_frame)
        options_row3.pack(fill=tk.X)

        ttk.Label(options_row3, text="🎯 Extraction métier:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        ttk.Label(options_row3, text="✓ Dernières valeurs cumulatives  ✓ Valeurs périodiques mensuelles  ✓ Détection zones graphiques",
                 font=("Arial", 8), foreground="green").pack(side=tk.LEFT, padx=(10, 0))

        # === SECTION BOUTON ET PROGRESS ===
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        self.start_button = ttk.Button(button_frame, text="🚀 LANCER EXTRACTION COMPLÈTE", command=self.start_extraction)
        self.start_button.pack()

        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))

        # === SECTION LOGS DÉTAILLÉS ===
        ttk.Label(main_frame, text="📋 Logs d'exécution détaillés:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, height=20, font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def browse_root_folder(self):
        folder = filedialog.askdirectory(title="📁 Dossier racine des fichiers Excel")
        if folder:
            self.root_folder_entry.delete(0, tk.END)
            self.root_folder_entry.insert(0, folder)

    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="💾 Dossier de sortie")
        if folder:
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, folder)

    def log_message(self, message):
        """Ajoute un message dans la zone de log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.master.update_idletasks()

    def detect_file_types(self, root_folder: Path):
        """Détecte les types de fichiers présents"""
        smc_files = []
        carrure_files = []

        # Rechercher fichiers SMC
        for pattern in ["*SMC*.xlsx", "*SMC*.xlsm"]:
            smc_files.extend(list(root_folder.rglob(pattern)))

        # Rechercher fichiers Carrure
        for pattern in ["*carrure*.xlsx", "*carrure*.xlsm"]:
            carrure_files.extend(list(root_folder.rglob(pattern)))

        return smc_files, carrure_files

    def start_extraction(self):
        root_folder = self.root_folder_entry.get().strip()
        month = self.month_entry.get().strip()
        output_folder = self.output_folder_entry.get().strip()
        data_type = self.data_type_var.get()

        # Validation
        if not root_folder or not os.path.isdir(root_folder):
            messagebox.showerror("Erreur", "Dossier racine invalide.")
            return

        if not re.match(r'^\d{4}-\d{2}$', month):
            messagebox.showerror("Erreur", "Format mois invalide (YYYY-MM).")
            return

        # Créer le dossier de sortie
        try:
            os.makedirs(output_folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de créer le dossier: {e}")
            return

        # Désactiver le bouton
        self.start_button.config(state='disabled', text="🔄 Extraction en cours...")
        self.progress.start()

        self.log_text.delete(1.0, tk.END)
        self.log_message(f"🚀 DÉMARRAGE EXTRACTION UNIFIÉE COMPLÈTE")
        self.log_message(f"═══════════════════════════════════════")
        self.log_message(f"📁 Source: {root_folder}")
        self.log_message(f"📅 Mois: {month}")
        self.log_message(f"💾 Sortie: {output_folder}")
        self.log_message(f"🎯 Type: {data_type}")
        self.log_message(f"⚙️ Logique métier: Dernières valeurs + Valeurs périodiques + Graphiques")
        self.log_message("")

        def extraction_thread():
            try:
                root_path = Path(root_folder)
                output_path = Path(output_folder)

                # Détection des fichiers
                smc_files, carrure_files = self.detect_file_types(root_path)

                self.master.after(0, lambda: self.log_message(f"🔍 DÉTECTION FICHIERS:"))
                self.master.after(0, lambda: self.log_message(f"   📊 SMC: {len(smc_files)} fichiers"))
                for smc_file in smc_files:
                    self.master.after(0, lambda f=smc_file: self.log_message(f"      • {f.name}"))

                self.master.after(0, lambda: self.log_message(f"   🏗️ Carrure: {len(carrure_files)} fichiers"))
                for carrure_file in carrure_files:
                    self.master.after(0, lambda f=carrure_file: self.log_message(f"      • {f.name}"))
                self.master.after(0, lambda: self.log_message(""))

                # Options pour l'extraction
                options = {
                    'generate_csv': self.generate_csv_var.get(),
                    'generate_graphs': self.generate_graphs_var.get(),
                    'generate_ligne_summaries': self.generate_ligne_var.get(),
                    'separate_by_type': self.separate_by_type_var.get()
                }

                success = False

                # Lancer l'extraction unifiée
                self.master.after(0, lambda: self.log_message("🎯 === EXTRACTION UNIFIÉE ==="))

                try:
                    from unified_extractor import run_unified_extraction
                    success = run_unified_extraction(
                        root_folder,
                        month,
                        output_folder,
                        options,
                        lambda msg: self.master.after(0, lambda: self.log_message(msg))
                    )
                except ImportError as e:
                    self.master.after(0, lambda: self.log_message(f"❌ Module unifié manquant: {e}"))
                    self.master.after(0, lambda: self.log_message("🔄 Tentative avec modules séparés..."))

                    # Fallback vers modules séparés
                    success_smc = False
                    success_carrure = False

                    if (data_type in ["auto", "smc"]) and smc_files:
                        try:
                            from src.smc_evolutions import run_extraction
                            smc_output = output_path / "SMC" if self.separate_by_type_var.get() else output_path
                            smc_output.mkdir(exist_ok=True)
                            success_smc = run_extraction(root_folder, month, str(smc_output), options,
                                                       lambda msg: self.master.after(0, lambda: self.log_message(msg)))
                        except ImportError as e:
                            self.master.after(0, lambda: self.log_message(f"❌ Module SMC manquant: {e}"))

                    if (data_type in ["auto", "carrure"]) and carrure_files:
                        try:
                            from carrure_extractor import run_carrure_extraction
                            carrure_output = output_path / "CARRURE" if self.separate_by_type_var.get() else output_path
                            carrure_output.mkdir(exist_ok=True)
                            success_carrure = run_carrure_extraction(root_folder, month, str(carrure_output), options,
                                                                   lambda msg: self.master.after(0, lambda: self.log_message(msg)))
                        except ImportError as e:
                            self.master.after(0, lambda: self.log_message(f"❌ Module Carrure manquant: {e}"))

                    success = success_smc or success_carrure

                # Résultats finaux
                if success:
                    self.master.after(0, lambda: self.log_message(""))
                    self.master.after(0, lambda: self.log_message("✅ ═══ EXTRACTION UNIFIÉE TERMINÉE ═══"))
                    self.master.after(0, lambda: self.log_message("🎯 Données extraites:"))
                    self.master.after(0, lambda: self.log_message("   📊 Dernières valeurs cumulatives"))
                    self.master.after(0, lambda: self.log_message("   📈 Valeurs périodiques (mois - mois précédent)"))
                    if self.generate_graphs_var.get():
                        self.master.after(0, lambda: self.log_message("   🎨 Graphiques générés par zones colorées"))
                    self.master.after(0, lambda: self.log_message(f"💾 Fichiers sauvés dans: {output_folder}"))

                    self.master.after(0, lambda: messagebox.showinfo("✅ Extraction terminée",
                                     f"Extraction unifiée terminée avec succès!\n\n"
                                     f"📊 Dernières valeurs + Valeurs périodiques extraites\n"
                                     f"🎨 Graphiques générés par zones\n"
                                     f"💾 Résultats dans: {output_folder}"))
                else:
                    self.master.after(0, lambda: self.log_message("❌ Aucune extraction réussie"))
                    self.master.after(0, lambda: messagebox.showerror("Erreur", "Aucune extraction n'a réussi"))

            except Exception as e:
                error_msg = f"Erreur globale: {str(e)}"
                self.master.after(0, lambda: self.log_message(f"❌ {error_msg}"))
                self.master.after(0, lambda: messagebox.showerror("Erreur", error_msg))
                import traceback
                self.master.after(0, lambda: self.log_message(f"🔍 Détails: {traceback.format_exc()}"))
            finally:
                # Réactiver
                self.master.after(0, lambda: self.progress.stop())
                self.master.after(0, lambda: self.start_button.config(state='normal', text="🚀 LANCER EXTRACTION COMPLÈTE"))

        threading.Thread(target=extraction_thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = UnifiedExtractionGui(root)
    root.mainloop()
