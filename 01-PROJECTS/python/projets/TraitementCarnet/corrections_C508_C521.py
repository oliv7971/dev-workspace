import re

# Lire le fichier D
with open('carnet/GHA-auscultation 251201-D.geo', 'r', encoding='latin-1') as f:
    contenu = f.read()

# Nouvelles corrections
corrections = [
    ('C.508', 'C.508.GV3.2'),
    ('C.521', 'C.521GMA.3'),
]

nb_total = 0

for ancien, nouveau in corrections:
    # Pattern pour matcher exactement avec espaces avant/après
    pattern = r'(?<=\s)' + re.escape(ancien) + r'(?=\s)'
    matches = len(re.findall(pattern, contenu))
    
    if matches > 0:
        contenu = re.sub(pattern, nouveau, contenu)
        nb_total += matches
        print(f"✓ {ancien:20s} → {nouveau:20s} ({matches} remplacement(s))")
    else:
        print(f"⚠ {ancien:20s} → Aucune occurrence trouvée")

# Sauvegarder dans version E
with open('carnet/GHA-auscultation 251201-E.geo', 'w', encoding='latin-1') as f:
    f.write(contenu)

print(f"\n{'='*80}")
print(f"✓ Total : {nb_total} remplacements effectués")
print(f"✓ Fichier mis à jour : carnet/GHA-auscultation 251201-E.geo")
print(f"{'='*80}")
