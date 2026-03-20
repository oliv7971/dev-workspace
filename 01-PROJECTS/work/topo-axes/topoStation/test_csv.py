import pandas as pd
from pathlib import Path
from topo_station_ls import ControlPoint

def read_controls_csv_safe(path):
    df = pd.read_csv(path)
    # Supprimer les lignes avec NaN
    df = df.dropna()
    controls = {}
    for _, row in df.iterrows():
        pid = str(row['pid']).strip()
        if pid and pid != 'nan':
            controls[pid] = ControlPoint(
                pid=pid,
                X=float(row['X']),
                Y=float(row['Y']),
                Z=float(row['Z'])
            )
    return controls

pts = read_controls_csv_safe(Path('controls.csv'))
print('Points chargés:', list(pts.keys()))
print('Nombre:', len(pts))
