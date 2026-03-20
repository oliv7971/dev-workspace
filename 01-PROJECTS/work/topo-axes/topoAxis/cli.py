
import argparse
import pandas as pd
from .parser_excel import build_from_workbook
from .engine import AxisModel

def main():
    ap = argparse.ArgumentParser(description='Compute plan & profile from Excel axis definition.')
    ap.add_argument('xlsx', help='Path to Excel workbook (converted .xlsx)')
    ap.add_argument('--from', dest='s_from', type=float, default=0.0, help='Start PK (m)')
    ap.add_argument('--to', dest='s_to', type=float, default=None, help='End PK (m); default = axis length')
    ap.add_argument('--step', dest='step', type=float, default=5.0, help='Step (m)')
    ap.add_argument('--out', dest='out', default='profile_xyz.csv', help='Output CSV')
    args = ap.parse_args()

    plan, vert, _ = build_from_workbook(args.xlsx)
    model = AxisModel(plan=plan, vertical=vert)

    s0 = args.s_from
    s1 = args.s_to if args.s_to is not None else model.L
    step = args.step
    s_vals = []
    s = s0
    while s <= s1 + 1e-9:
        s_vals.append(s)
        s += step

    rows = []
    for s in s_vals:
        X,Y,Z = model.xyz(s)
        rows.append({'PK': s, 'X': X, 'Y': Y, 'Z': Z})
    df = pd.DataFrame(rows)
    df.to_csv(args.out, index=False)
    print(f'Wrote {args.out} with {len(df)} rows.')

if __name__ == '__main__':
    main()
