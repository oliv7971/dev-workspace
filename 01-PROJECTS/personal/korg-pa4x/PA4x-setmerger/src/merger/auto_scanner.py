"""
Mode automatique pour PA4x Set Merger
Scanne les répertoires et génère automatiquement des SET
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable
from enum import Enum
from collections import defaultdict

from ..models.style_bank import StyleBank, BankType
from ..models.set_file import SetFile


class GroupingStrategy(Enum):
    """Stratégie de regroupement des styles"""
    BY_FOLDER = "by_folder"           # Un SET par dossier contenant des STY
    BY_PARENT_FOLDER = "by_parent"    # Un SET par dossier parent
    BY_PREFIX = "by_prefix"           # Regrouper par préfixe de nom (ex: "Dance_*.STY")
    BY_PATTERN = "by_pattern"         # Regrouper par pattern regex
    SINGLE_SET = "single_set"         # Tout dans un seul SET
    SMART = "smart"                   # Détection intelligente


@dataclass
class ScanResult:
    """Résultat d'un scan de répertoire"""
    path: Path
    sty_files: List[Path] = field(default_factory=list)
    set_folders: List[Path] = field(default_factory=list)
    subdirectories: List['ScanResult'] = field(default_factory=list)
    
    @property
    def total_sty_count(self) -> int:
        """Nombre total de fichiers STY (récursif)"""
        count = len(self.sty_files)
        for subdir in self.subdirectories:
            count += subdir.total_sty_count
        return count
    
    @property
    def has_content(self) -> bool:
        return len(self.sty_files) > 0 or len(self.set_folders) > 0


@dataclass
class SetGenerationPlan:
    """Plan de génération d'un SET"""
    name: str
    output_path: Path
    sources: List[Tuple[Path, BankType, int]]  # (path, type, numéro)
    source_folder: Optional[Path] = None
    
    @property
    def favorite_count(self) -> int:
        return sum(1 for _, bt, _ in self.sources if bt == BankType.FAVORITE)
    
    @property
    def user_count(self) -> int:
        return sum(1 for _, bt, _ in self.sources if bt == BankType.USER)


class AutoScanner:
    """
    Scanner automatique de répertoires pour générer des SET
    """
    
    # Extensions reconnues
    STY_EXTENSION = '.STY'
    SET_EXTENSION = '.SET'
    
    def __init__(self):
        self.scan_results: List[ScanResult] = []
        self.generation_plans: List[SetGenerationPlan] = []
        self.progress_callback: Optional[Callable[[str, int, int], None]] = None
        
        # Configuration
        self.grouping_strategy = GroupingStrategy.SMART
        self.recursive = True
        self.include_existing_sets = True
        self.output_base_path: Optional[Path] = None
        self.set_name_prefix = ""
        self.set_name_suffix = ""
        
        # Statistiques
        self.stats = {
            'scanned_folders': 0,
            'found_sty': 0,
            'found_sets': 0,
            'generated_sets': 0,
            'errors': []
        }
    
    def set_progress_callback(self, callback: Callable[[str, int, int], None]):
        """Définit un callback pour le suivi de progression"""
        self.progress_callback = callback
    
    def _report_progress(self, message: str, current: int = 0, total: int = 0):
        """Rapporte la progression"""
        if self.progress_callback:
            self.progress_callback(message, current, total)
    
    def scan_directory(self, root_path: str | Path, recursive: bool = True) -> ScanResult:
        """
        Scanne un répertoire à la recherche de fichiers STY et SET
        
        Args:
            root_path: Chemin racine à scanner
            recursive: Scanner récursivement les sous-dossiers
        
        Returns:
            Résultat du scan
        """
        root_path = Path(root_path)
        
        if not root_path.exists():
            raise FileNotFoundError(f"Répertoire non trouvé: {root_path}")
        
        self._report_progress(f"Scan: {root_path.name}")
        self.stats['scanned_folders'] += 1
        
        result = ScanResult(path=root_path)
        
        try:
            for item in root_path.iterdir():
                if item.is_file():
                    if item.suffix.upper() == self.STY_EXTENSION:
                        result.sty_files.append(item)
                        self.stats['found_sty'] += 1
                
                elif item.is_dir():
                    # Vérifier si c'est un dossier .SET
                    if item.suffix.upper() == self.SET_EXTENSION:
                        result.set_folders.append(item)
                        self.stats['found_sets'] += 1
                        
                        # Scanner aussi l'intérieur du SET pour les STY
                        if self.include_existing_sets:
                            style_dir = item / "STYLE"
                            if style_dir.exists():
                                for sty in style_dir.glob("*.STY"):
                                    result.sty_files.append(sty)
                                    self.stats['found_sty'] += 1
                    
                    elif recursive:
                        # Scanner récursivement
                        sub_result = self.scan_directory(item, recursive=True)
                        if sub_result.has_content or sub_result.subdirectories:
                            result.subdirectories.append(sub_result)
        
        except PermissionError:
            self.stats['errors'].append(f"Accès refusé: {root_path}")
        
        return result
    
    def analyze_and_plan(self, scan_result: ScanResult, 
                         strategy: Optional[GroupingStrategy] = None) -> List[SetGenerationPlan]:
        """
        Analyse les résultats du scan et crée un plan de génération
        
        Args:
            scan_result: Résultat du scan
            strategy: Stratégie de regroupement (utilise self.grouping_strategy si None)
        
        Returns:
            Liste des plans de génération
        """
        strategy = strategy or self.grouping_strategy
        
        if strategy == GroupingStrategy.SMART:
            return self._plan_smart(scan_result)
        elif strategy == GroupingStrategy.BY_FOLDER:
            return self._plan_by_folder(scan_result)
        elif strategy == GroupingStrategy.BY_PARENT_FOLDER:
            return self._plan_by_parent(scan_result)
        elif strategy == GroupingStrategy.SINGLE_SET:
            return self._plan_single_set(scan_result)
        elif strategy == GroupingStrategy.BY_PREFIX:
            return self._plan_by_prefix(scan_result)
        else:
            return self._plan_smart(scan_result)
    
    def _plan_smart(self, scan_result: ScanResult) -> List[SetGenerationPlan]:
        """
        Stratégie intelligente:
        - Si un dossier contient des FAVORITE*.STY ou USER*.STY → un SET
        - Si un dossier contient des STY nommés autrement → les regrouper intelligemment
        - Respecter la structure existante
        - Créer plusieurs SET si trop de fichiers
        """
        plans = []
        
        def process_result(result: ScanResult, depth: int = 0):
            if result.sty_files:
                # Analyser les fichiers STY de ce dossier
                favorites = []
                users = []
                others = []
                
                for sty in result.sty_files:
                    name = sty.stem.upper()
                    if name.startswith('FAVORITE'):
                        try:
                            num = int(name[8:])
                            favorites.append((sty, num))
                        except:
                            others.append(sty)
                    elif name.startswith('USER'):
                        try:
                            num = int(name[4:])
                            users.append((sty, num))
                        except:
                            others.append(sty)
                    else:
                        others.append(sty)
                
                # Si on a des FAVORITE/USER, c'est déjà structuré → un SET (ou plus)
                if favorites or users:
                    new_plans = self._create_plan_from_structured(
                        result.path, favorites, users, others
                    )
                    plans.extend(new_plans)
                
                # Si on a que des "autres", les regrouper
                elif others:
                    new_plans = self._create_plan_from_unstructured(result.path, others)
                    plans.extend(new_plans)
            
            # Traiter les sous-dossiers
            for subdir in result.subdirectories:
                process_result(subdir, depth + 1)
        
        process_result(scan_result)
        return plans
    
    def _create_plan_from_structured(self, folder: Path, 
                                      favorites: List[Tuple[Path, int]],
                                      users: List[Tuple[Path, int]],
                                      others: List[Path]) -> List[SetGenerationPlan]:
        """Crée un ou plusieurs plans à partir de fichiers déjà structurés (FAVORITE/USER)"""
        sources = []
        
        # Ajouter les favorites
        for path, num in sorted(favorites, key=lambda x: x[1]):
            if 1 <= num <= 10:
                sources.append((path, BankType.FAVORITE, num))
        
        # Ajouter les users
        for path, num in sorted(users, key=lambda x: x[1]):
            if 1 <= num <= 3:
                sources.append((path, BankType.USER, num))
        
        # Ajouter les autres dans les slots libres
        used_fav = {num for _, num in favorites if 1 <= num <= 10}
        used_usr = {num for _, num in users if 1 <= num <= 3}
        
        remaining_others = []
        for other in others:
            placed = False
            # Chercher un slot libre dans Favorites
            for i in range(1, 11):
                if i not in used_fav:
                    sources.append((other, BankType.FAVORITE, i))
                    used_fav.add(i)
                    placed = True
                    break
            
            if not placed:
                # Chercher un slot libre dans Users
                for i in range(1, 4):
                    if i not in used_usr:
                        sources.append((other, BankType.USER, i))
                        used_usr.add(i)
                        placed = True
                        break
            
            if not placed:
                # Plus de place, garder pour un autre SET
                remaining_others.append(other)
        
        if not sources:
            return []
        
        # Nom du SET basé sur le dossier
        set_name = self._generate_set_name(folder)
        output_path = self._get_output_path(folder, set_name)
        
        plans = [SetGenerationPlan(
            name=set_name,
            output_path=output_path,
            sources=sources,
            source_folder=folder
        )]
        
        # Si des fichiers restent, créer des SET supplémentaires
        if remaining_others:
            extra_plans = self._create_plan_from_unstructured(folder, remaining_others)
            # Renommer les plans supplémentaires
            for i, plan in enumerate(extra_plans):
                plan.name = f"{set_name}_Extra{i + 1}"
                plan.output_path = self._get_output_path(folder, plan.name)
            plans.extend(extra_plans)
        
        return plans
    
    def _create_plan_from_unstructured(self, folder: Path, 
                                        sty_files: List[Path]) -> List[SetGenerationPlan]:
        """Crée un ou plusieurs plans à partir de fichiers STY non structurés"""
        if not sty_files:
            return []
        
        plans = []
        sorted_files = sorted(sty_files, key=lambda x: x.name)
        
        # Maximum 13 banques par SET (10 FAV + 3 USER)
        MAX_PER_SET = 13
        
        # Diviser en chunks si nécessaire
        chunks = [sorted_files[i:i + MAX_PER_SET] for i in range(0, len(sorted_files), MAX_PER_SET)]
        
        for chunk_idx, chunk in enumerate(chunks):
            sources = []
            fav_num = 1
            user_num = 1
            
            for sty in chunk:
                if fav_num <= 10:
                    sources.append((sty, BankType.FAVORITE, fav_num))
                    fav_num += 1
                elif user_num <= 3:
                    sources.append((sty, BankType.USER, user_num))
                    user_num += 1
            
            # Nom du SET avec suffixe si plusieurs parties
            base_name = self._generate_set_name(folder)
            if len(chunks) > 1:
                set_name = f"{base_name}_Part{chunk_idx + 1}"
            else:
                set_name = base_name
            
            output_path = self._get_output_path(folder, set_name)
            
            plan = SetGenerationPlan(
                name=set_name,
                output_path=output_path,
                sources=sources,
                source_folder=folder
            )
            plans.append(plan)
        
        return plans
    
    def _plan_by_folder(self, scan_result: ScanResult) -> List[SetGenerationPlan]:
        """Un SET (ou plusieurs) par dossier contenant des STY"""
        plans = []
        
        def process(result: ScanResult):
            if result.sty_files:
                new_plans = self._create_plan_from_unstructured(result.path, result.sty_files)
                plans.extend(new_plans)
            
            for subdir in result.subdirectories:
                process(subdir)
        
        process(scan_result)
        return plans
    
    def _plan_by_parent(self, scan_result: ScanResult) -> List[SetGenerationPlan]:
        """Regroupe les STY par dossier parent"""
        # Collecter tous les STY par dossier parent
        by_parent: Dict[Path, List[Path]] = defaultdict(list)
        
        def collect(result: ScanResult):
            for sty in result.sty_files:
                parent = sty.parent
                # Si c'est dans un dossier STYLE, prendre le grand-parent
                if parent.name.upper() == "STYLE":
                    parent = parent.parent
                by_parent[parent].append(sty)
            
            for subdir in result.subdirectories:
                collect(subdir)
        
        collect(scan_result)
        
        plans = []
        for parent_folder, sty_files in by_parent.items():
            new_plans = self._create_plan_from_unstructured(parent_folder, sty_files)
            plans.extend(new_plans)
        
        return plans
    
    def _plan_single_set(self, scan_result: ScanResult) -> List[SetGenerationPlan]:
        """Tout dans un ou plusieurs SET"""
        all_sty = []
        
        def collect(result: ScanResult):
            all_sty.extend(result.sty_files)
            for subdir in result.subdirectories:
                collect(subdir)
        
        collect(scan_result)
        
        if not all_sty:
            return []
        
        # Créer autant de SET que nécessaire
        return self._create_plan_from_unstructured(scan_result.path, all_sty)
    
    def _plan_by_prefix(self, scan_result: ScanResult) -> List[SetGenerationPlan]:
        """Regroupe par préfixe de nom de fichier"""
        all_sty = []
        
        def collect(result: ScanResult):
            all_sty.extend(result.sty_files)
            for subdir in result.subdirectories:
                collect(subdir)
        
        collect(scan_result)
        
        # Extraire les préfixes (premier mot ou avant le premier chiffre/underscore)
        by_prefix: Dict[str, List[Path]] = defaultdict(list)
        
        for sty in all_sty:
            name = sty.stem
            # Extraire le préfixe
            match = re.match(r'^([A-Za-z]+)', name)
            prefix = match.group(1) if match else "Other"
            by_prefix[prefix].append(sty)
        
        plans = []
        for prefix, files in by_prefix.items():
            if files:
                new_plans = self._create_plan_from_unstructured(
                    scan_result.path / prefix, files
                )
                # Renommer les plans avec le préfixe
                for i, plan in enumerate(new_plans):
                    if len(new_plans) > 1:
                        plan.name = f"{self.set_name_prefix}{prefix}{self.set_name_suffix}_Part{i + 1}"
                    else:
                        plan.name = f"{self.set_name_prefix}{prefix}{self.set_name_suffix}"
                    plan.output_path = self._get_output_path(scan_result.path, plan.name)
                plans.extend(new_plans)
        
        return plans
    
    def _generate_set_name(self, folder: Path) -> str:
        """Génère un nom de SET basé sur le dossier"""
        name = folder.stem
        
        # Nettoyer le nom
        name = re.sub(r'[^\w\s-]', '', name)
        name = name.strip()
        
        # Appliquer préfixe/suffixe
        name = f"{self.set_name_prefix}{name}{self.set_name_suffix}"
        
        # Limiter la longueur
        if len(name) > 30:
            name = name[:30]
        
        return name or "GeneratedSet"
    
    def _get_output_path(self, source_folder: Path, set_name: str) -> Path:
        """Détermine le chemin de sortie pour un SET"""
        if self.output_base_path:
            return self.output_base_path / f"{set_name}.SET"
        else:
            # Créer à côté du dossier source
            return source_folder.parent / f"{set_name}.SET"
    
    def execute_plans(self, plans: Optional[List[SetGenerationPlan]] = None,
                      dry_run: bool = False) -> List[Tuple[SetGenerationPlan, bool, str]]:
        """
        Exécute les plans de génération
        
        Args:
            plans: Liste des plans à exécuter (utilise self.generation_plans si None)
            dry_run: Si True, ne crée pas les fichiers, juste simule
        
        Returns:
            Liste de tuples (plan, succès, message)
        """
        plans = plans or self.generation_plans
        results = []
        
        for i, plan in enumerate(plans):
            self._report_progress(f"Génération: {plan.name}", i + 1, len(plans))
            
            try:
                if dry_run:
                    results.append((plan, True, f"[DRY-RUN] {plan.name} serait créé"))
                    continue
                
                # Créer le SET
                new_set = SetFile.create_empty(plan.name)
                
                for source_path, bank_type, bank_num in plan.sources:
                    try:
                        bank = StyleBank.from_file(source_path)
                        new_set.add_style_bank(bank, bank_type, bank_num)
                    except Exception as e:
                        self.stats['errors'].append(f"Erreur chargement {source_path}: {e}")
                
                # Sauvegarder
                new_set.save(plan.output_path)
                self.stats['generated_sets'] += 1
                
                results.append((plan, True, f"Créé: {plan.output_path}"))
                
            except Exception as e:
                self.stats['errors'].append(f"Erreur génération {plan.name}: {e}")
                results.append((plan, False, str(e)))
        
        return results
    
    def get_summary(self) -> Dict:
        """Retourne un résumé des statistiques"""
        return {
            'scanned_folders': self.stats['scanned_folders'],
            'found_sty': self.stats['found_sty'],
            'found_sets': self.stats['found_sets'],
            'planned_sets': len(self.generation_plans),
            'generated_sets': self.stats['generated_sets'],
            'errors': len(self.stats['errors']),
            'error_details': self.stats['errors']
        }
    
    def reset(self):
        """Remet à zéro le scanner"""
        self.scan_results = []
        self.generation_plans = []
        self.stats = {
            'scanned_folders': 0,
            'found_sty': 0,
            'found_sets': 0,
            'generated_sets': 0,
            'errors': []
        }


def auto_generate_sets(source_path: str | Path,
                       output_path: Optional[str | Path] = None,
                       strategy: GroupingStrategy = GroupingStrategy.SMART,
                       recursive: bool = True,
                       dry_run: bool = False) -> Dict:
    """
    Fonction utilitaire pour générer automatiquement des SET
    
    Args:
        source_path: Chemin source à scanner
        output_path: Chemin de sortie (si None, crée à côté des sources)
        strategy: Stratégie de regroupement
        recursive: Scanner récursivement
        dry_run: Mode simulation
    
    Returns:
        Dictionnaire avec les statistiques et résultats
    """
    scanner = AutoScanner()
    scanner.recursive = recursive
    scanner.grouping_strategy = strategy
    
    if output_path:
        scanner.output_base_path = Path(output_path)
    
    # Scanner
    scan_result = scanner.scan_directory(source_path, recursive)
    
    # Planifier
    scanner.generation_plans = scanner.analyze_and_plan(scan_result)
    
    # Exécuter
    results = scanner.execute_plans(dry_run=dry_run)
    
    return {
        'summary': scanner.get_summary(),
        'plans': scanner.generation_plans,
        'results': results
    }
