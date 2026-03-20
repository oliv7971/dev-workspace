"""
Fenêtre du mode automatique pour PA4x Set Merger
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, List
import threading

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.merger.auto_scanner import (
    AutoScanner, GroupingStrategy, ScanResult, SetGenerationPlan
)


class AutoModeWindow(tk.Toplevel):
    """Fenêtre pour le mode automatique"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Mode Automatique - PA4x Set Merger")
        self.geometry("900x700")
        self.minsize(700, 500)
        self.transient(parent)
        
        self.scanner = AutoScanner()
        self.scan_result: Optional[ScanResult] = None
        self.plans: List[SetGenerationPlan] = []
        
        self._create_widgets()
        
        # Centrer
        self.geometry(f"+{parent.winfo_x() + 50}+{parent.winfo_y() + 30}")
    
    def _create_widgets(self):
        """Crée les widgets de l'interface"""
        
        # === Section Configuration ===
        config_frame = ttk.LabelFrame(self, text="📁 Configuration", padding=10)
        config_frame.pack(fill='x', padx=10, pady=5)
        
        # Chemin source
        source_frame = ttk.Frame(config_frame)
        source_frame.pack(fill='x', pady=2)
        
        ttk.Label(source_frame, text="Dossier source:").pack(side='left')
        self.source_var = tk.StringVar()
        self.source_entry = ttk.Entry(source_frame, textvariable=self.source_var, width=60)
        self.source_entry.pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(source_frame, text="📂", width=3, command=self._browse_source).pack(side='left')
        
        # Chemin destination
        dest_frame = ttk.Frame(config_frame)
        dest_frame.pack(fill='x', pady=2)
        
        ttk.Label(dest_frame, text="Dossier destination:").pack(side='left')
        self.dest_var = tk.StringVar()
        self.dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_var, width=60)
        self.dest_entry.pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(dest_frame, text="📂", width=3, command=self._browse_dest).pack(side='left')
        
        # Options
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(fill='x', pady=5)
        
        # Stratégie
        ttk.Label(options_frame, text="Stratégie:").pack(side='left')
        self.strategy_var = tk.StringVar(value="smart")
        strategy_combo = ttk.Combobox(
            options_frame, 
            textvariable=self.strategy_var,
            values=[
                ("smart", "🧠 Intelligent (détection auto)"),
                ("by_folder", "📁 Un SET par dossier"),
                ("by_parent", "📂 Regrouper par dossier parent"),
                ("by_prefix", "🔤 Regrouper par préfixe"),
                ("single_set", "📦 Tout en un seul SET")
            ],
            state='readonly',
            width=35
        )
        strategy_combo['values'] = [
            "🧠 Intelligent (détection auto)",
            "📁 Un SET par dossier",
            "📂 Regrouper par dossier parent", 
            "🔤 Regrouper par préfixe",
            "📦 Tout en un seul SET"
        ]
        strategy_combo.current(0)
        strategy_combo.pack(side='left', padx=10)
        
        # Checkbox récursif
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame, 
            text="🔄 Récursif (sous-dossiers)",
            variable=self.recursive_var
        ).pack(side='left', padx=10)
        
        # Checkbox inclure SET existants
        self.include_sets_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="📥 Inclure SET existants",
            variable=self.include_sets_var
        ).pack(side='left', padx=10)
        
        # Bouton Scanner
        scan_btn_frame = ttk.Frame(config_frame)
        scan_btn_frame.pack(fill='x', pady=10)
        
        self.scan_btn = ttk.Button(
            scan_btn_frame, 
            text="🔍 Scanner le dossier",
            command=self._start_scan
        )
        self.scan_btn.pack(side='left', padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            scan_btn_frame, 
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        self.progress_bar.pack(side='left', padx=10, fill='x', expand=True)
        
        self.progress_label = ttk.Label(scan_btn_frame, text="")
        self.progress_label.pack(side='left', padx=5)
        
        # === Section Résultats du scan ===
        results_frame = ttk.LabelFrame(self, text="📊 Résultats du scan", padding=10)
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Statistiques
        stats_frame = ttk.Frame(results_frame)
        stats_frame.pack(fill='x', pady=5)
        
        self.stats_label = ttk.Label(
            stats_frame, 
            text="Lancez un scan pour voir les résultats",
            font=('Helvetica', 10)
        )
        self.stats_label.pack(side='left')
        
        # Liste des plans de génération
        plans_frame = ttk.Frame(results_frame)
        plans_frame.pack(fill='both', expand=True, pady=5)
        
        # Treeview pour les plans
        columns = ('name', 'favorites', 'users', 'source', 'output')
        self.plans_tree = ttk.Treeview(plans_frame, columns=columns, show='headings', height=15)
        
        self.plans_tree.heading('name', text='Nom du SET')
        self.plans_tree.heading('favorites', text='Favorites')
        self.plans_tree.heading('users', text='Users')
        self.plans_tree.heading('source', text='Source')
        self.plans_tree.heading('output', text='Destination')
        
        self.plans_tree.column('name', width=150)
        self.plans_tree.column('favorites', width=70, anchor='center')
        self.plans_tree.column('users', width=60, anchor='center')
        self.plans_tree.column('source', width=200)
        self.plans_tree.column('output', width=200)
        
        # Scrollbars
        yscroll = ttk.Scrollbar(plans_frame, orient='vertical', command=self.plans_tree.yview)
        xscroll = ttk.Scrollbar(plans_frame, orient='horizontal', command=self.plans_tree.xview)
        self.plans_tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        
        self.plans_tree.pack(side='left', fill='both', expand=True)
        yscroll.pack(side='right', fill='y')
        
        # Détails du plan sélectionné
        details_frame = ttk.LabelFrame(results_frame, text="📋 Détails", padding=5)
        details_frame.pack(fill='x', pady=5)
        
        self.details_text = tk.Text(details_frame, height=6, font=('Consolas', 9))
        self.details_text.pack(fill='x')
        
        self.plans_tree.bind('<<TreeviewSelect>>', self._on_plan_select)
        
        # === Section Actions ===
        action_frame = ttk.Frame(self)
        action_frame.pack(fill='x', padx=10, pady=10)
        
        # Boutons
        self.preview_btn = ttk.Button(
            action_frame,
            text="👁 Prévisualiser",
            command=self._preview,
            state='disabled'
        )
        self.preview_btn.pack(side='left', padx=5)
        
        self.generate_btn = ttk.Button(
            action_frame,
            text="🚀 Générer les SET",
            command=self._generate,
            state='disabled'
        )
        self.generate_btn.pack(side='left', padx=5)
        
        self.generate_selected_btn = ttk.Button(
            action_frame,
            text="✅ Générer sélection",
            command=self._generate_selected,
            state='disabled'
        )
        self.generate_selected_btn.pack(side='left', padx=5)
        
        ttk.Button(
            action_frame,
            text="❌ Fermer",
            command=self.destroy
        ).pack(side='right', padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(self, text="📝 Journal", padding=5)
        log_frame.pack(fill='x', padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=4, font=('Consolas', 9))
        self.log_text.pack(fill='x')
        self.log_text.configure(state='disabled')
    
    def _browse_source(self):
        """Sélectionne le dossier source"""
        folder = filedialog.askdirectory(title="Sélectionner le dossier source")
        if folder:
            self.source_var.set(folder)
    
    def _browse_dest(self):
        """Sélectionne le dossier destination"""
        folder = filedialog.askdirectory(title="Sélectionner le dossier destination")
        if folder:
            self.dest_var.set(folder)
    
    def _log(self, message: str):
        """Ajoute un message au log"""
        self.log_text.configure(state='normal')
        self.log_text.insert('end', f"{message}\n")
        self.log_text.see('end')
        self.log_text.configure(state='disabled')
    
    def _get_strategy(self) -> GroupingStrategy:
        """Retourne la stratégie sélectionnée"""
        idx = [
            "🧠 Intelligent (détection auto)",
            "📁 Un SET par dossier",
            "📂 Regrouper par dossier parent",
            "🔤 Regrouper par préfixe",
            "📦 Tout en un seul SET"
        ].index(self.strategy_var.get()) if self.strategy_var.get() in [
            "🧠 Intelligent (détection auto)",
            "📁 Un SET par dossier",
            "📂 Regrouper par dossier parent",
            "🔤 Regrouper par préfixe",
            "📦 Tout en un seul SET"
        ] else 0
        
        strategies = [
            GroupingStrategy.SMART,
            GroupingStrategy.BY_FOLDER,
            GroupingStrategy.BY_PARENT_FOLDER,
            GroupingStrategy.BY_PREFIX,
            GroupingStrategy.SINGLE_SET
        ]
        
        return strategies[idx]
    
    def _progress_callback(self, message: str, current: int, total: int):
        """Callback pour la progression"""
        self.progress_label.configure(text=message[:50])
        if total > 0:
            self.progress_var.set((current / total) * 100)
        self.update_idletasks()
    
    def _start_scan(self):
        """Lance le scan"""
        source = self.source_var.get()
        
        if not source:
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier source")
            return
        
        if not Path(source).exists():
            messagebox.showerror("Erreur", "Le dossier source n'existe pas")
            return
        
        # Désactiver les boutons pendant le scan
        self.scan_btn.configure(state='disabled')
        self.progress_var.set(0)
        self._log(f"Scan de {source}...")
        
        # Configurer le scanner
        self.scanner.reset()
        self.scanner.recursive = self.recursive_var.get()
        self.scanner.include_existing_sets = self.include_sets_var.get()
        self.scanner.set_progress_callback(self._progress_callback)
        
        if self.dest_var.get():
            self.scanner.output_base_path = Path(self.dest_var.get())
        
        # Lancer dans un thread
        def do_scan():
            try:
                self.scan_result = self.scanner.scan_directory(source, self.scanner.recursive)
                self.plans = self.scanner.analyze_and_plan(self.scan_result, self._get_strategy())
                self.scanner.generation_plans = self.plans
                
                # Mettre à jour l'UI dans le thread principal
                self.after(0, self._update_results)
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erreur", f"Erreur lors du scan:\n{e}"))
            finally:
                self.after(0, lambda: self.scan_btn.configure(state='normal'))
        
        threading.Thread(target=do_scan, daemon=True).start()
    
    def _update_results(self):
        """Met à jour l'affichage des résultats"""
        summary = self.scanner.get_summary()
        
        # Stats
        self.stats_label.configure(
            text=f"📁 {summary['scanned_folders']} dossiers | "
                 f"📄 {summary['found_sty']} fichiers STY | "
                 f"📦 {summary['found_sets']} SET existants | "
                 f"🎯 {len(self.plans)} SET à générer"
        )
        
        # Vider la liste
        for item in self.plans_tree.get_children():
            self.plans_tree.delete(item)
        
        # Remplir avec les plans
        for plan in self.plans:
            source_name = plan.source_folder.name if plan.source_folder else "N/A"
            output_name = plan.output_path.name
            
            self.plans_tree.insert('', 'end', values=(
                plan.name,
                f"{plan.favorite_count}/10",
                f"{plan.user_count}/3",
                source_name,
                output_name
            ))
        
        # Activer les boutons
        if self.plans:
            self.preview_btn.configure(state='normal')
            self.generate_btn.configure(state='normal')
            self.generate_selected_btn.configure(state='normal')
        
        self._log(f"Scan terminé: {len(self.plans)} SET planifiés")
        self.progress_var.set(100)
    
    def _on_plan_select(self, event):
        """Affiche les détails du plan sélectionné"""
        selection = self.plans_tree.selection()
        
        if not selection:
            return
        
        idx = self.plans_tree.index(selection[0])
        plan = self.plans[idx]
        
        # Afficher les détails
        details = f"SET: {plan.name}\n"
        details += f"Sortie: {plan.output_path}\n"
        details += f"Source: {plan.source_folder}\n\n"
        details += "Contenu:\n"
        
        for path, bank_type, bank_num in plan.sources:
            details += f"  • {bank_type.value}{bank_num:02d} ← {path.name}\n"
        
        self.details_text.delete('1.0', 'end')
        self.details_text.insert('1.0', details)
    
    def _preview(self):
        """Prévisualise la génération (dry run)"""
        self._log("Prévisualisation...")
        
        results = self.scanner.execute_plans(dry_run=True)
        
        preview_text = "=== PRÉVISUALISATION ===\n\n"
        for plan, success, message in results:
            status = "✅" if success else "❌"
            preview_text += f"{status} {plan.name}\n"
            preview_text += f"   → {plan.output_path}\n"
            preview_text += f"   Favorites: {plan.favorite_count}, Users: {plan.user_count}\n\n"
        
        # Afficher dans une fenêtre
        preview_win = tk.Toplevel(self)
        preview_win.title("Prévisualisation")
        preview_win.geometry("600x400")
        
        text = tk.Text(preview_win, font=('Consolas', 10))
        text.insert('1.0', preview_text)
        text.configure(state='disabled')
        text.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Button(preview_win, text="Fermer", command=preview_win.destroy).pack(pady=10)
    
    def _generate(self):
        """Génère tous les SET"""
        if not self.plans:
            return
        
        if not messagebox.askyesno(
            "Confirmer",
            f"Générer {len(self.plans)} SET ?\n\n"
            "Les SET existants seront écrasés."
        ):
            return
        
        self._do_generate(self.plans)
    
    def _generate_selected(self):
        """Génère uniquement les SET sélectionnés"""
        selection = self.plans_tree.selection()
        
        if not selection:
            messagebox.showinfo("Info", "Sélectionnez les SET à générer")
            return
        
        selected_plans = [self.plans[self.plans_tree.index(item)] for item in selection]
        
        if not messagebox.askyesno(
            "Confirmer",
            f"Générer {len(selected_plans)} SET sélectionné(s) ?"
        ):
            return
        
        self._do_generate(selected_plans)
    
    def _do_generate(self, plans: List[SetGenerationPlan]):
        """Exécute la génération"""
        self.generate_btn.configure(state='disabled')
        self.generate_selected_btn.configure(state='disabled')
        self.progress_var.set(0)
        
        def do_generation():
            results = self.scanner.execute_plans(plans, dry_run=False)
            
            success_count = sum(1 for _, s, _ in results if s)
            fail_count = len(results) - success_count
            
            self.after(0, lambda: self._generation_complete(results, success_count, fail_count))
        
        threading.Thread(target=do_generation, daemon=True).start()
    
    def _generation_complete(self, results, success_count, fail_count):
        """Appelé quand la génération est terminée"""
        self.generate_btn.configure(state='normal')
        self.generate_selected_btn.configure(state='normal')
        self.progress_var.set(100)
        
        # Log
        for plan, success, message in results:
            status = "✅" if success else "❌"
            self._log(f"{status} {message}")
        
        # Message final
        if fail_count == 0:
            messagebox.showinfo(
                "Succès",
                f"✅ {success_count} SET générés avec succès !"
            )
        else:
            messagebox.showwarning(
                "Terminé avec erreurs",
                f"✅ {success_count} SET générés\n"
                f"❌ {fail_count} erreurs\n\n"
                "Consultez le journal pour plus de détails."
            )


def show_auto_mode(parent):
    """Affiche la fenêtre du mode automatique"""
    window = AutoModeWindow(parent)
    return window
