"""
Modèle représentant un fichier SET Korg PA4x
Un SET est en fait un dossier avec l'extension .SET contenant:
- STYLE/ : Banques de styles (FAVORITE01-10.STY, USER01-03.STY)
- SOUND/ : Sons utilisateur (USER01.PCG)
- GLOBAL/ : Configuration globale (SETUP.GBL)
- PCM/ : Échantillons audio (RAM*.PCM)
- MULTISMP/ : Multisamples (RAM.KMP)
- PAD/ : Pads
"""

import os
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .style_bank import StyleBank, BankType


@dataclass
class SetFile:
    """
    Représente un fichier SET complet pour Korg PA4x
    """
    path: Optional[Path] = None
    name: str = "NewSet"
    
    # Banques de styles
    favorite_banks: Dict[int, StyleBank] = field(default_factory=dict)  # 1-10
    user_banks: Dict[int, StyleBank] = field(default_factory=dict)  # 1-3
    
    # Autres composants (chemins des fichiers)
    global_setup: Optional[Path] = None
    sound_files: List[Path] = field(default_factory=list)
    pcm_files: List[Path] = field(default_factory=list)
    multisample_files: List[Path] = field(default_factory=list)
    pad_files: List[Path] = field(default_factory=list)
    
    # Structure de dossiers standard
    STRUCTURE = {
        'STYLE': ['FAVORITE{:02d}.STY'.format(i) for i in range(1, 11)] + 
                 ['USER{:02d}.STY'.format(i) for i in range(1, 4)],
        'SOUND': [],
        'GLOBAL': ['SETUP.GBL'],
        'PCM': [],
        'MULTISMP': [],
        'PAD': []
    }
    
    @classmethod
    def from_directory(cls, dirpath: str | Path) -> 'SetFile':
        """Charge un SET depuis un dossier .SET"""
        dirpath = Path(dirpath)
        
        if not dirpath.exists():
            raise FileNotFoundError(f"Dossier non trouvé: {dirpath}")
        
        if not dirpath.is_dir():
            raise ValueError(f"Ce n'est pas un dossier: {dirpath}")
        
        set_file = cls(
            path=dirpath,
            name=dirpath.stem
        )
        
        # Charger les composants
        set_file._load_styles()
        set_file._load_global()
        set_file._load_sounds()
        set_file._load_pcm()
        set_file._load_multisamples()
        set_file._load_pads()
        
        return set_file
    
    @classmethod
    def create_empty(cls, name: str = "NewSet") -> 'SetFile':
        """Crée un nouveau SET vide"""
        return cls(name=name)
    
    def _load_styles(self):
        """Charge les banques de styles"""
        style_dir = self.path / "STYLE"
        
        if not style_dir.exists():
            return
        
        for sty_file in style_dir.glob("*.STY"):
            try:
                bank = StyleBank.from_file(sty_file)
                
                if bank.bank_type == BankType.FAVORITE:
                    self.favorite_banks[bank.bank_number] = bank
                else:
                    self.user_banks[bank.bank_number] = bank
                    
            except Exception as e:
                print(f"Erreur lors du chargement de {sty_file}: {e}")
    
    def _load_global(self):
        """Charge la configuration globale"""
        global_dir = self.path / "GLOBAL"
        setup_file = global_dir / "SETUP.GBL"
        
        if setup_file.exists():
            self.global_setup = setup_file
    
    def _load_sounds(self):
        """Charge les fichiers sons"""
        sound_dir = self.path / "SOUND"
        
        if sound_dir.exists():
            self.sound_files = list(sound_dir.glob("*.PCG"))
    
    def _load_pcm(self):
        """Charge les fichiers PCM"""
        pcm_dir = self.path / "PCM"
        
        if pcm_dir.exists():
            self.pcm_files = list(pcm_dir.glob("*.PCM"))
    
    def _load_multisamples(self):
        """Charge les multisamples"""
        ms_dir = self.path / "MULTISMP"
        
        if ms_dir.exists():
            self.multisample_files = list(ms_dir.glob("*.KMP"))
    
    def _load_pads(self):
        """Charge les pads"""
        pad_dir = self.path / "PAD"
        
        if pad_dir.exists():
            self.pad_files = list(pad_dir.glob("*"))
    
    def add_style_bank(self, bank: StyleBank, 
                       bank_type: Optional[BankType] = None,
                       bank_number: Optional[int] = None):
        """
        Ajoute une banque de styles au SET
        
        Args:
            bank: La banque à ajouter
            bank_type: Type de banque (écrase celui de la banque si fourni)
            bank_number: Numéro de banque (écrase celui de la banque si fourni)
        """
        btype = bank_type or bank.bank_type
        bnum = bank_number or bank.bank_number
        
        if btype == BankType.FAVORITE:
            if bnum < 1 or bnum > 10:
                raise ValueError(f"Numéro de banque Favorite invalide: {bnum} (1-10)")
            self.favorite_banks[bnum] = bank
        else:
            if bnum < 1 or bnum > 3:
                raise ValueError(f"Numéro de banque User invalide: {bnum} (1-3)")
            self.user_banks[bnum] = bank
    
    def remove_style_bank(self, bank_type: BankType, bank_number: int):
        """Supprime une banque de styles"""
        if bank_type == BankType.FAVORITE:
            if bank_number in self.favorite_banks:
                del self.favorite_banks[bank_number]
        else:
            if bank_number in self.user_banks:
                del self.user_banks[bank_number]
    
    def get_all_banks(self) -> List[StyleBank]:
        """Retourne toutes les banques de styles"""
        banks = []
        for i in range(1, 11):
            if i in self.favorite_banks:
                banks.append(self.favorite_banks[i])
        for i in range(1, 4):
            if i in self.user_banks:
                banks.append(self.user_banks[i])
        return banks
    
    def get_bank_summary(self) -> Dict[str, Any]:
        """Résumé des banques présentes"""
        summary = {
            'favorites': {},
            'users': {}
        }
        
        for i in range(1, 11):
            if i in self.favorite_banks:
                bank = self.favorite_banks[i]
                summary['favorites'][f'FAVORITE{i:02d}'] = {
                    'present': True,
                    'size': len(bank.raw_data),
                    'path': str(bank.path) if bank.path else None
                }
            else:
                summary['favorites'][f'FAVORITE{i:02d}'] = {'present': False}
        
        for i in range(1, 4):
            if i in self.user_banks:
                bank = self.user_banks[i]
                summary['users'][f'USER{i:02d}'] = {
                    'present': True,
                    'size': len(bank.raw_data),
                    'path': str(bank.path) if bank.path else None
                }
            else:
                summary['users'][f'USER{i:02d}'] = {'present': False}
        
        return summary
    
    def save(self, output_path: str | Path):
        """
        Sauvegarde le SET dans un dossier
        
        Args:
            output_path: Chemin de destination (doit finir par .SET)
        """
        output_path = Path(output_path)
        
        # S'assurer que le nom finit par .SET
        if not output_path.suffix.upper() == '.SET':
            output_path = output_path.with_suffix('.SET')
        
        # Créer la structure de dossiers
        output_path.mkdir(parents=True, exist_ok=True)
        
        style_dir = output_path / "STYLE"
        style_dir.mkdir(exist_ok=True)
        
        global_dir = output_path / "GLOBAL"
        global_dir.mkdir(exist_ok=True)
        
        # Sauvegarder les banques de styles
        for bank_num, bank in self.favorite_banks.items():
            filename = f"FAVORITE{bank_num:02d}.STY"
            bank.save(style_dir / filename)
        
        for bank_num, bank in self.user_banks.items():
            filename = f"USER{bank_num:02d}.STY"
            bank.save(style_dir / filename)
        
        # Copier le fichier GLOBAL si présent
        if self.global_setup and self.global_setup.exists():
            shutil.copy2(self.global_setup, global_dir / "SETUP.GBL")
        
        # Copier les sons si présents
        if self.sound_files:
            sound_dir = output_path / "SOUND"
            sound_dir.mkdir(exist_ok=True)
            for sound_file in self.sound_files:
                if sound_file.exists():
                    shutil.copy2(sound_file, sound_dir / sound_file.name)
        
        # Copier les PCM si présents
        if self.pcm_files:
            pcm_dir = output_path / "PCM"
            pcm_dir.mkdir(exist_ok=True)
            for pcm_file in self.pcm_files:
                if pcm_file.exists():
                    shutil.copy2(pcm_file, pcm_dir / pcm_file.name)
        
        # Copier les multisamples si présents
        if self.multisample_files:
            ms_dir = output_path / "MULTISMP"
            ms_dir.mkdir(exist_ok=True)
            for ms_file in self.multisample_files:
                if ms_file.exists():
                    shutil.copy2(ms_file, ms_dir / ms_file.name)
        
        # Copier les pads si présents
        if self.pad_files:
            pad_dir = output_path / "PAD"
            pad_dir.mkdir(exist_ok=True)
            for pad_file in self.pad_files:
                if pad_file.exists():
                    shutil.copy2(pad_file, pad_dir / pad_file.name)
        
        # Mettre à jour le chemin
        self.path = output_path
    
    def get_info(self) -> Dict[str, Any]:
        """Retourne les informations complètes sur le SET"""
        return {
            'name': self.name,
            'path': str(self.path) if self.path else None,
            'favorite_count': len(self.favorite_banks),
            'user_count': len(self.user_banks),
            'has_global': self.global_setup is not None,
            'sound_count': len(self.sound_files),
            'pcm_count': len(self.pcm_files),
            'multisample_count': len(self.multisample_files),
            'pad_count': len(self.pad_files),
            'banks': self.get_bank_summary()
        }
    
    def __repr__(self):
        return (f"SetFile({self.name}, "
                f"FAV:{len(self.favorite_banks)}/10, "
                f"USR:{len(self.user_banks)}/3)")
