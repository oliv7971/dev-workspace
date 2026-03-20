"""
Logique de fusion des fichiers SET et STY pour Korg PA4x
"""

from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum
from dataclasses import dataclass

from ..models.style_bank import StyleBank, BankType
from ..models.set_file import SetFile


class ConflictResolution(Enum):
    """Stratégie de résolution des conflits"""
    OVERWRITE = "overwrite"  # Écraser l'existant
    SKIP = "skip"  # Garder l'existant
    RENAME = "rename"  # Décaler vers un slot libre
    ASK = "ask"  # Demander à l'utilisateur


@dataclass
class MergeOperation:
    """Représente une opération de fusion"""
    source: Path
    source_type: str  # "STY" ou "SET"
    target_bank_type: BankType
    target_bank_number: int
    has_conflict: bool = False
    status: str = "pending"  # pending, completed, skipped, error
    message: str = ""


class SetMerger:
    """
    Gestionnaire de fusion pour les fichiers SET et STY
    """
    
    def __init__(self):
        self.target_set: Optional[SetFile] = None
        self.operations: List[MergeOperation] = []
        self.conflict_resolution: ConflictResolution = ConflictResolution.ASK
    
    def create_new_target(self, name: str = "MergedSet") -> SetFile:
        """Crée un nouveau SET cible vide"""
        self.target_set = SetFile.create_empty(name)
        return self.target_set
    
    def load_target(self, set_path: str | Path) -> SetFile:
        """Charge un SET existant comme cible"""
        self.target_set = SetFile.from_directory(Path(set_path))
        return self.target_set
    
    def add_sty_file(self, sty_path: str | Path, 
                     bank_type: Optional[BankType] = None,
                     bank_number: Optional[int] = None) -> MergeOperation:
        """
        Ajoute un fichier STY à la liste des opérations
        
        Args:
            sty_path: Chemin vers le fichier .STY
            bank_type: Type de banque cible (si None, déduit du nom)
            bank_number: Numéro de banque cible (si None, déduit du nom)
        
        Returns:
            L'opération de fusion créée
        """
        sty_path = Path(sty_path)
        
        # Charger la banque pour déterminer son type
        bank = StyleBank.from_file(sty_path)
        
        # Utiliser les valeurs fournies ou celles de la banque
        target_type = bank_type or bank.bank_type
        target_num = bank_number or bank.bank_number
        
        # Vérifier les conflits
        has_conflict = self._check_conflict(target_type, target_num)
        
        operation = MergeOperation(
            source=sty_path,
            source_type="STY",
            target_bank_type=target_type,
            target_bank_number=target_num,
            has_conflict=has_conflict
        )
        
        self.operations.append(operation)
        return operation
    
    def add_set_directory(self, set_path: str | Path) -> List[MergeOperation]:
        """
        Ajoute toutes les banques d'un SET à la liste des opérations
        
        Args:
            set_path: Chemin vers le dossier .SET
        
        Returns:
            Liste des opérations créées
        """
        set_path = Path(set_path)
        source_set = SetFile.from_directory(set_path)
        
        operations = []
        
        # Ajouter les banques Favorites
        for bank_num, bank in source_set.favorite_banks.items():
            if bank.path:
                op = self.add_sty_file(bank.path, BankType.FAVORITE, bank_num)
                operations.append(op)
        
        # Ajouter les banques User
        for bank_num, bank in source_set.user_banks.items():
            if bank.path:
                op = self.add_sty_file(bank.path, BankType.USER, bank_num)
                operations.append(op)
        
        return operations
    
    def add_sty_directory(self, dir_path: str | Path) -> List[MergeOperation]:
        """
        Ajoute tous les fichiers STY d'un répertoire
        
        Args:
            dir_path: Chemin vers le répertoire contenant des .STY
        
        Returns:
            Liste des opérations créées
        """
        dir_path = Path(dir_path)
        operations = []
        
        for sty_file in sorted(dir_path.glob("*.STY")):
            op = self.add_sty_file(sty_file)
            operations.append(op)
        
        return operations
    
    def _check_conflict(self, bank_type: BankType, bank_number: int) -> bool:
        """Vérifie s'il y a un conflit avec une banque existante"""
        if self.target_set is None:
            return False
        
        if bank_type == BankType.FAVORITE:
            return bank_number in self.target_set.favorite_banks
        else:
            return bank_number in self.target_set.user_banks
    
    def find_free_slot(self, bank_type: BankType) -> Optional[int]:
        """Trouve le premier slot libre pour un type de banque"""
        if self.target_set is None:
            return 1
        
        if bank_type == BankType.FAVORITE:
            for i in range(1, 11):
                if i not in self.target_set.favorite_banks:
                    return i
        else:
            for i in range(1, 4):
                if i not in self.target_set.user_banks:
                    return i
        
        return None
    
    def get_available_slots(self) -> Dict[str, List[int]]:
        """Retourne les slots disponibles"""
        slots = {
            'favorites': [],
            'users': []
        }
        
        if self.target_set is None:
            slots['favorites'] = list(range(1, 11))
            slots['users'] = list(range(1, 4))
            return slots
        
        for i in range(1, 11):
            if i not in self.target_set.favorite_banks:
                slots['favorites'].append(i)
        
        for i in range(1, 4):
            if i not in self.target_set.user_banks:
                slots['users'].append(i)
        
        return slots
    
    def reassign_operation(self, operation: MergeOperation,
                          new_type: BankType, new_number: int):
        """Réassigne une opération à un nouveau slot"""
        operation.target_bank_type = new_type
        operation.target_bank_number = new_number
        operation.has_conflict = self._check_conflict(new_type, new_number)
    
    def execute_merge(self, 
                      conflict_resolution: Optional[ConflictResolution] = None
                      ) -> Tuple[int, int, List[str]]:
        """
        Exécute toutes les opérations de fusion
        
        Args:
            conflict_resolution: Stratégie de résolution des conflits
        
        Returns:
            Tuple (succès, échecs, messages)
        """
        if self.target_set is None:
            self.create_new_target()
        
        resolution = conflict_resolution or self.conflict_resolution
        
        success = 0
        failed = 0
        messages = []
        
        for op in self.operations:
            try:
                if op.has_conflict:
                    if resolution == ConflictResolution.SKIP:
                        op.status = "skipped"
                        op.message = f"Conflit ignoré: {op.target_bank_type.value}{op.target_bank_number:02d}"
                        messages.append(op.message)
                        continue
                    
                    elif resolution == ConflictResolution.RENAME:
                        # Trouver un slot libre
                        free_slot = self.find_free_slot(op.target_bank_type)
                        if free_slot is None:
                            op.status = "error"
                            op.message = f"Pas de slot libre pour {op.target_bank_type.value}"
                            messages.append(op.message)
                            failed += 1
                            continue
                        
                        op.target_bank_number = free_slot
                        op.has_conflict = False
                
                # Charger et ajouter la banque
                bank = StyleBank.from_file(op.source)
                self.target_set.add_style_bank(
                    bank, 
                    op.target_bank_type, 
                    op.target_bank_number
                )
                
                op.status = "completed"
                op.message = f"Ajouté: {op.source.name} → {op.target_bank_type.value}{op.target_bank_number:02d}"
                messages.append(op.message)
                success += 1
                
            except Exception as e:
                op.status = "error"
                op.message = f"Erreur: {op.source.name} - {str(e)}"
                messages.append(op.message)
                failed += 1
        
        return success, failed, messages
    
    def clear_operations(self):
        """Efface toutes les opérations en attente"""
        self.operations = []
    
    def get_operations_summary(self) -> Dict[str, Any]:
        """Résumé des opérations"""
        return {
            'total': len(self.operations),
            'pending': sum(1 for op in self.operations if op.status == 'pending'),
            'completed': sum(1 for op in self.operations if op.status == 'completed'),
            'skipped': sum(1 for op in self.operations if op.status == 'skipped'),
            'errors': sum(1 for op in self.operations if op.status == 'error'),
            'conflicts': sum(1 for op in self.operations if op.has_conflict),
        }
