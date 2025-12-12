import re

# Lire le fichier C
with open('carnet/GHA-auscultation 251201-C.geo', 'r', encoding='latin-1') as f:
    contenu = f.read()

# Corrections des codes sans point P0xxG/D
corrections_sans_point = [
    ('P001G', '01GMA.11G'),
    ('P001D', '01GMA.13D'),
    ('P009G', '009.i.GHA.4G'),
    ('P009D', '009.i.GHA.4D'),
    ('P036G', '036.i.GHA.1G'),
    ('P036D', '036.i.GHA.1D'),
    ('P093G', '93GV3.12G'),
]

nb_total = 0

for ancien, nouveau in corrections_sans_point:
    # Pattern pour matcher exactement avec espaces avant/après
    pattern = r'(?<=\s)' + re.escape(ancien) + r'(?=\s)'
    matches = len(re.findall(pattern, contenu))
    
    if matches > 0:
        contenu = re.sub(pattern, nouveau, contenu)
        nb_total += matches
        print(f"✓ {ancien:20s} → {nouveau:20s} ({matches} remplacement(s))")
    else:
        print(f"  {ancien:20s} → Déjà corrigé")

# Sauvegarder dans version D
with open('carnet/GHA-auscultation 251201-D.geo', 'w', encoding='latin-1') as f:
    f.write(contenu)

print(f"\n{'='*80}")
print(f"✓ Total : {nb_total} remplacements effectués")
print(f"✓ Fichier mis à jour : carnet/GHA-auscultation 251201-D.geo")
print(f"{'='*80}")
