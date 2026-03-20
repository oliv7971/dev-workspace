"""
Script pour renommer les points L058.G, L059.G, L069.G, L070.G par leurs équivalents G.LB.*
"""

import re

# Lire le fichier
with open('POLYGCR-251121-D.geo', 'r', encoding='utf-8') as f:
    content = f.read()

# Dictionnaire de correspondances
correspondances = {
    'L070.G': 'G.LB.070',
    'L069.G': 'G.LB.069',
    'L059.G': 'G.LB.057',
    'L058.G': 'G.LB.058',
}

# Compter les remplacements
compteurs = {ancien: 0 for ancien in correspondances}

# Faire les remplacements
for ancien, nouveau in sorted(correspondances.items(), key=lambda x: len(x[0]), reverse=True):
    # Pattern pour matcher le nom dans une ligne Mesure
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
with open('POLYGCR-251121-D.geo', 'w', encoding='utf-8') as f:
    f.write(content)

# Afficher le résumé
print("="*80)
print("RÉSUMÉ DES REMPLACEMENTS")
print("="*80)

total_remplacements = sum(compteurs.values())

for ancien, nouveau in sorted(correspondances.items()):
    count = compteurs[ancien]
    if count > 0:
        print(f"{ancien:15s} -> {nouveau:20s} : {count:3d} remplacements")

print("="*80)
print(f"Total: {total_remplacements} remplacements effectués")
print("="*80)
