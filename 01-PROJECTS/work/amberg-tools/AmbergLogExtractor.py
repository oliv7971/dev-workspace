import re
import pandas as pd

# Lire le fichier log
log_file = "setout.log"  # fichier amberg

# Regex pour extraire les infos
date_pattern = r"(\d{1,2}-\s*\d{1,2}-\d{4} \d{1,2}:\d{1,2}:\d{1,2})"
hs_pattern = r"HS:\s*([\d\.\-]+)"
l_pattern = r"L:\s*([\d\.\-]+)"
h_pattern = r"H:\s*([\d\.\-]+)"
coord_pattern = r"Est:\s*([\d\.\-]+);\s*Nord:\s*([\d\.\-]+);\s*Height:\s*([\d\.\-]+)"

# Stockage des données
data = []

with open(log_file, "r", encoding="utf-8") as file:
    lines = file.readlines()
    for i in range(len(lines)):
        date_match = re.search(date_pattern, lines[i])
        hs_match = re.search(hs_pattern, lines[i+1]) if i+1 < len(lines) else None
        l_match = re.search(l_pattern, lines[i+1]) if i+1 < len(lines) else None
        h_match = re.search(h_pattern, lines[i+1]) if i+1 < len(lines) else None
        coord_match = re.search(coord_pattern, lines[i+2]) if i+2 < len(lines) else None

        if date_match and hs_match and l_match and h_match and coord_match:
            date = date_match.group(1)
            hs = hs_match.group(1)
            l = l_match.group(1)
            h = h_match.group(1)
            est = coord_match.group(1)
            nord = coord_match.group(2)
            height = coord_match.group(3)

            data.append([date, hs, l, h, est, nord, height])

# Création du tableau avec Pandas
df = pd.DataFrame(data, columns=["Date", "HS", "L", "H", "Est", "Nord", "Height"])

# Affichage du tableau
print(df)

# Export en CSV si besoin
df.to_csv("extraction_log.csv", index=False)
