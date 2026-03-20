import sys
import subprocess
import os

# Variables simulant ce que SMG_gui passerait
root_dir = r"C:\temp\1-tableaux"  # dossier des données
y_m = "2025-07"                   # mois
out_dir = root_dir                # même dossier en sortie

# Chemins vers les scripts
script_dir = os.path.dirname(os.path.abspath(__file__))
evol_path = os.path.join(script_dir, "smc_evolutions.py")
recaps_path = os.path.join(script_dir, "produire_recaps.py")

# 1) Lancer smc_evolutions.py
#cmd1 = [sys.executable, evol_path,
#        "--root", root_dir,
#        "--month", y_m,
#        "--out", out_dir]
#print("CMD1:", " ".join(cmd1))
#proc1 = subprocess.run(cmd1, capture_output=True, text=True, encoding="utf-8", errors="replace")
#print("RETURN CODE1:", proc1.returncode)
#print("STDOUT1:", proc1.stdout)
#print("STDERR1:", proc1.stderr)

# 2) Lancer produire_recaps.py
cmd2 = [sys.executable, recaps_path,
        "--root", out_dir,
        "--month", y_m]
print("CMD2:", " ".join(cmd2))
proc2 = subprocess.run(cmd2, capture_output=True, text=True, encoding="utf-8", errors="replace")
print("RETURN CODE2:", proc2.returncode)
print("STDOUT2:", proc2.stdout)
print("STDERR2:", proc2.stderr)
