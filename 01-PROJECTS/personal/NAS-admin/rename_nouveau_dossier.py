"""
Renommage des dossiers 'Nouveau dossier' dans 21-CERENE.
Noms choisis en fonction du contenu.

Usage:
    python rename_nouveau_dossier.py            # dry-run
    python rename_nouveau_dossier.py --execute  # renommage réel
"""
import os
import sys

EXECUTE = "--execute" in sys.argv
NAS = "\\\\Nas_travail\\01-ds414-data\\21-CERENE"

# (chemin_actuel_relatif, nouveau_nom)
RENAMES = [
    # 49 Mo - contient Gavalet.dwg, Hta-a.shp → données réseau HTA Gavalet
    ("02-AFFAIRES\\ACAD\\DWG\\Nouveau dossier", "Gavalet-HTA"),
    
    # 1.1 Mo - 82 styles/blocs DWG Graniou
    ("02-AFFAIRES\\Graniou\\Styles\\Nouveau dossier", "Blocs-Graniou"),
    
    # 3.9 Mo - base Access mobile.mdb + requêtes
    ("02-AFFAIRES\\PhoneSignalTracking\\Doc\\Nouveau dossier", "Base-Requetes"),
    
    # 3.4 Mo - plans topo SDIS77 en PDF
    ("02-AFFAIRES\\SDIS\\Plot\\PDF\\100216\\Nouveau dossier", "Plans-SDIS77"),
    
    # 0.9 Ko - juste un raccourci .lnk → supprimer le dossier serait mieux
    # mais on le renomme quand même pour cohérence
    ("02-AFFAIRES\\Scan-3D\\Nouveau dossier", "raccourci-batiment"),
    
    # 1.3 Ko - code VB DrawOnTheMap
    ("02-AFFAIRES\\SuperGIS\\prog\\vb\\Nouveau dossier", "DrawOnMap"),
    
    # 82 Ko - Loisy-Cad1.dwg
    ("02-AFFAIRES\\Topo\\Loisy\\Livraison\\Nouveau dossier", "Cadastre"),
    
    # 26 Mo - photos panoramiques station s58
    ("03-PROJETS\\metz-gare\\photos metz\\photos\\s58\\Nouveau dossier", "panoramas"),
    
    # 26 Mo - photos panoramiques intérieur hall gare
    ("03-PROJETS\\metz-gare\\photos\\interieur_hall_gare\\Nouveau dossier", "panoramas"),
    
    # 1.5 Ko - messages SBD satellite
    ("03-PROJETS\\projet_geosiara-2011102\\cle_20070507\\documents\\tempsbd\\Nouveau dossier", "messages-SBD"),
    
    # 2.9 Mo - outils firmware AVL Colombia
    ("10-SERVEURS\\12-SERVEUR MOZART02\\mozart02\\projet_geosiara-2011102\\001 Fournisseur\\AVL\\AVL de Colombia\\firmware\\firmware\\Nouveau dossier", "outils-programmation"),
    
    # 4 Ko - header C geonode.h
    ("10-SERVEURS\\12-SERVEUR MOZART02\\mozart02\\projet_geosiara-2011102\\001 Fournisseur\\AVL\\LatitudeTech\\Nouveau dossier", "headers"),
    
    # 1.5 Ko - messages SBD (copie dans SERVEURS)
    ("10-SERVEURS\\12-SERVEUR MOZART02\\mozart02\\projet_geosiara-2011102\\cle_20070507\\documents\\tempsbd\\Nouveau dossier", "messages-SBD"),
]

def main():
    mode = "⚡ RENOMMAGE" if EXECUTE else "🔍 DRY-RUN"
    print(f"{mode}")
    print("=" * 70)
    
    ok = 0
    skip = 0
    fail = 0
    
    for rel_old, new_name in RENAMES:
        old_path = os.path.join(NAS, rel_old)
        parent = os.path.dirname(old_path)
        new_path = os.path.join(parent, new_name)
        
        # Vérifier que l'ancien existe
        if not os.path.exists(old_path):
            print(f"  ⏭️  ABSENT  {rel_old}")
            skip += 1
            continue
        
        # Vérifier que la destination n'existe pas déjà
        if os.path.exists(new_path):
            print(f"  ⚠️  CONFLIT {rel_old} → {new_name} (destination existe déjà)")
            fail += 1
            continue
        
        # Afficher le renommage
        rel_new = os.path.join(os.path.dirname(rel_old), new_name)
        print(f"  ✏️  {rel_old}")
        print(f"    → {rel_new}")
        
        if EXECUTE:
            try:
                os.rename(old_path, new_path)
                ok += 1
            except Exception as e:
                print(f"    ❌ Erreur: {e}")
                fail += 1
        else:
            ok += 1
    
    print(f"\n{'─' * 70}")
    if EXECUTE:
        print(f"  ✅ Renommés : {ok}")
    else:
        print(f"  Renommages prévus : {ok}")
    if skip:
        print(f"  ⏭️  Absents : {skip}")
    if fail:
        print(f"  ❌ Conflits : {fail}")
    
    if not EXECUTE:
        print(f"\n→ Pour exécuter : python rename_nouveau_dossier.py --execute")

if __name__ == "__main__":
    main()
