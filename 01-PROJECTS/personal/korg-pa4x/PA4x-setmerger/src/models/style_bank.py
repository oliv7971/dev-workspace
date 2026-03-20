"""
Modèle représentant une banque de styles (.STY)
Une banque peut être FAVORITE01-10 ou USER01-03
"""

import os
import struct
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class BankType(Enum):
    """Type de banque de styles"""
    FAVORITE = "FAVORITE"
    USER = "USER"


@dataclass
class StyleInfo:
    """Information sur un style individuel dans une banque"""
    index: int  # Position dans la banque (0-95 typiquement)
    name: str
    offset: int  # Position dans le fichier
    size: int  # Taille des données
    
    def __repr__(self):
        return f"Style({self.index}: {self.name})"


@dataclass
class StyleBank:
    """
    Représente une banque de styles (.STY)
    Peut contenir jusqu'à 96 styles (ou plus selon version)
    """
    path: Optional[Path] = None
    bank_type: BankType = BankType.USER
    bank_number: int = 1
    styles: List[StyleInfo] = field(default_factory=list)
    raw_data: bytes = field(default_factory=bytes, repr=False)
    header_info: Dict[str, Any] = field(default_factory=dict)
    
    # Signature typique des fichiers STY Korg
    KORG_SIGNATURE = b'KORG'
    
    @property
    def filename(self) -> str:
        """Génère le nom de fichier standard"""
        return f"{self.bank_type.value}{self.bank_number:02d}.STY"
    
    @property
    def style_count(self) -> int:
        """Nombre de styles dans la banque"""
        return len(self.styles)
    
    @property
    def is_empty(self) -> bool:
        """Vérifie si la banque est vide"""
        return len(self.styles) == 0
    
    @classmethod
    def from_file(cls, filepath: str | Path) -> 'StyleBank':
        """Charge une banque depuis un fichier .STY"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {filepath}")
        
        if not filepath.suffix.upper() == '.STY':
            raise ValueError(f"Extension invalide: {filepath.suffix}")
        
        # Déterminer le type et numéro de banque depuis le nom
        bank_type, bank_number = cls._parse_filename(filepath.name)
        
        # Lire le fichier binaire
        with open(filepath, 'rb') as f:
            raw_data = f.read()
        
        bank = cls(
            path=filepath,
            bank_type=bank_type,
            bank_number=bank_number,
            raw_data=raw_data
        )
        
        # Parser le contenu
        bank._parse_content()
        
        return bank
    
    @staticmethod
    def _parse_filename(filename: str) -> tuple[BankType, int]:
        """Parse le nom de fichier pour extraire type et numéro"""
        name = filename.upper().replace('.STY', '')
        
        if name.startswith('FAVORITE'):
            return BankType.FAVORITE, int(name[8:])
        elif name.startswith('USER'):
            return BankType.USER, int(name[4:])
        else:
            # Fichier STY isolé, on l'assigne à USER01 par défaut
            return BankType.USER, 1
    
    def _parse_content(self):
        """Parse le contenu binaire du fichier STY"""
        if not self.raw_data:
            return
        
        # Vérifier la signature Korg
        if len(self.raw_data) >= 4:
            header = self.raw_data[:4]
            self.header_info['signature'] = header
            
            # Recherche de la signature KORG
            if self.KORG_SIGNATURE in self.raw_data[:16]:
                self.header_info['is_korg'] = True
            else:
                self.header_info['is_korg'] = False
        
        # Taille du fichier
        self.header_info['file_size'] = len(self.raw_data)
        
        # Parser les styles individuels
        # La structure exacte dépend du format - on fait une analyse basique
        self._extract_style_names()
    
    def _extract_style_names(self):
        """Extrait les noms des styles du fichier"""
        # Les noms de styles sont généralement des chaînes ASCII/UTF-8
        # terminées par des null bytes, souvent alignées sur des blocs
        
        # Recherche de patterns de noms dans les données
        # Format typique: bloc de 16-32 caractères pour chaque nom
        
        data = self.raw_data
        styles = []
        
        # Méthode heuristique: chercher des séquences de caractères imprimables
        # suivies de null bytes (padding)
        
        # Pour l'instant, on extrait juste les infos de base
        # Une analyse plus poussée nécessite des fichiers de référence
        
        self.styles = styles
    
    def save(self, filepath: str | Path):
        """Sauvegarde la banque dans un fichier"""
        filepath = Path(filepath)
        
        with open(filepath, 'wb') as f:
            f.write(self.raw_data)
    
    def get_info(self) -> Dict[str, Any]:
        """Retourne les informations sur la banque"""
        return {
            'filename': self.filename,
            'type': self.bank_type.value,
            'number': self.bank_number,
            'style_count': self.style_count,
            'file_size': len(self.raw_data),
            'is_korg': self.header_info.get('is_korg', False),
            'path': str(self.path) if self.path else None
        }
    
    def __repr__(self):
        return f"StyleBank({self.filename}, {self.style_count} styles)"
