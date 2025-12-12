"""
Script pour corriger les noms de dossiers avec format aa-mm-jj en aaaa-mm-jj
"""
import os
import sys
import re

# Chemin de base
BASE_PATH = r"C:\data\11-CHANTIERS\BURE\11-GALERIES"

def corriger_nom_annee(nom):
    """
    Convertit aa-mm-jj-*** en aaaa-mm-jj-***
    Les deux premiers chiffres avant le premier - représentent l'année
    """
    # Pattern pour détecter aa-mm-jj au début
    pattern = r'^(\d{2})-(\d{2})-(\d{2})-(.+)$'
    match = re.match(pattern, nom)
    
    if match:
        annee_courte = match.group(1)
        mois = match.group(2)
        jour = match.group(3)
        reste = match.group(4)
        
        # Conversion aa -> aaaa (20aa)
        annee_complete = f"20{annee_courte}"
        
        nouveau_nom = f"{annee_complete}-{mois}-{jour}-{reste}"
        return nouveau_nom
    
    return None

def analyser_dossiers(galerie=None):
    """Analyse les dossiers avec format année courte"""
    dossiers_a_corriger = []
    
    if galerie:
        # Analyse une galerie spécifique
        galeries = [galerie]
    else:
        # Analyse toutes les galeries
        galeries = [d for d in os.listdir(BASE_PATH) 
                   if os.path.isdir(os.path.join(BASE_PATH, d))]
    
    for galerie_nom in galeries:
        galerie_path = os.path.join(BASE_PATH, galerie_nom)
        if not os.path.isdir(galerie_path):
            continue
        
        # Parcourir les catégories
        for categorie in os.listdir(galerie_path):
            categorie_path = os.path.join(galerie_path, categorie)
            if not os.path.isdir(categorie_path):
                continue
            
            # Parcourir les dossiers
            for dossier in os.listdir(categorie_path):
                dossier_path = os.path.join(categorie_path, dossier)
                if not os.path.isdir(dossier_path):
                    continue
                
                nouveau_nom = corriger_nom_annee(dossier)
                if nouveau_nom:
                    dossiers_a_corriger.append({
                        'galerie': galerie_nom,
                        'categorie': categorie,
                        'ancien': dossier,
                        'nouveau': nouveau_nom,
                        'chemin': categorie_path
                    })
    
    return dossiers_a_corriger

def afficher_corrections(dossiers):
    """Affiche les corrections à effectuer"""
    if not dossiers:
        print("\nAucun dossier à corriger trouvé.")
        return
    
    print(f"\n{len(dossiers)} dossier(s) à corriger:\n")
    
    galerie_actuelle = None
    for d in dossiers:
        if d['galerie'] != galerie_actuelle:
            galerie_actuelle = d['galerie']
            print(f"\n{galerie_actuelle}")
            print("=" * 80)
        
        print(f"  [{d['categorie']}]")
        print(f"    {d['ancien']}")
        print(f"    → {d['nouveau']}")

def executer_corrections(dossiers):
    """Effectue les renommages"""
    succes = 0
    erreurs = 0
    
    print("\n" + "=" * 80)
    print("RENOMMAGE EN COURS...")
    print("=" * 80)
    
    for d in dossiers:
        ancien_path = os.path.join(d['chemin'], d['ancien'])
        nouveau_path = os.path.join(d['chemin'], d['nouveau'])
        
        try:
            # Vérifier si la destination existe déjà
            if os.path.exists(nouveau_path):
                print(f"[ERREUR] Destination existe déjà: {d['nouveau']}")
                erreurs += 1
                continue
            
            os.rename(ancien_path, nouveau_path)
            print(f"[RENOMMÉ] {d['ancien']} → {d['nouveau']}")
            succes += 1
            
        except Exception as e:
            print(f"[ERREUR] {d['ancien']}: {e}")
            erreurs += 1
    
    print("\n" + "=" * 80)
    print(f"RÉSUMÉ: {succes} renommés, {erreurs} erreurs")
    print("=" * 80)

def main():
    # Vérifier les arguments
    execute = "--execute" in sys.argv
    galerie = None
    
    for arg in sys.argv[1:]:
        if arg != "--execute" and not arg.startswith("-"):
            galerie = arg
            break
    
    if not execute:
        print("[MODE SIMULATION] Aucun fichier ne sera renommé")
        print("Ajoutez --execute pour effectuer les renommages\n")
    else:
        print("[MODE EXÉCUTION] Les fichiers seront renommés\n")
    
    # Analyser les dossiers
    dossiers = analyser_dossiers(galerie)
    
    # Afficher les corrections
    afficher_corrections(dossiers)
    
    # Exécuter si demandé
    if execute and dossiers:
        reponse = input("\nConfirmer le renommage de ces dossiers ? (oui/non): ")
        if reponse.lower() in ['oui', 'o', 'yes', 'y']:
            executer_corrections(dossiers)
        else:
            print("Annulé.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
