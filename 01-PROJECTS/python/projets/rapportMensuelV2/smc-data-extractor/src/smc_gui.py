import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import re

class SMCGui:
    def __init__(self, master):
        self.master = master
        master.title("SMC Data Extractor")
        master.geometry("700x500")

        # Frame principal
        main_frame = ttk.Frame(master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Dossier racine
        ttk.Label(main_frame, text="Dossier racine des fichiers SMC:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 15))

        self.root_folder_entry = ttk.Entry(folder_frame, width=60)
        self.root_folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Pré-remplir avec le chemin de base plus générique
        default_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025"
        self.root_folder_entry.insert(0, default_path)

        ttk.Button(folder_frame, text="Parcourir", command=self.browse_root_folder).pack(side=tk.RIGHT)

        # Mois
        ttk.Label(main_frame, text="Mois à traiter (YYYY-MM):", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.month_entry = ttk.Entry(main_frame, width=15)
        self.month_entry.pack(anchor=tk.W, pady=(0, 15))
        self.month_entry.insert(0, "2025-09")  # Mois plus récent

        # Dossier de sortie
        ttk.Label(main_frame, text="Dossier de sortie:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(0, 15))

        self.output_folder_entry = ttk.Entry(output_frame, width=60)
        self.output_folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.output_folder_entry.insert(0, r"C:\temp\smc_output")

        ttk.Button(output_frame, text="Parcourir", command=self.browse_output_folder).pack(side=tk.RIGHT)

        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 15))

        self.generate_csv_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Générer CSV (DEBUG MODE)", variable=self.generate_csv_var).pack(anchor=tk.W)

        self.generate_ligne_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Générer récapitulatifs en ligne", variable=self.generate_ligne_var).pack(anchor=tk.W)

        # Bouton
        self.start_button = ttk.Button(main_frame, text="🚀 Démarrer l'extraction DEBUG", command=self.start_extraction)
        self.start_button.pack(pady=20)

        # Barre de progression
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))

        # Zone de log
        ttk.Label(main_frame, text="Logs d'exécution:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, height=15, font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def browse_root_folder(self):
        folder = filedialog.askdirectory(title="Dossier racine SMC")
        if folder:
            self.root_folder_entry.delete(0, tk.END)
            self.root_folder_entry.insert(0, folder)

    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Dossier de sortie")
        if folder:
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, folder)

    def log_message(self, message):
        """Ajoute un message dans la zone de log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.master.update_idletasks()

    def start_extraction(self):
        root_folder = self.root_folder_entry.get().strip()
        month = self.month_entry.get().strip()
        output_folder = self.output_folder_entry.get().strip()

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
        self.start_button.config(state='disabled', text="🔄 Analyse en cours...")
        self.progress.start()

        self.log_text.delete(1.0, tk.END)
        self.log_message(f"🚀 Démarrage extraction SMC DEBUG...")
        self.log_message(f"📁 Source: {root_folder}")
        self.log_message(f"📅 Mois: {month}")
        self.log_message(f"💾 Sortie: {output_folder}")
        self.log_message(f"")

        def extraction_thread():
            try:
                # VRAIE EXTRACTION ICI
                from smc_evolutions import run_extraction

                options = {
                    'generate_csv': self.generate_csv_var.get(),
                    'generate_pdf': False,
                    'generate_ligne_summaries': self.generate_ligne_var.get()
                }
                success = run_extraction(root_folder, month, output_folder, options, self.log_message)

                if success:
                    self.master.after(0, lambda: self.log_message(""))
                    self.master.after(0, lambda: self.log_message("✅ ANALYSE DEBUG TERMINÉE"))
                    self.master.after(0, lambda: messagebox.showinfo("Analyse terminée", "Consultez les logs pour voir la structure des fichiers"))
                else:
                    self.master.after(0, lambda: self.log_message("❌ Échec de l'analyse"))
                    self.master.after(0, lambda: messagebox.showerror("Erreur", "Échec de l'analyse"))

            except ImportError as e:
                error_msg = f"Module smc_evolutions manquant: {e}"
                self.master.after(0, lambda: self.log_message(f"❌ {error_msg}"))
                self.master.after(0, lambda: messagebox.showerror("Erreur", error_msg))
            except Exception as e:
                error_msg = f"Erreur: {str(e)}"
                self.master.after(0, lambda: self.log_message(f"❌ {error_msg}"))
                self.master.after(0, lambda: messagebox.showerror("Erreur", error_msg))
            finally:
                # Réactiver
                self.master.after(0, lambda: self.progress.stop())
                self.master.after(0, lambda: self.start_button.config(state='normal', text="🚀 Démarrer l'extraction DEBUG"))

        threading.Thread(target=extraction_thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = SMCGui(root)
    root.mainloop()
