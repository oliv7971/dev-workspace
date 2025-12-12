import re

# Lire le fichier B
with open('carnet/GHA-auscultation 251201-B.geo', 'r', encoding='latin-1') as f:
    contenu = f.read()

# Corrections supplémentaires
corrections = [
    ('036.i.GHA.1G', '036.i.GHA.1G'),  # Déjà correct
    ('93GV3.12G', '93GV3.12G'),        # Déjà correct
    ('C.021', 'C.521GMA.3'),
    ('C.707', 'C.707.GV3.4'),
    ('C.541', 'C.541.GV3.6'),
    ('C.341', 'C.541.GV3.6'),
]

nb_total = 0

for ancien, nouveau in corrections:
    if ancien == nouveau:
        continue
    
    # Pattern pour matcher exactement avec espaces avant/après
    pattern = r'(?<=\s)' + re.escape(ancien) + r'(?=\s)'
    matches = len(re.findall(pattern, contenu))
    
    if matches > 0:
        contenu = re.sub(pattern, nouveau, contenu)
        nb_total += matches
        print(f"✓ {ancien:20s} → {nouveau:20s} ({matches} remplacement(s))")
    else:
        print(f"⚠ {ancien:20s} → Aucune occurrence trouvée")

# Sauvegarder dans version C
with open('carnet/GHA-auscultation 251201-C.geo', 'w', encoding='latin-1') as f:
    f.write(contenu)

print(f"\n{'='*80}")
print(f"✓ Total : {nb_total} remplacements effectués")
print(f"✓ Fichier mis à jour : carnet/GHA-auscultation 251201-C.geo")
print(f"{'='*80}")
