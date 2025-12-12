"""
Interface graphique pour le calculateur de stations libres
Permet la saisie interactive des observations et l'affichage des résultats
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import json
import csv
from typing import List, Dict, Optional
import numpy as np

# Import du moteur de calcul
from topo_station_ls import (
    FreeStationLS, ControlPoint, Observation, Config,
    read_controls_csv, read_observations_csv, read_rays_csv
)
from gsi_parser import GSIParser


class StationLibreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculateur de Stations Libres")
        self.root.geometry("1200x800")
        
        # Données
        self.controls: Dict[str, ControlPoint] = {}
        self.observations: List[Observation] = []
        self.config = Config()
        
        # Création de l'interface
        self.create_widgets()
        
    def create_widgets(self):
        """Créer tous les widgets de l'interface"""
        
        # Notebook principal (onglets)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet 1: Configuration
        self.tab_config = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_config, text="⚙️ Configuration")
        self.create_config_tab()
        
        # Onglet 2: Points connus
        self.tab_points = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_points, text="📍 Points Connus")
        self.create_points_tab()
        
        # Onglet 3: Observations
        self.tab_obs = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_obs, text="🔭 Observations")
        self.create_observations_tab()
        
        # Onglet 4: Résultats
        self.tab_results = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_results, text="📊 Résultats")
        self.create_results_tab()
        
        # Barre d'outils en bas
        self.create_toolbar()
        
    def create_config_tab(self):
        """Onglet de configuration"""
        frame = ttk.LabelFrame(self.tab_config, text="Paramètres de calcul", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Hauteur instrument
        row = 0
        ttk.Label(frame, text="Hauteur instrument (m):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_hi = ttk.Entry(frame, width=15)
        self.entry_hi.insert(0, "0.000")
        self.entry_hi.grid(row=row, column=1, padx=5, pady=5)
        
        # Sigma direction
        row += 1
        ttk.Label(frame, text="Sigma direction (mgon):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_sigma_dir = ttk.Entry(frame, width=15)
        self.entry_sigma_dir.insert(0, "0.5")
        self.entry_sigma_dir.grid(row=row, column=1, padx=5, pady=5)
        
        # Sigma zénith
        row += 1
        ttk.Label(frame, text="Sigma zénith (mgon):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_sigma_zen = ttk.Entry(frame, width=15)
        self.entry_sigma_zen.insert(0, "1.0")
        self.entry_sigma_zen.grid(row=row, column=1, padx=5, pady=5)
        
        # EDM a (mm)
        row += 1
        ttk.Label(frame, text="EDM constante a (mm):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_edm_a = ttk.Entry(frame, width=15)
        self.entry_edm_a.insert(0, "1.5")
        self.entry_edm_a.grid(row=row, column=1, padx=5, pady=5)
        
        # EDM b (ppm)
        row += 1
        ttk.Label(frame, text="EDM échelle b (ppm):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_edm_b = ttk.Entry(frame, width=15)
        self.entry_edm_b.insert(0, "2.0")
        self.entry_edm_b.grid(row=row, column=1, padx=5, pady=5)
        
        # Unité des angles
        row += 1
        ttk.Label(frame, text="Unité des angles:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.combo_unit = ttk.Combobox(frame, values=["gon", "deg", "rad"], width=12, state="readonly")
        self.combo_unit.set("gon")
        self.combo_unit.grid(row=row, column=1, padx=5, pady=5)
        
        # Boutons import/export config
        row += 1
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="📁 Charger config", command=self.load_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Sauver config", command=self.save_config).pack(side=tk.LEFT, padx=5)
        
    def create_points_tab(self):
        """Onglet des points connus"""
        # Frame supérieur pour les boutons
        top_frame = ttk.Frame(self.tab_points)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(top_frame, text="📁 Importer CSV", command=self.import_controls_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="📋 Importer GSI", command=self.import_gsi_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="➕ Ajouter point", command=self.add_control_point).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="❌ Supprimer", command=self.delete_control_point).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="🗑️ Tout effacer", command=self.clear_controls).pack(side=tk.LEFT, padx=5)
        
        # Table des points
        frame = ttk.Frame(self.tab_points)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tree_points = ttk.Treeview(frame, columns=("ID", "X", "Y", "Z"), 
                                        show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree_points.yview)
        
        self.tree_points.heading("ID", text="Point ID")
        self.tree_points.heading("X", text="X (m)")
        self.tree_points.heading("Y", text="Y (m)")
        self.tree_points.heading("Z", text="Z (m)")
        
        self.tree_points.column("ID", width=100)
        self.tree_points.column("X", width=150)
        self.tree_points.column("Y", width=150)
        self.tree_points.column("Z", width=150)
        
        self.tree_points.pack(fill=tk.BOTH, expand=True)
        
    def create_observations_tab(self):
        """Onglet des observations"""
        # Frame supérieur pour les boutons
        top_frame = ttk.Frame(self.tab_obs)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(top_frame, text="📁 Importer CSV", command=self.import_observations_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="📋 Importer GSI", command=self.import_gsi_observations).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="➕ Ajouter observation", command=self.add_observation).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="❌ Supprimer", command=self.delete_observation).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="🗑️ Tout effacer", command=self.clear_observations).pack(side=tk.LEFT, padx=5)
        
        # Table des observations
        frame = ttk.Frame(self.tab_obs)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tree_obs = ttk.Treeview(frame, 
                                     columns=("Ray", "Point", "Type", "Valeur", "Unité", "Séries", "Hauteur"),
                                     show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree_obs.yview)
        
        self.tree_obs.heading("Ray", text="Visée")
        self.tree_obs.heading("Point", text="Point")
        self.tree_obs.heading("Type", text="Type")
        self.tree_obs.heading("Valeur", text="Valeur")
        self.tree_obs.heading("Unité", text="Unité")
        self.tree_obs.heading("Séries", text="Séries")
        self.tree_obs.heading("Hauteur", text="H. Prisme")
        
        self.tree_obs.column("Ray", width=80)
        self.tree_obs.column("Point", width=80)
        self.tree_obs.column("Type", width=80)
        self.tree_obs.column("Valeur", width=120)
        self.tree_obs.column("Unité", width=60)
        self.tree_obs.column("Séries", width=60)
        self.tree_obs.column("Hauteur", width=80)
        
        self.tree_obs.pack(fill=tk.BOTH, expand=True)
        
    def create_results_tab(self):
        """Onglet des résultats"""
        # Zone de texte avec scrollbar
        frame = ttk.Frame(self.tab_results)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_results = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                                   font=("Courier New", 10))
        scrollbar.config(command=self.text_results.yview)
        self.text_results.pack(fill=tk.BOTH, expand=True)
        
        # Boutons d'export
        btn_frame = ttk.Frame(self.tab_results)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="💾 Exporter résultats", command=self.export_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📊 Graphiques", command=self.show_graphs).pack(side=tk.LEFT, padx=5)
        
    def create_toolbar(self):
        """Barre d'outils en bas"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="🧮 CALCULER", command=self.calculate, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(toolbar, text="Prêt", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(toolbar, text="❓ Aide", command=self.show_help).pack(side=tk.RIGHT, padx=5)
        
    # === Méthodes de gestion des points ===
    
    def import_controls_csv(self):
        """Importer les points connus depuis un CSV"""
        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier des points connus",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.controls = read_controls_csv(Path(filename))
                self.refresh_points_table()
                self.status_label.config(text=f"✅ {len(self.controls)} points chargés")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'import:\n{str(e)}")
    
    def import_gsi_file(self):
        """Importer un fichier GSI complet (points + observations)"""
        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier GSI Leica",
            filetypes=[("GSI files", "*.gsi"), ("All files", "*.*")]
        )
        if filename:
            try:
                parser = GSIParser()
                parser.parse_file(Path(filename))
                
                # Afficher un résumé
                summary = parser.export_summary()
                
                # Demander confirmation
                dialog = tk.Toplevel(self.root)
                dialog.title("Aperçu des données GSI")
                dialog.geometry("600x400")
                dialog.transient(self.root)
                
                text_widget = tk.Text(dialog, wrap=tk.WORD, font=("Courier New", 9))
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                text_widget.insert(1.0, summary)
                text_widget.config(state=tk.DISABLED)
                
                btn_frame = ttk.Frame(dialog)
                btn_frame.pack(fill=tk.X, padx=10, pady=10)
                
                def import_data():
                    observations, control_points = parser.to_observations()
                    
                    # Fusionner avec les données existantes
                    self.controls.update(control_points)
                    self.observations.extend(observations)
                    
                    # Mettre à jour la hauteur instrument
                    h_inst = parser.get_instrument_height()
                    if h_inst > 0:
                        self.entry_hi.delete(0, tk.END)
                        self.entry_hi.insert(0, f"{h_inst:.3f}")
                    
                    self.refresh_points_table()
                    self.refresh_observations_table()
                    
                    dialog.destroy()
                    self.status_label.config(text=f"✅ GSI importé: {len(control_points)} points, {len(observations)} obs")
                
                ttk.Button(btn_frame, text="✅ Importer", command=import_data).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_frame, text="❌ Annuler", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier GSI:\n{str(e)}")
                
    def add_control_point(self):
        """Ajouter un point connu manuellement"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter un point connu")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="ID du point:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        entry_id = ttk.Entry(dialog, width=20)
        entry_id.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="X (m):").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        entry_x = ttk.Entry(dialog, width=20)
        entry_x.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Y (m):").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        entry_y = ttk.Entry(dialog, width=20)
        entry_y.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Z (m):").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        entry_z = ttk.Entry(dialog, width=20)
        entry_z.grid(row=3, column=1, padx=10, pady=5)
        
        def save_point():
            try:
                pid = entry_id.get().strip()
                x = float(entry_x.get())
                y = float(entry_y.get())
                z = float(entry_z.get())
                
                if not pid:
                    raise ValueError("L'ID du point est requis")
                
                self.controls[pid] = ControlPoint(pid=pid, X=x, Y=y, Z=z)
                self.refresh_points_table()
                dialog.destroy()
                self.status_label.config(text=f"✅ Point {pid} ajouté")
            except ValueError as e:
                messagebox.showerror("Erreur", str(e))
        
        ttk.Button(dialog, text="✅ Ajouter", command=save_point).grid(row=4, column=0, columnspan=2, pady=10)
        
    def delete_control_point(self):
        """Supprimer le point sélectionné"""
        selection = self.tree_points.selection()
        if not selection:
            messagebox.showwarning("Attention", "Aucun point sélectionné")
            return
        
        item = self.tree_points.item(selection[0])
        pid = item['values'][0]
        
        if messagebox.askyesno("Confirmation", f"Supprimer le point {pid} ?"):
            del self.controls[pid]
            self.refresh_points_table()
            self.status_label.config(text=f"🗑️ Point {pid} supprimé")
            
    def clear_controls(self):
        """Effacer tous les points"""
        if messagebox.askyesno("Confirmation", "Supprimer tous les points ?"):
            self.controls.clear()
            self.refresh_points_table()
            self.status_label.config(text="🗑️ Tous les points supprimés")
            
    def refresh_points_table(self):
        """Rafraîchir la table des points"""
        # Effacer
        for item in self.tree_points.get_children():
            self.tree_points.delete(item)
        
        # Remplir
        for pid, point in sorted(self.controls.items()):
            self.tree_points.insert("", tk.END, values=(
                pid, f"{point.X:.3f}", f"{point.Y:.3f}", f"{point.Z:.3f}"
            ))
            
    # === Méthodes de gestion des observations ===
    
    def import_observations_csv(self):
        """Importer les observations depuis un CSV"""
        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier des observations",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.observations = read_observations_csv(Path(filename), 
                                                         self.combo_unit.get())
                self.refresh_observations_table()
                self.status_label.config(text=f"✅ {len(self.observations)} observations chargées")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'import:\n{str(e)}")
    
    def import_gsi_observations(self):
        """Importer les observations depuis un fichier GSI (sans les points connus)"""
        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier GSI Leica",
            filetypes=[("GSI files", "*.gsi"), ("All files", "*.*")]
        )
        if filename:
            try:
                parser = GSIParser()
                parser.parse_file(Path(filename))
                
                observations, _ = parser.to_observations()
                
                # Ajouter aux observations existantes
                self.observations.extend(observations)
                self.refresh_observations_table()
                
                # Mettre à jour la hauteur instrument
                h_inst = parser.get_instrument_height()
                if h_inst > 0:
                    self.entry_hi.delete(0, tk.END)
                    self.entry_hi.insert(0, f"{h_inst:.3f}")
                
                self.status_label.config(text=f"✅ {len(observations)} observations GSI importées")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'import GSI:\n{str(e)}")
                
    def add_observation(self):
        """Ajouter une observation manuellement"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter une observation")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="ID visée (ray):").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        entry_ray = ttk.Entry(dialog, width=20)
        entry_ray.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Point visé:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        entry_pid = ttk.Entry(dialog, width=20)
        entry_pid.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Type:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        combo_type = ttk.Combobox(dialog, values=["dir", "zen", "dist"], width=17, state="readonly")
        combo_type.set("dir")
        combo_type.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Valeur:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        entry_value = ttk.Entry(dialog, width=20)
        entry_value.grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Unité:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        entry_unit = ttk.Entry(dialog, width=20)
        entry_unit.insert(0, self.combo_unit.get())
        entry_unit.grid(row=4, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Nb séries:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        entry_series = ttk.Entry(dialog, width=20)
        entry_series.insert(0, "1")
        entry_series.grid(row=5, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Hauteur prisme (m):").grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)
        entry_height = ttk.Entry(dialog, width=20)
        entry_height.insert(0, "0.000")
        entry_height.grid(row=6, column=1, padx=10, pady=5)
        
        def save_obs():
            try:
                obs = Observation(
                    ray_id=entry_ray.get().strip(),
                    pid=entry_pid.get().strip(),
                    obs_type=combo_type.get(),
                    value=float(entry_value.get()),
                    unit=entry_unit.get(),
                    n_series=int(entry_series.get()),
                    h_target=float(entry_height.get())
                )
                self.observations.append(obs)
                self.refresh_observations_table()
                dialog.destroy()
                self.status_label.config(text="✅ Observation ajoutée")
            except ValueError as e:
                messagebox.showerror("Erreur", str(e))
        
        ttk.Button(dialog, text="✅ Ajouter", command=save_obs).grid(row=7, column=0, columnspan=2, pady=10)
        
    def delete_observation(self):
        """Supprimer l'observation sélectionnée"""
        selection = self.tree_obs.selection()
        if not selection:
            messagebox.showwarning("Attention", "Aucune observation sélectionnée")
            return
        
        idx = self.tree_obs.index(selection[0])
        if messagebox.askyesno("Confirmation", "Supprimer cette observation ?"):
            del self.observations[idx]
            self.refresh_observations_table()
            self.status_label.config(text="🗑️ Observation supprimée")
            
    def clear_observations(self):
        """Effacer toutes les observations"""
        if messagebox.askyesno("Confirmation", "Supprimer toutes les observations ?"):
            self.observations.clear()
            self.refresh_observations_table()
            self.status_label.config(text="🗑️ Toutes les observations supprimées")
            
    def refresh_observations_table(self):
        """Rafraîchir la table des observations"""
        # Effacer
        for item in self.tree_obs.get_children():
            self.tree_obs.delete(item)
        
        # Remplir
        for obs in self.observations:
            self.tree_obs.insert("", tk.END, values=(
                obs.ray_id, obs.pid, obs.obs_type, 
                f"{obs.value:.4f}", obs.unit, obs.n_series, f"{obs.h_target:.3f}"
            ))
            
    # === Calcul ===
    
    def calculate(self):
        """Lancer le calcul de la station libre"""
        # Vérifications
        if not self.controls:
            messagebox.showerror("Erreur", "Aucun point connu défini")
            return
        
        if not self.observations:
            messagebox.showerror("Erreur", "Aucune observation définie")
            return
        
        # Récupérer la config
        try:
            config = Config(
                sigma_dir_mgon=float(self.entry_sigma_dir.get()),
                sigma_zen_mgon=float(self.entry_sigma_zen.get()),
                edm_a_mm=float(self.entry_edm_a.get()),
                edm_b_ppm=float(self.entry_edm_b.get()),
                h_instrument=float(self.entry_hi.get()),
                angles_unit=self.combo_unit.get()
            )
        except ValueError as e:
            messagebox.showerror("Erreur", f"Paramètres invalides:\n{str(e)}")
            return
        
        # Calcul
        self.status_label.config(text="⏳ Calcul en cours...")
        self.root.update()
        
        try:
            solver = FreeStationLS(self.controls, self.observations, {}, config)
            result = solver.solve()
            
            # Afficher les résultats
            self.display_results(result, config)
            self.notebook.select(self.tab_results)
            self.status_label.config(text="✅ Calcul terminé avec succès")
            
        except Exception as e:
            messagebox.showerror("Erreur de calcul", str(e))
            self.status_label.config(text="❌ Erreur de calcul")
            
    def display_results(self, result, config):
        """Afficher les résultats dans l'onglet résultats"""
        self.text_results.delete(1.0, tk.END)
        
        text = "="*70 + "\n"
        text += "  RÉSULTATS DU CALCUL DE STATION LIBRE\n"
        text += "="*70 + "\n\n"
        
        # Paramètres calculés
        text += "COORDONNÉES DE LA STATION:\n"
        text += "-"*70 + "\n"
        text += f"  X₀ = {result.X0:12.3f} m  ± {result.std_X0*1000:6.1f} mm\n"
        text += f"  Y₀ = {result.Y0:12.3f} m  ± {result.std_Y0*1000:6.1f} mm\n"
        text += f"  Z₀ = {result.Z0:12.3f} m  ± {result.std_Z0*1000:6.1f} mm\n"
        text += f"  ω  = {result.omega_gon:12.4f} gon  ± {result.std_omega_mgon:6.2f} mgon\n\n"
        
        # Statistiques
        text += "STATISTIQUES:\n"
        text += "-"*70 + "\n"
        text += f"  Nombre d'observations : {result.n_obs}\n"
        text += f"  Nombre de paramètres  : {result.n_params}\n"
        text += f"  Degrés de liberté     : {result.dof}\n"
        text += f"  Sigma a posteriori    : {result.sigma0:.4f}\n"
        text += f"  Convergence           : {result.converged}\n"
        text += f"  Itérations            : {result.iterations}\n\n"
        
        # Configuration utilisée
        text += "CONFIGURATION:\n"
        text += "-"*70 + "\n"
        text += f"  Hauteur instrument    : {config.h_instrument:.3f} m\n"
        text += f"  Sigma direction       : {config.sigma_dir_mgon:.2f} mgon\n"
        text += f"  Sigma zénith          : {config.sigma_zen_mgon:.2f} mgon\n"
        text += f"  EDM a (constante)     : {config.edm_a_mm:.2f} mm\n"
        text += f"  EDM b (échelle)       : {config.edm_b_ppm:.2f} ppm\n"
        text += f"  Unité angles          : {config.angles_unit}\n\n"
        
        self.text_results.insert(1.0, text)
        self.current_result = result
        
    # === Export et graphiques ===
    
    def export_results(self):
        """Exporter les résultats"""
        if not hasattr(self, 'current_result'):
            messagebox.showwarning("Attention", "Aucun résultat à exporter")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Exporter les résultats",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.text_results.get(1.0, tk.END))
            self.status_label.config(text=f"✅ Résultats exportés vers {filename}")
            
    def show_graphs(self):
        """Afficher les graphiques des résultats"""
        if not hasattr(self, 'current_result'):
            messagebox.showwarning("Attention", "Aucun résultat à visualiser")
            return
        
        messagebox.showinfo("Info", "Fonctionnalité en développement\nGraphiques à venir!")
        
    # === Config ===
    
    def load_config(self):
        """Charger une configuration depuis un fichier JSON"""
        filename = filedialog.askopenfilename(
            title="Charger une configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                self.entry_hi.delete(0, tk.END)
                self.entry_hi.insert(0, str(config.get("h_instrument", 0.0)))
                
                self.entry_sigma_dir.delete(0, tk.END)
                self.entry_sigma_dir.insert(0, str(config.get("sigma_dir_mgon", 0.5)))
                
                self.entry_sigma_zen.delete(0, tk.END)
                self.entry_sigma_zen.insert(0, str(config.get("sigma_zen_mgon", 1.0)))
                
                self.entry_edm_a.delete(0, tk.END)
                self.entry_edm_a.insert(0, str(config.get("edm_a_mm", 1.5)))
                
                self.entry_edm_b.delete(0, tk.END)
                self.entry_edm_b.insert(0, str(config.get("edm_b_ppm", 2.0)))
                
                self.combo_unit.set(config.get("angles_unit", "gon"))
                
                self.status_label.config(text="✅ Configuration chargée")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du chargement:\n{str(e)}")
                
    def save_config(self):
        """Sauvegarder la configuration actuelle"""
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder la configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                config = {
                    "h_instrument": float(self.entry_hi.get()),
                    "sigma_dir_mgon": float(self.entry_sigma_dir.get()),
                    "sigma_zen_mgon": float(self.entry_sigma_zen.get()),
                    "edm_a_mm": float(self.entry_edm_a.get()),
                    "edm_b_ppm": float(self.entry_edm_b.get()),
                    "angles_unit": self.combo_unit.get()
                }
                
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)
                
                self.status_label.config(text="✅ Configuration sauvegardée")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}")
                
    def show_help(self):
        """Afficher l'aide"""
        help_text = """
CALCULATEUR DE STATIONS LIBRES - AIDE

1. Configuration :
   - Définir les paramètres de calcul (sigmas, EDM, hauteur instrument)
   
2. Points Connus :
   - Importer depuis un CSV (pid,X,Y,Z)
   - Ou ajouter manuellement point par point
   
3. Observations :
   - Importer depuis un CSV (ray_id,pid,obs_type,value,unit,n_series,h_target)
   - Ou ajouter manuellement
   - Types : dir (direction), zen (zénith), dist (distance)
   
4. Calcul :
   - Cliquer sur "CALCULER" pour lancer l'ajustement
   - Les résultats s'affichent dans l'onglet "Résultats"
   
5. Export :
   - Sauvegarder les résultats en fichier texte
   - Graphiques (à venir)

Pour plus d'informations, voir README_topo_station_ls.md
        """
        messagebox.showinfo("Aide", help_text)


def main():
    root = tk.Tk()
    
    # Style
    style = ttk.Style()
    style.theme_use('clam')
    
    app = StationLibreGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
