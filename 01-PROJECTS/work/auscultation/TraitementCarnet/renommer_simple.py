import re

def renommer_points(fichier_source, fichier_cible, renommages):
    """
    Renomme des points selon un dictionnaire de patterns regex
    """
    
    with open(fichier_source, 'r', encoding='latin-1') as f:
        contenu = f.read()
    
    total_remplacements = 0
    
    for pattern, nouveau_nom in renommages:
        occurrences = len(re.findall(pattern, contenu))
        if occurrences > 0:
            contenu = re.sub(pattern, nouveau_nom, contenu)
            total_remplacements += occurrences
            print(f"{pattern:30s} → {nouveau_nom:20s} : {occurrences:3d} remplacements")
    
    with open(fichier_cible, 'w', encoding='latin-1') as f:
        f.write(contenu)
    
    print(f"\nTotal: {total_remplacements} remplacements effectués")
    print(f"Fichier sauvegardé: {fichier_cible}")

if __name__ == "__main__":
    fichier_source = "POLYGCR-251121-U.geo"
    fichier_cible = "POLYGCR-251121-V.geo"
    
    # Liste des renommages: (pattern_regex, nouveau_nom)
    renommages = [
        (r'\bA141G\.1\d\b', 'A141.GVA.5G'),
        (r'\bP001D\.GCR\b', '01GCR.3D'),
        (r'\bP001G\.GCR\b', '01GCR.3G'),
        (r'\bP052G\.GV3\b', '52GV3.4G'),
        (r'\bP052D\.GV3\b', '52GV3.4D'),
        (r'\bP054G\.GV3\b', '54GV3.9G'),
        (r'\bA142D\b', 'A142GVA.1D'),
        (r'\bA122G\b', 'A122.GVA.1G'),
        (r'\bP071G\b', '71GCR.3G'),
        (r'\bP061G\b', '61GCR.3G'),
        (r'\bV\.1\.\d{2}\b', 'V.1'),
        (r'\bV\.2\.\d{2}\b', 'V.2'),
        (r'\bV\.3\.\d{2}\b', 'V.3'),
        (r'\b1GCR\.3G\b', '01GCR.3G'),
        (r'\b1GCR\.3D\b', '01GCR.3D'),
        (r'\bA\.142D\b', 'A142GVA.1D'),
        (r'\bA\.102G\b', 'A122.GVA.3G'),
        (r'\bA\.141G\b', 'A141.GVA.5G'),
        (r'\bP\.001G\b', '01GCR.3G'),
        (r'\bP\.052G\b', '52GV3.4G'),
        (r'\bP\.054D\b', '54GV3.9D'),
        (r'\b\.001D\b', '01GCR.3D'),
        (r'\bA\.101\b', 'C.101.GVA.2'),
        (r'\bA\.551\b', 'C.551.GV3'),
        (r'\bA\.530\b', 'C.530.GCR.3'),
        (r'\bA\.540\b', 'C.540.GV3.5'),
        (r'\bC\.144\b', 'C.144CGR.2'),
        (r'\bC\.143\b', 'C.143CGR.2'),
        (r'(?<=\s)A142(?=\s)', 'A142GVA.1D'),
        (r'(?<=\s)A122(?=\s)', 'A122.GVA.1G'),
        (r'(?<=\s)A141(?=\s)', 'A141.GVA.5G'),
        (r'(?<=\s)C\.540(?=\s)', 'C.540.GV3.5'),
        (r'(?<=\s)C\.530(?=\s)', 'C.530.GCR.3'),
        (r'(?<=\s)C\.511(?=\s)', 'C.511.GV3'),
        (r'(?<=\s)C\.101(?=\s)', 'C.101.GVA.2'),
        (r'(?<=\s)C\.532(?=\s)', 'C.532.GV3'),
        (r'\bC\.540\.GV3\.5\b', 'C.540GVA.2'),
        (r'\bP059G\.GV3\b', '59GV3.12G'),
        (r'\bP059D\.GV3\b', '59GV3.12D'),
        (r'\bP054D\.GV3\b', '54GV3.9D'),
        (r'\bP054D\.GV4\b', '54GV3.9D'),
    ]
    
    renommer_points(fichier_source, fichier_cible, renommages)
