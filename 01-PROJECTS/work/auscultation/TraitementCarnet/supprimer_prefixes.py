import re

# Lire le fichier
with open('carnet/auscultations GGS-251128 -B.geo', 'r', encoding='latin-1') as f:
    contenu = f.read()

# Supprimer les préfixes S1. et S2. dans les mesures
# Pattern: Mesure suivi d'espaces puis S1. ou S2.
pattern = r'(Mesure\s+)S[12]\.'
contenu_modifie = re.sub(pattern, r'\1', contenu)

# Compter les remplacements
nb_remplacements = len(re.findall(pattern, contenu))

# Sauvegarder
with open('carnet/auscultations GGS-251128 -B.geo', 'w', encoding='latin-1') as f:
    f.write(contenu_modifie)

print(f"{'='*80}")
print(f"✓ Suppression des préfixes S1. et S2. des mesures")
print(f"✓ {nb_remplacements} remplacements effectués")
print(f"✓ Fichier mis à jour : carnet/auscultations GGS-251128 -B.geo")
print(f"{'='*80}")
