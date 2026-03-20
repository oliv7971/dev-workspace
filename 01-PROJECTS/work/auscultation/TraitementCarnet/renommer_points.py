"""
Script pour renommer tous les anciens noms de points par leurs équivalents A.LB.*
"""

import re

# Lire le fichier
with open('POLYGCR-251121-C.geo', 'r', encoding='utf-8') as f:
    content = f.read()

# Dictionnaire de correspondances (ancien -> nouveau)
# Basé sur l'analyse des angles
correspondances = {
    # Points simples numérotés
    '101': 'A.LB.1665',
    '102': 'A.LB.1625',
    '103': 'A.LB.1605',
    '201': 'A.LB.1676',
    '202': 'A.LB.1646',
    '301': 'A.LB.1667',
    '303': 'A.LB.1667',  # Attention : même que 301
    '304': 'A.LB.1626',
    '305': 'A.LB.1606',
    '401': 'A.LB.1627',
    '402': 'A.LB.1607',
    
    # Points L169.*
    'L169.1': 'A.LB.1691',
    'L169.2': 'A.LB.1693',
    'L169.3': 'A.LB.1694',
    'L169.4': 'A.LB.1695',
    'L169.5': 'A.LB.1696',
    'L169.6': 'A.LB.1697',
    
    # Points L170.*
    'L170.1': 'A.LB.1701',
    'L170.2': 'A.LB.1702',
    'L170.3': 'A.LB.1703',
    'L170.4': 'A.LB.1704',
    
    # Points L158.*
    'L158.1': 'A.LB.1576.2',
    'L158.3': 'A.LB.1574',
    'L158.4': 'A.LB.1573',
    'L158.5': 'A.LB.1572',
    
    # Points L162.*
    'L162.1': 'A.LB.1607',  # Attention : même que 402
    'L162.2': 'A.LB.1605',  # Attention : même que 103
    'L162.3': 'A.LB.1604',
    'L162.4': 'A.LB.1603',
    'L162.5': 'A.LB.1601',
    
    # Point L155
    'L155.D': 'A.LB.C056',
}

# Compter les remplacements
compteurs = {ancien: 0 for ancien in correspondances}
original_content = content

# Faire les remplacements en respectant le format (nom sur 20 caractères)
for ancien, nouveau in sorted(correspondances.items(), key=lambda x: len(x[0]), reverse=True):
    # Pattern pour matcher le nom dans une ligne Mesure
    # Format: 6 chiffres + 2 espaces + "Mesure" + espaces + nom (20 chars) + reste
    pattern = r'(\d{6}\s+Mesure\s+)' + re.escape(ancien) + r'(\s+0\.000000)'
    
    # Calculer les espaces pour avoir exactement 20 caractères
    espaces_necessaires = 20 - len(nouveau)
    replacement = r'\1' + nouveau + ' ' * espaces_necessaires + r'\2'
    
    # Compter les occurrences avant remplacement
    occurrences = len(re.findall(pattern, content))
    compteurs[ancien] = occurrences
    
    # Faire le remplacement
    content = re.sub(pattern, replacement, content)

# Sauvegarder
with open('POLYGCR-251121-C.geo', 'w', encoding='utf-8') as f:
    f.write(content)

# Afficher le résumé
print("="*80)
print("RÉSUMÉ DES REMPLACEMENTS")
print("="*80)

total_remplacements = sum(compteurs.values())
points_remplaces = sum(1 for c in compteurs.values() if c > 0)

for ancien, nouveau in sorted(correspondances.items()):
    count = compteurs[ancien]
    if count > 0:
        print(f"{ancien:15s} -> {nouveau:20s} : {count:3d} remplacements")

print("="*80)
print(f"Total: {total_remplacements} remplacements effectués sur {points_remplaces} points différents")
print("="*80)

# Vérifier qu'on n'a pas cassé le fichier
lignes_avant = original_content.count('\n')
lignes_apres = content.count('\n')
print(f"\nVérification: {lignes_avant} lignes avant, {lignes_apres} lignes après")

if lignes_avant == lignes_apres:
    print("✓ Nombre de lignes inchangé - OK")
else:
    print("⚠ ATTENTION: Le nombre de lignes a changé!")
