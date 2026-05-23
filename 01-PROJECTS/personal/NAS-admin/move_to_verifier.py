"""Déplace les dossiers douteux de _doublons vers _a_verifier."""
import os, shutil

NAS = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\34-controle voussoirs SMP4"
DOUBLONS  = os.path.join(NAS, "_doublons")
A_VERIFIER = os.path.join(NAS, "_a_verifier")

a_deplacer = [
    "03-traitement  smp4 mars 2017 - 170318",
    "06-smp.bak",
    "CONTROLES SMP A CLASSER",
    "MOULES SMP4",
    "SMP - CONTROLES MOULES ET VOUSSOIRS",
    "smp-janv2018",
    "tracker",
]

os.makedirs(A_VERIFIER, exist_ok=True)

for folder in a_deplacer:
    src = os.path.join(DOUBLONS, folder)
    dst = os.path.join(A_VERIFIER, folder)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"  ✅  {folder}")
    else:
        print(f"  ??  {folder} — introuvable dans _doublons")

# Ce qui reste dans _doublons (confirmés)
restants = [d for d in os.listdir(DOUBLONS) if os.path.isdir(os.path.join(DOUBLONS, d))]
print(f"\nRestant dans _doublons (confirmés) : {restants}")
print("Terminé.")
