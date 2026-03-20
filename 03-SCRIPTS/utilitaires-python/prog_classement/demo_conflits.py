"""
DÉMONSTRATION : Gestion des fichiers existants
Montre comment le système gère les différents cas de conflit
"""

import os
import tempfile
import shutil
from datetime import datetime

def demo_conflits():
    """Démonstration des différents types de conflits"""
    
    print("🔍 DÉMONSTRATION - GESTION DES FICHIERS EXISTANTS")
    print("="*60)
    
    # Création d'un environnement de test
    temp_dir = tempfile.mkdtemp(prefix="demo_conflits_")
    print(f"📁 Dossier de test: {temp_dir}")
    
    try:
        # Cas 1: Fichiers identiques
        print(f"\n1️⃣ CAS 1: FICHIERS IDENTIQUES")
        source_file = os.path.join(temp_dir, "source.txt")
        dest_file = os.path.join(temp_dir, "destination.txt")
        
        # Création de fichiers identiques
        with open(source_file, 'w') as f:
            f.write("Contenu identique")
        shutil.copy2(source_file, dest_file)  # Copie exacte
        
        print(f"   📄 Source: {os.path.basename(source_file)} ({os.path.getsize(source_file)} bytes)")
        print(f"   📄 Destination: {os.path.basename(dest_file)} ({os.path.getsize(dest_file)} bytes)")
        print(f"   ✅ RÉSOLUTION: Ignoré (fichiers identiques détectés par hash MD5)")
        
        # Cas 2: Fichier source plus récent
        print(f"\n2️⃣ CAS 2: SOURCE PLUS RÉCENTE")
        import time
        time.sleep(1)  # Délai pour différencier les dates
        
        with open(source_file, 'w') as f:
            f.write("Contenu modifié plus récent")
        
        stat_source = os.stat(source_file)
        stat_dest = os.stat(dest_file)
        
        print(f"   📄 Source: {datetime.fromtimestamp(stat_source.st_mtime).strftime('%H:%M:%S')}")
        print(f"   📄 Destination: {datetime.fromtimestamp(stat_dest.st_mtime).strftime('%H:%M:%S')}")
        print(f"   ✅ RÉSOLUTION: Écrasement (source plus récente)")
        
        # Cas 3: Fusion de dossiers
        print(f"\n3️⃣ CAS 3: FUSION DE DOSSIERS")
        
        source_dir = os.path.join(temp_dir, "dossier_source")
        dest_dir = os.path.join(temp_dir, "dossier_destination")
        
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Contenu différent dans chaque dossier
        with open(os.path.join(source_dir, "nouveau_fichier.txt"), 'w') as f:
            f.write("Nouveau contenu")
        
        with open(os.path.join(dest_dir, "ancien_fichier.txt"), 'w') as f:
            f.write("Ancien contenu")
        
        print(f"   📁 Source: nouveau_fichier.txt")
        print(f"   📁 Destination: ancien_fichier.txt") 
        print(f"   ✅ RÉSOLUTION: Fusion (garde les deux fichiers)")
        
        # Cas 4: Conflit complexe
        print(f"\n4️⃣ CAS 4: CONFLIT COMPLEXE")
        
        # Même nom, contenu différent, dates similaires
        common_file_source = os.path.join(source_dir, "commun.txt")
        common_file_dest = os.path.join(dest_dir, "commun.txt")
        
        with open(common_file_source, 'w') as f:
            f.write("Version source du fichier")
        
        with open(common_file_dest, 'w') as f:
            f.write("Version destination différente")
        
        print(f"   📄 Même nom, contenu différent")
        print(f"   ❓ RÉSOLUTION: Mode interactif (demande à l'utilisateur)")
        
    finally:
        # Nettoyage
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Nettoyage terminé")

def afficher_strategies():
    """Affiche les stratégies de résolution disponibles"""
    
    print(f"\n📋 STRATÉGIES DE RÉSOLUTION DISPONIBLES")
    print(f"="*50)
    
    strategies = {
        "🔄 ÉCRASEMENT": [
            "• Remplace destination par source",
            "• Backup automatique de l'ancien",
            "• Utilisé quand source est plus récent/gros"
        ],
        "🔗 FUSION": [
            "• Combine le contenu (pour dossiers)",
            "• Garde tous les fichiers",
            "• Renomme automatiquement si conflit"
        ],
        "📝 RENOMMAGE": [
            "• Garde les deux versions",
            "• Ajoute suffixe _(1), _(2), etc.",
            "• Aucune perte de données"
        ],
        "🧠 COMPARAISON": [
            "• Analyse intelligente automatique",
            "• Garde la 'meilleure' version",
            "• Basée sur date + taille + contenu"
        ],
        "👤 INTERACTIF": [
            "• Demande à l'utilisateur",
            "• Affiche toutes les informations",
            "• Contrôle total sur la décision"
        ],
        "⏭️ IGNORER": [
            "• Garde la version existante",
            "• Ne fait rien",
            "• Utilisé pour fichiers identiques"
        ]
    }
    
    for strategie, details in strategies.items():
        print(f"\n{strategie}")
        for detail in details:
            print(f"   {detail}")

def demo_workflow_complet():
    """Montre le workflow complet de gestion des conflits"""
    
    print(f"\n🔄 WORKFLOW COMPLET DE GESTION DES CONFLITS")
    print(f"="*60)
    
    workflow = [
        ("1. DÉTECTION", "Scan automatique des fichiers existants"),
        ("2. ANALYSE", "Comparaison hash, taille, date, contenu"),
        ("3. CLASSIFICATION", "Détermine le type de conflit"),
        ("4. RECOMMANDATION", "Suggère la meilleure stratégie"),
        ("5. BACKUP", "Sauvegarde automatique si écrasement"),
        ("6. RÉSOLUTION", "Applique la stratégie choisie"),
        ("7. VÉRIFICATION", "Contrôle que l'opération a réussi"),
        ("8. LOGGING", "Enregistre l'opération dans les logs")
    ]
    
    for etape, description in workflow:
        print(f"{etape:<15} → {description}")
    
    print(f"\n💡 EXEMPLE CONCRET:")
    print(f"📁 Vous avez déjà un dossier 'GALERIE GCS/IMPLANTATION'")
    print(f"📥 Le système veut y ajouter de nouveaux fichiers")
    print(f"")
    print(f"🔍 Le système va :")
    print(f"   1. Détecter que le dossier existe")
    print(f"   2. Analyser le contenu existant vs nouveau")
    print(f"   3. Proposer la fusion (garde tout)")
    print(f"   4. Faire un backup de l'existant")
    print(f"   5. Fusionner les contenus")
    print(f"   6. Logger l'opération")

if __name__ == "__main__":
    demo_conflits()
    afficher_strategies() 
    demo_workflow_complet()