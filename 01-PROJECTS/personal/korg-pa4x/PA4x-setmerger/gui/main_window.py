"""
Interface graphique pour PA4x Set Merger
Utilise tkinter avec ttk pour un look moderne
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, List, Dict, Any
import threading

# Ajouter le chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.style_bank import StyleBank, BankType
from src.models.set_file import SetFile
from src.merger.set_merger import SetMerger, ConflictResolution, MergeOperation
from gui.auto_mode_window import show_auto_mode


class DragDropListbox(tk.Listbox):
    """Listbox avec support drag & drop interne"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<Button-1>', self.on_click)
        self.bind('<B1-Motion>', self.on_drag)
        self.bind('<ButtonRelease-1>', self.on_drop)
        self.drag_start_index = None
    
    def on_click(self, event):
        self.drag_start_index = self.nearest(event.y)
    
    def on_drag(self, event):
        pass  # Visuel de drag si nécessaire
    
    def on_drop(self, event):
        if self.drag_start_index is None:
            return
        
        drop_index = self.nearest(event.y)
        if drop_index != self.drag_start_index:
            # Réorganiser les éléments
            item = self.get(self.drag_start_index)
            self.delete(self.drag_start_index)
            self.insert(drop_index, item)
        
        self.drag_start_index = None


class BankSlotWidget(ttk.Frame):
    """Widget représentant un slot de banque"""
    
    def __init__(self, parent, bank_type: str, bank_number: int, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.bank_type = bank_type
        self.bank_number = bank_number
        self.bank_data: Optional[StyleBank] = None
        self.source_path: Optional[Path] = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Nom du slot
        self.label = ttk.Label(
            self, 
            text=f"{self.bank_type}{self.bank_number:02d}",
            width=12,
            anchor='center'
        )
        self.label.pack(side='left', padx=2)
        
        # Indicateur de contenu
        self.content_label = ttk.Label(
            self, 
            text="(vide)",
            width=30,
            anchor='w'
        )
        self.content_label.pack(side='left', padx=5, fill='x', expand=True)
        
        # Boutons
        self.btn_load = ttk.Button(self, text="📂", width=3, command=self.load_file)
        self.btn_load.pack(side='left', padx=2)
        
        self.btn_clear = ttk.Button(self, text="🗑", width=3, command=self.clear, state='disabled')
        self.btn_clear.pack(side='left', padx=2)
        
        # Style par défaut
        self.configure(relief='groove', borderwidth=1, padding=5)
    
    def load_file(self):
        """Charge un fichier STY dans ce slot"""
        filepath = filedialog.askopenfilename(
            title=f"Charger {self.bank_type}{self.bank_number:02d}",
            filetypes=[("Fichiers STY", "*.STY"), ("Tous les fichiers", "*.*")]
        )
        
        if filepath:
            try:
                self.set_content(Path(filepath))
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger le fichier:\n{e}")
    
    def set_content(self, path: Path, bank: Optional[StyleBank] = None):
        """Définit le contenu du slot"""
        self.source_path = path
        
        if bank is None:
            self.bank_data = StyleBank.from_file(path)
        else:
            self.bank_data = bank
        
        # Mettre à jour l'affichage
        filename = path.name if len(path.name) < 30 else path.name[:27] + "..."
        size_kb = len(self.bank_data.raw_data) / 1024
        self.content_label.configure(text=f"{filename} ({size_kb:.1f} KB)")
        self.btn_clear.configure(state='normal')
        
        # Changer la couleur de fond
        self.configure(style='Filled.TFrame')
    
    def clear(self):
        """Vide le slot"""
        self.bank_data = None
        self.source_path = None
        self.content_label.configure(text="(vide)")
        self.btn_clear.configure(state='disabled')
        self.configure(style='TFrame')
    
    def get_data(self) -> Optional[StyleBank]:
        """Retourne les données de la banque"""
        return self.bank_data
    
    def is_filled(self) -> bool:
        """Vérifie si le slot contient des données"""
        return self.bank_data is not None


class PA4xSetMergerApp:
    """Application principale"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PA4x Set Merger - Korg Style Fusion Tool")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)
        
        # Merger
        self.merger = SetMerger()
        self.merger.create_new_target()
        
        # Slots de banques
        self.favorite_slots: List[BankSlotWidget] = []
        self.user_slots: List[BankSlotWidget] = []
        
        # Sources ajoutées
        self.sources: List[Dict[str, Any]] = []
        
        # Créer le style
        self._create_styles()
        
        # Créer l'interface
        self._create_menu()
        self._create_main_layout()
        self._create_status_bar()
        
        # Configurer le drag & drop de fichiers
        self._setup_drag_drop()
    
    def _create_styles(self):
        """Configure les styles ttk"""
        style = ttk.Style()
        
        # Style pour les slots remplis
        style.configure('Filled.TFrame', background='#90EE90')
        
        # Style pour les sections
        style.configure('Section.TLabelframe', padding=10)
        style.configure('Section.TLabelframe.Label', font=('Helvetica', 10, 'bold'))
    
    def _create_menu(self):
        """Crée la barre de menu"""
        menubar = tk.Menu(self.root)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nouveau SET", command=self.new_set, accelerator="Ctrl+N")
        file_menu.add_command(label="Ouvrir SET...", command=self.open_set, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Enregistrer SET...", command=self.save_set, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit, accelerator="Alt+F4")
        menubar.add_cascade(label="Fichier", menu=file_menu)
        
        # Menu Sources
        source_menu = tk.Menu(menubar, tearoff=0)
        source_menu.add_command(label="Ajouter fichier STY...", command=self.add_sty_file)
        source_menu.add_command(label="Ajouter dossier de STY...", command=self.add_sty_folder)
        source_menu.add_command(label="Ajouter SET existant...", command=self.add_set_folder)
        source_menu.add_separator()
        source_menu.add_command(label="Effacer toutes les sources", command=self.clear_sources)
        menubar.add_cascade(label="Sources", menu=source_menu)
        
        # Menu Outils
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="🤖 Mode Automatique...", command=self.open_auto_mode, accelerator="Ctrl+A")
        tools_menu.add_separator()
        tools_menu.add_command(label="Analyser un SET...", command=self.analyze_set)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="À propos", command=self.show_about)
        help_menu.add_command(label="Guide d'utilisation", command=self.show_help)
        menubar.add_cascade(label="Aide", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # Raccourcis clavier
        self.root.bind('<Control-n>', lambda e: self.new_set())
        self.root.bind('<Control-o>', lambda e: self.open_set())
        self.root.bind('<Control-s>', lambda e: self.save_set())
        self.root.bind('<Control-a>', lambda e: self.open_auto_mode())
    
    def _create_main_layout(self):
        """Crée le layout principal"""
        # Frame principal avec PanedWindow
        main_paned = ttk.PanedWindow(self.root, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # === Panneau gauche: Sources ===
        left_frame = ttk.Frame(main_paned, width=350)
        main_paned.add(left_frame, weight=1)
        
        self._create_sources_panel(left_frame)
        
        # === Panneau droit: SET cible ===
        right_frame = ttk.Frame(main_paned, width=600)
        main_paned.add(right_frame, weight=2)
        
        self._create_target_panel(right_frame)
    
    def _create_sources_panel(self, parent):
        """Crée le panneau des sources"""
        # Titre
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(title_frame, text="① Sources", font=('Helvetica', 12, 'bold')).pack(side='left')
        
        # Boutons d'ajout
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="+ Fichier STY", command=self.add_sty_file).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="+ Dossier STY", command=self.add_sty_folder).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="+ SET", command=self.add_set_folder).pack(side='left', padx=2)
        
        # Liste des sources avec scrollbar
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill='both', expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.sources_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            selectmode='extended',
            font=('Consolas', 9)
        )
        self.sources_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.sources_listbox.yview)
        
        # Bind double-click pour assigner
        self.sources_listbox.bind('<Double-Button-1>', self.assign_selected_source)
        
        # Boutons d'action
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill='x', pady=5)
        
        ttk.Button(action_frame, text="② Assigner →", command=self.assign_selected_source).pack(side='left', padx=2)
        ttk.Button(action_frame, text="② Auto-Assign", command=self.auto_assign_sources).pack(side='left', padx=2)
        ttk.Button(action_frame, text="Supprimer", command=self.remove_selected_source).pack(side='left', padx=2)
        
        # Instructions
        help_frame = ttk.LabelFrame(parent, text="📖 Mode d'emploi", padding=5)
        help_frame.pack(fill='x', pady=10)
        
        instructions = """① Ajouter des fichiers STY ci-dessus
② Assigner aux slots (double-clic ou Auto-Assign)
③ Enregistrer le SET →

💡 Ou utilisez Outils → Mode Automatique
   pour scanner et générer automatiquement !"""
        
        ttk.Label(help_frame, text=instructions, justify='left', font=('Helvetica', 9)).pack(anchor='w')
        
        # Info zone
        info_frame = ttk.LabelFrame(parent, text="Informations", style='Section.TLabelframe')
        info_frame.pack(fill='x', pady=5)
        
        self.source_info_text = tk.Text(info_frame, height=5, font=('Consolas', 9), state='disabled')
        self.source_info_text.pack(fill='x', padx=5, pady=5)
        
        # Bind selection
        self.sources_listbox.bind('<<ListboxSelect>>', self.on_source_select)
    
    def _create_target_panel(self, parent):
        """Crée le panneau du SET cible"""
        # Titre avec nom du SET
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(title_frame, text="🎹 SET Cible:", font=('Helvetica', 12, 'bold')).pack(side='left')
        
        self.set_name_var = tk.StringVar(value="NouveauSet")
        self.set_name_entry = ttk.Entry(title_frame, textvariable=self.set_name_var, width=30)
        self.set_name_entry.pack(side='left', padx=10)
        
        # Notebook pour Favorites et Users
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True, pady=5)
        
        # Onglet Favorites
        fav_frame = ttk.Frame(notebook, padding=10)
        notebook.add(fav_frame, text="⭐ Favorites (1-10)")
        
        self._create_bank_slots(fav_frame, "FAVORITE", 10, self.favorite_slots)
        
        # Onglet Users
        user_frame = ttk.Frame(notebook, padding=10)
        notebook.add(user_frame, text="👤 Users (1-3)")
        
        self._create_bank_slots(user_frame, "USER", 3, self.user_slots)
        
        # Boutons d'action
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill='x', pady=10)
        
        ttk.Button(
            action_frame, 
            text="③ 💾 ENREGISTRER LE SET", 
            command=self.save_set,
            style='Accent.TButton'
        ).pack(side='right', padx=5, ipadx=10, ipady=5)
        
        ttk.Button(
            action_frame, 
            text="🗑 Tout effacer", 
            command=self.clear_all_slots
        ).pack(side='right', padx=5)
        
        # Résumé
        summary_frame = ttk.LabelFrame(parent, text="Résumé", style='Section.TLabelframe')
        summary_frame.pack(fill='x', pady=5)
        
        self.summary_label = ttk.Label(
            summary_frame, 
            text="Favorites: 0/10 | Users: 0/3 | Total: 0 banques"
        )
        self.summary_label.pack(pady=5)
    
    def _create_bank_slots(self, parent, bank_type: str, count: int, slot_list: list):
        """Crée les widgets de slots de banques"""
        for i in range(1, count + 1):
            slot = BankSlotWidget(parent, bank_type, i)
            slot.pack(fill='x', pady=2)
            slot_list.append(slot)
    
    def _create_status_bar(self):
        """Crée la barre de statut"""
        self.status_bar = ttk.Label(
            self.root, 
            text="Prêt - Glissez des fichiers STY ou SET pour commencer",
            relief='sunken',
            anchor='w',
            padding=5
        )
        self.status_bar.pack(fill='x', side='bottom')
    
    def _setup_drag_drop(self):
        """Configure le drag & drop de fichiers depuis l'explorateur"""
        # Note: tkinter natif ne supporte pas le drag & drop externe
        # Il faudrait utiliser tkinterdnd2 pour ça
        # Pour l'instant, on utilise les boutons et menus
        pass
    
    def update_status(self, message: str):
        """Met à jour la barre de statut"""
        self.status_bar.configure(text=message)
        self.root.update_idletasks()
    
    def update_summary(self):
        """Met à jour le résumé"""
        fav_count = sum(1 for slot in self.favorite_slots if slot.is_filled())
        user_count = sum(1 for slot in self.user_slots if slot.is_filled())
        total = fav_count + user_count
        
        self.summary_label.configure(
            text=f"Favorites: {fav_count}/10 | Users: {user_count}/3 | Total: {total} banques"
        )
    
    # === Actions du menu Fichier ===
    
    def new_set(self):
        """Crée un nouveau SET vide"""
        if self._has_unsaved_changes():
            if not messagebox.askyesno("Nouveau SET", "Créer un nouveau SET ? Les données non sauvegardées seront perdues."):
                return
        
        self.clear_all_slots()
        self.set_name_var.set("NouveauSet")
        self.merger.create_new_target()
        self.update_status("Nouveau SET créé")
    
    def open_set(self):
        """Ouvre un SET existant"""
        folder = filedialog.askdirectory(title="Sélectionner un dossier .SET")
        
        if folder:
            if not folder.upper().endswith('.SET'):
                messagebox.showwarning("Attention", "Le dossier devrait avoir l'extension .SET")
            
            try:
                self.clear_all_slots()
                set_file = SetFile.from_directory(Path(folder))
                
                # Charger les banques dans les slots
                for bank_num, bank in set_file.favorite_banks.items():
                    if bank_num <= len(self.favorite_slots):
                        self.favorite_slots[bank_num - 1].set_content(bank.path, bank)
                
                for bank_num, bank in set_file.user_banks.items():
                    if bank_num <= len(self.user_slots):
                        self.user_slots[bank_num - 1].set_content(bank.path, bank)
                
                self.set_name_var.set(set_file.name)
                self.merger.target_set = set_file
                self.update_summary()
                self.update_status(f"SET chargé: {folder}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger le SET:\n{e}")
    
    def save_set(self):
        """Sauvegarde le SET"""
        # Demander le chemin
        folder = filedialog.askdirectory(title="Enregistrer le SET dans...")
        
        if not folder:
            return
        
        set_name = self.set_name_var.get() or "MonSet"
        output_path = Path(folder) / f"{set_name}.SET"
        
        if output_path.exists():
            if not messagebox.askyesno("Confirmer", f"Le dossier {output_path.name} existe déjà. Écraser ?"):
                return
        
        try:
            # Créer le SET avec les données des slots
            new_set = SetFile.create_empty(set_name)
            
            for i, slot in enumerate(self.favorite_slots, 1):
                if slot.is_filled():
                    new_set.add_style_bank(slot.get_data(), BankType.FAVORITE, i)
            
            for i, slot in enumerate(self.user_slots, 1):
                if slot.is_filled():
                    new_set.add_style_bank(slot.get_data(), BankType.USER, i)
            
            new_set.save(output_path)
            
            self.update_status(f"SET enregistré: {output_path}")
            messagebox.showinfo("Succès", f"SET enregistré avec succès:\n{output_path}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'enregistrer le SET:\n{e}")
    
    # === Actions du menu Sources ===
    
    def add_sty_file(self):
        """Ajoute un fichier STY aux sources"""
        files = filedialog.askopenfilenames(
            title="Sélectionner des fichiers STY",
            filetypes=[("Fichiers STY", "*.STY"), ("Tous les fichiers", "*.*")]
        )
        
        for filepath in files:
            self._add_source(Path(filepath), "STY")
    
    def add_sty_folder(self):
        """Ajoute tous les STY d'un dossier aux sources"""
        folder = filedialog.askdirectory(title="Sélectionner un dossier contenant des STY")
        
        if folder:
            folder_path = Path(folder)
            sty_files = list(folder_path.glob("*.STY"))
            
            if not sty_files:
                messagebox.showinfo("Info", "Aucun fichier .STY trouvé dans ce dossier")
                return
            
            for sty_file in sorted(sty_files):
                self._add_source(sty_file, "STY")
            
            self.update_status(f"{len(sty_files)} fichiers STY ajoutés depuis {folder_path.name}")
    
    def add_set_folder(self):
        """Ajoute un SET existant aux sources"""
        folder = filedialog.askdirectory(title="Sélectionner un dossier .SET")
        
        if folder:
            folder_path = Path(folder)
            
            # Chercher les STY dans le sous-dossier STYLE
            style_dir = folder_path / "STYLE"
            
            if style_dir.exists():
                sty_files = list(style_dir.glob("*.STY"))
            else:
                # Peut-être que c'est directement dans le dossier
                sty_files = list(folder_path.glob("*.STY"))
            
            if not sty_files:
                messagebox.showinfo("Info", "Aucun fichier .STY trouvé dans ce SET")
                return
            
            for sty_file in sorted(sty_files):
                self._add_source(sty_file, "SET")
            
            self.update_status(f"{len(sty_files)} banques ajoutées depuis {folder_path.name}")
    
    def _add_source(self, path: Path, source_type: str):
        """Ajoute une source à la liste"""
        # Vérifier si déjà présent
        for source in self.sources:
            if source['path'] == path:
                return
        
        try:
            bank = StyleBank.from_file(path)
            
            source_info = {
                'path': path,
                'type': source_type,
                'bank': bank,
                'bank_type': bank.bank_type,
                'bank_number': bank.bank_number,
                'size': len(bank.raw_data)
            }
            
            self.sources.append(source_info)
            
            # Ajouter à la listbox
            display_name = f"{bank.filename} - {path.parent.name}/{path.name}"
            self.sources_listbox.insert('end', display_name)
            
        except Exception as e:
            print(f"Erreur lors du chargement de {path}: {e}")
    
    def remove_selected_source(self):
        """Supprime les sources sélectionnées"""
        selection = self.sources_listbox.curselection()
        
        for index in reversed(selection):
            self.sources_listbox.delete(index)
            del self.sources[index]
    
    def clear_sources(self):
        """Efface toutes les sources"""
        self.sources.clear()
        self.sources_listbox.delete(0, 'end')
        self.update_status("Sources effacées")
    
    def on_source_select(self, event):
        """Appelé quand une source est sélectionnée"""
        selection = self.sources_listbox.curselection()
        
        if not selection:
            return
        
        source = self.sources[selection[0]]
        
        # Afficher les infos
        info_text = f"""Fichier: {source['path'].name}
Type: {source['type']}
Banque: {source['bank_type'].value}{source['bank_number']:02d}
Taille: {source['size'] / 1024:.1f} KB
Chemin: {source['path']}"""
        
        self.source_info_text.configure(state='normal')
        self.source_info_text.delete(1.0, 'end')
        self.source_info_text.insert('end', info_text)
        self.source_info_text.configure(state='disabled')
    
    def assign_selected_source(self, event=None):
        """Assigne la source sélectionnée à un slot"""
        selection = self.sources_listbox.curselection()
        
        if not selection:
            messagebox.showinfo("Info", "Sélectionnez d'abord une source")
            return
        
        source = self.sources[selection[0]]
        
        # Dialogue pour choisir le slot
        dialog = SlotSelectionDialog(self.root, source)
        
        if dialog.result:
            bank_type, bank_num = dialog.result
            
            if bank_type == "FAVORITE":
                slot = self.favorite_slots[bank_num - 1]
            else:
                slot = self.user_slots[bank_num - 1]
            
            slot.set_content(source['path'], source['bank'])
            self.update_summary()
            self.update_status(f"Assigné: {source['path'].name} → {bank_type}{bank_num:02d}")
    
    def auto_assign_sources(self):
        """Assigne automatiquement toutes les sources aux slots disponibles"""
        assigned = 0
        skipped = 0
        
        for source in self.sources:
            bank_type = source['bank_type']
            bank_num = source['bank_number']
            
            # Trouver le slot correspondant
            slot = None
            if bank_type == BankType.FAVORITE and bank_num <= 10:
                slot = self.favorite_slots[bank_num - 1]
            elif bank_type == BankType.USER and bank_num <= 3:
                slot = self.user_slots[bank_num - 1]
            
            # Si le slot préféré est pris, chercher un slot libre
            if slot is None or slot.is_filled():
                slot = self._find_free_slot()
            
            if slot and not slot.is_filled():
                slot.set_content(source['path'], source['bank'])
                assigned += 1
            else:
                skipped += 1
        
        self.update_summary()
        
        if skipped > 0:
            self.update_status(f"{assigned} banques assignées, {skipped} ignorées (SET plein)")
            messagebox.showwarning(
                "SET plein",
                f"✅ {assigned} banques assignées\n"
                f"⚠️ {skipped} fichiers ignorés\n\n"
                "Un SET ne peut contenir que 13 banques maximum\n"
                "(10 Favorites + 3 Users)\n\n"
                "💡 Utilisez le Mode Automatique (Outils → Mode Auto)\n"
                "pour créer plusieurs SET automatiquement."
            )
        else:
            self.update_status(f"{assigned} banques assignées automatiquement")
    
    def _find_free_slot(self) -> Optional[BankSlotWidget]:
        """Trouve le premier slot libre"""
        # D'abord chercher dans les Favorites
        for slot in self.favorite_slots:
            if not slot.is_filled():
                return slot
        # Puis dans les Users
        for slot in self.user_slots:
            if not slot.is_filled():
                return slot
        return None
    
    def clear_all_slots(self):
        """Efface tous les slots"""
        for slot in self.favorite_slots:
            slot.clear()
        for slot in self.user_slots:
            slot.clear()
        
        self.update_summary()
        self.update_status("Tous les slots effacés")
    
    def _has_unsaved_changes(self) -> bool:
        """Vérifie s'il y a des changements non sauvegardés"""
        return any(slot.is_filled() for slot in self.favorite_slots + self.user_slots)
    
    # === Aide ===
    
    def open_auto_mode(self):
        """Ouvre la fenêtre du mode automatique"""
        show_auto_mode(self.root)
    
    def analyze_set(self):
        """Analyse un SET existant et affiche ses informations"""
        folder = filedialog.askdirectory(title="Sélectionner un dossier .SET à analyser")
        
        if not folder:
            return
        
        try:
            set_file = SetFile.from_directory(Path(folder))
            info = set_file.get_info()
            
            # Créer une fenêtre d'analyse
            analyze_win = tk.Toplevel(self.root)
            analyze_win.title(f"Analyse: {info['name']}")
            analyze_win.geometry("500x400")
            
            text = tk.Text(analyze_win, font=('Consolas', 10), padx=10, pady=10)
            text.pack(fill='both', expand=True)
            
            # Formatage des infos
            report = f"""═══════════════════════════════════════
  ANALYSE DU SET: {info['name']}
═══════════════════════════════════════

📁 Chemin: {info['path']}

📊 STATISTIQUES:
  • Banques Favorites: {info['favorite_count']}/10
  • Banques Users: {info['user_count']}/3
  • Configuration globale: {'✅ Oui' if info['has_global'] else '❌ Non'}
  • Fichiers sons: {info['sound_count']}
  • Fichiers PCM: {info['pcm_count']}
  • Multisamples: {info['multisample_count']}
  • Pads: {info['pad_count']}

⭐ BANQUES FAVORITES:
"""
            for name, data in info['banks']['favorites'].items():
                status = "✅" if data['present'] else "⬜"
                size = f" ({data['size'] / 1024:.1f} KB)" if data.get('size') else ""
                report += f"  {status} {name}{size}\n"
            
            report += "\n👤 BANQUES USERS:\n"
            for name, data in info['banks']['users'].items():
                status = "✅" if data['present'] else "⬜"
                size = f" ({data['size'] / 1024:.1f} KB)" if data.get('size') else ""
                report += f"  {status} {name}{size}\n"
            
            text.insert('1.0', report)
            text.configure(state='disabled')
            
            ttk.Button(analyze_win, text="Fermer", command=analyze_win.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'analyser le SET:\n{e}")
    
    def show_about(self):
        """Affiche la boîte À propos"""
        messagebox.showinfo(
            "À propos",
            "PA4x Set Merger v1.0\n\n"
            "Outil de fusion de fichiers SET et STY\n"
            "pour claviers Korg PA4x\n\n"
            "© 2024"
        )
    
    def show_help(self):
        """Affiche l'aide"""
        help_text = """
Guide d'utilisation - PA4x Set Merger

1. AJOUTER DES SOURCES
   - Cliquez sur "+ STY" pour ajouter des fichiers STY isolés
   - Cliquez sur "+ Dossier" pour ajouter tous les STY d'un dossier
   - Cliquez sur "+ SET" pour importer les banques d'un SET existant

2. ASSIGNER LES BANQUES
   - Double-cliquez sur une source pour l'assigner à un slot
   - Ou utilisez "Auto-Assign" pour assigner automatiquement
   - Vous pouvez aussi charger directement dans chaque slot avec 📂

3. ENREGISTRER LE SET
   - Donnez un nom à votre SET dans le champ de texte
   - Cliquez sur "Enregistrer SET"
   - Choisissez le dossier de destination

STRUCTURE D'UN SET:
   - 10 banques Favorites (FAVORITE01-10.STY)
   - 3 banques Users (USER01-03.STY)
   - Chaque banque peut contenir jusqu'à 96 styles
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Aide")
        help_window.geometry("500x400")
        
        text = tk.Text(help_window, wrap='word', padx=10, pady=10)
        text.insert('1.0', help_text)
        text.configure(state='disabled')
        text.pack(fill='both', expand=True)


class SlotSelectionDialog(tk.Toplevel):
    """Dialogue pour sélectionner un slot de destination"""
    
    def __init__(self, parent, source: dict):
        super().__init__(parent)
        
        self.title("Choisir le slot de destination")
        self.geometry("300x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.result = None
        self.source = source
        
        self._create_widgets()
        
        # Centrer sur le parent
        self.geometry(f"+{parent.winfo_x() + 50}+{parent.winfo_y() + 50}")
        
        self.wait_window()
    
    def _create_widgets(self):
        ttk.Label(
            self, 
            text=f"Assigner: {self.source['path'].name}",
            wraplength=280
        ).pack(pady=10)
        
        # Type de banque
        type_frame = ttk.Frame(self)
        type_frame.pack(pady=5)
        
        ttk.Label(type_frame, text="Type:").pack(side='left')
        
        self.type_var = tk.StringVar(value=self.source['bank_type'].value)
        ttk.Radiobutton(type_frame, text="Favorite", variable=self.type_var, value="FAVORITE").pack(side='left', padx=5)
        ttk.Radiobutton(type_frame, text="User", variable=self.type_var, value="USER").pack(side='left', padx=5)
        
        # Numéro de banque
        num_frame = ttk.Frame(self)
        num_frame.pack(pady=5)
        
        ttk.Label(num_frame, text="Numéro:").pack(side='left')
        
        self.num_var = tk.StringVar(value=str(self.source['bank_number']))
        self.num_combo = ttk.Combobox(num_frame, textvariable=self.num_var, width=5, state='readonly')
        self.num_combo.pack(side='left', padx=5)
        
        self._update_num_options()
        self.type_var.trace_add('write', lambda *args: self._update_num_options())
        
        # Boutons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="OK", command=self._on_ok).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side='left', padx=10)
    
    def _update_num_options(self):
        if self.type_var.get() == "FAVORITE":
            values = [str(i) for i in range(1, 11)]
        else:
            values = [str(i) for i in range(1, 4)]
        
        self.num_combo['values'] = values
        if self.num_var.get() not in values:
            self.num_var.set(values[0])
    
    def _on_ok(self):
        self.result = (self.type_var.get(), int(self.num_var.get()))
        self.destroy()


def main():
    """Point d'entrée principal"""
    root = tk.Tk()
    
    # Icône (si disponible)
    try:
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    app = PA4xSetMergerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
