"""
Script pour déplacer les doublons avec format aa-mm-jj vers un dossier spécial
quand le format aaaa-mm-jj existe déjà
"""
import os
import sys
import re
import shutil

# Chemins
BASE_PATH = r"C:\data\11-CHANTIERS\BURE\11-GALERIES"
DOUBLONS_PATH = r"C:\data\11-CHANTIERS\BURE\11-GALERIES\_DOUBLONS_ANNEES_COURTES"

def corriger_nom_annee(nom):
    """Convertit aa-mm-jj-*** en aaaa-mm-jj-***"""
    pattern = r'^(\d{2})-(\d{2})-(\d{2})-(.+)$'
    match = re.match(pattern, nom)
    
    if match:
        annee_courte = match.group(1)
        mois = match.group(2)
        jour = match.group(3)
        reste = match.group(4)
        
        annee_complete = f"20{annee_courte}"
        nouveau_nom = f"{annee_complete}-{mois}-{jour}-{reste}"
        return nouveau_nom
    
    return None

def trouver_doublons(galerie=None):
    """Trouve les dossiers aa-mm-jj qui ont un équivalent aaaa-mm-jj"""
    doublons = []
    
    if galerie:
        galeries = [galerie]
    else:
        galeries = [d for d in os.listdir(BASE_PATH) 
                   if os.path.isdir(os.path.join(BASE_PATH, d)) and not d.startswith('_')]
    
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
                    # Vérifier si la version aaaa-mm-jj existe
                    nouveau_path = os.path.join(categorie_path, nouveau_nom)
                    if os.path.exists(nouveau_path):
                        doublons.append({
                            'galerie': galerie_nom,
                            'categorie': categorie,
                            'ancien': dossier,
                            'nouveau': nouveau_nom,
                            'chemin_source': dossier_path,
                            'categorie_path': categorie_path
                        })
    
    return doublons

def afficher_doublons(doublons):
    """Affiche les doublons détectés"""
    if not doublons:
        print("\nAucun doublon détecté.")
        return
    
    print(f"\n{len(doublons)} doublon(s) détecté(s):\n")
    
    galerie_actuelle = None
    for d in doublons:
        if d['galerie'] != galerie_actuelle:
            galerie_actuelle = d['galerie']
            print(f"\n{galerie_actuelle}")
            print("=" * 80)
        
        print(f"  [{d['categorie']}]")
        print(f"    {d['ancien']} (existe déjà: {d['nouveau']})")

def deplacer_doublons(doublons):
    """Déplace les doublons vers le dossier spécial"""
    succes = 0
    erreurs = 0
    
    # Créer le dossier de destination s'il n'existe pas
    if not os.path.exists(DOUBLONS_PATH):
        os.makedirs(DOUBLONS_PATH)
        print(f"[CRÉÉ] {DOUBLONS_PATH}")
    
    print("\n" + "=" * 80)
    print("DÉPLACEMENT EN COURS...")
    print("=" * 80)
    
    for d in doublons:
        # Créer la structure galerie/catégorie dans le dossier doublons
        dest_galerie_path = os.path.join(DOUBLONS_PATH, d['galerie'])
        dest_categorie_path = os.path.join(dest_galerie_path, d['categorie'])
        
        try:
            # Créer les dossiers si nécessaire
            if not os.path.exists(dest_categorie_path):
                os.makedirs(dest_categorie_path)
            
            # Déplacer le dossier
            dest_path = os.path.join(dest_categorie_path, d['ancien'])
            shutil.move(d['chemin_source'], dest_path)
            print(f"[DÉPLACÉ] {d['galerie']}/{d['categorie']}/{d['ancien']}")
            succes += 1
            
        except Exception as e:
            print(f"[ERREUR] {d['ancien']}: {e}")
            erreurs += 1
    
    print("\n" + "=" * 80)
    print(f"RÉSUMÉ: {succes} déplacés, {erreurs} erreurs")
    print(f"Destination: {DOUBLONS_PATH}")
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
        print("[MODE SIMULATION] Aucun fichier ne sera déplacé")
        print("Ajoutez --execute pour effectuer les déplacements\n")
    else:
        print("[MODE EXÉCUTION] Les doublons seront déplacés\n")
    
    # Trouver les doublons
    doublons = trouver_doublons(galerie)
    
    # Afficher les doublons
    afficher_doublons(doublons)
    
    # Exécuter si demandé
    if execute and doublons:
        print(f"\nLes {len(doublons)} doublons seront déplacés vers:")
        print(f"  {DOUBLONS_PATH}")
        reponse = input("\nConfirmer le déplacement ? (oui/non): ")
        if reponse.lower() in ['oui', 'o', 'yes', 'y']:
            deplacer_doublons(doublons)
        else:
            print("Annulé.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
