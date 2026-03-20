import re

# Liste des renommages à effectuer
renommages = [
    # Correspondances automatiques trouvées
    ('S1.P014D', 'S1.14.GGS.8D'),
    ('S1.P019G', 'S1.19.GGS.10G'),
    ('S1.P026D', 'S1.26.GGS.8D'),
    ('S1.P043D', 'S1.43.GGS.6D'),
    ('S1.P043G', 'S1.43.GGS.5G'),
    ('S1.P051D', 'S1.51.GGS.4D'),
    ('S1.P051G', 'S1.51.GGS.4G'),
    
    # Correspondances manuelles
    ('S1.P003D', 'S1.03.GGS.10D'),
    ('S1.P003G', 'S1.03.GGS.10G'),
    ('S1.P011G', 'S1.011.GVA.2G'),
    ('S1.P012G', 'S1.011.GVA.2G'),  # Même point
    ('S1.P013G', 'S1.011.GVA.2G'),  # Même point
    
    ('S2.P003D', 'S2.03.GGS.10D'),
    ('S2.P003G', 'S2.03.GGS.10G'),
    ('S2.P011G', 'S2.011.GVA.2G'),
    ('S2.P012G', 'S2.011.GVA.2G'),  # Même point
    ('S2.P019G', 'S2.19.GGS.10G'),
    ('S2.P026D', 'S2.26.GGS.8D'),
]

# Lire le fichier
with open('carnet/auscultations GGS-251128 -B.geo', 'r', encoding='latin-1') as f:
    contenu = f.read()

# Appliquer les renommages
nb_remplacements = 0
for ancien, nouveau in renommages:
    # Utiliser regex pour matcher exactement (avec limites de mots)
    pattern = r'(?<=\s)' + re.escape(ancien) + r'(?=\s)'
    matches = len(re.findall(pattern, contenu))
    if matches > 0:
        contenu = re.sub(pattern, nouveau, contenu)
        nb_remplacements += matches
        print(f"✓ {ancien:20s} → {nouveau:20s} ({matches} remplacement(s))")
    else:
        print(f"⚠ {ancien:20s} → Aucune occurrence trouvée")

# Sauvegarder
with open('carnet/auscultations GGS-251128 -B.geo', 'w', encoding='latin-1') as f:
    f.write(contenu)

print(f"\n{'='*80}")
print(f"✓ Total : {nb_remplacements} remplacements effectués")
print(f"✓ Fichier mis à jour : carnet/auscultations GGS-251128 -B.geo")
print(f"{'='*80}")
