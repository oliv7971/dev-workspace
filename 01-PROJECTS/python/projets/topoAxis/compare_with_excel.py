
from __future__ import annotations
import pandas as pd
from .parser_excel import build_from_workbook
from .engine import AxisModel

def compare_xyZ_with_workbook(xlsx_path: str,
                              pk_col_like: str = 'PK',
                              calcxy_sheet_like: str = 'Calcul XY',
                              calcz_sheet_like: str = 'Calcul Z',
                              max_rows: int = 5000) -> pd.DataFrame:
    '''Build axis from definition sheets, compute XY/Z at PKs present in Calcul XY/Z,
       and return a DataFrame with deltas versus Excel results (if present).'''
    plan, vert, defs = build_from_workbook(xlsx_path)
    model = AxisModel(plan=plan, vertical=vert)

    xls = pd.ExcelFile(xlsx_path)
    def _find_sheet(like):
        for s in xls.sheet_names:
            if like.lower() in s.lower():
                return s
        return None

    sxy = _find_sheet(calcxy_sheet_like)
    sz = _find_sheet(calcz_sheet_like)

    dfxy = pd.read_excel(xls, sxy) if sxy else pd.DataFrame()
    dfz  = pd.read_excel(xls, sz) if sz else pd.DataFrame()

    def _find_col(df, patterns):
        for c in df.columns:
            cl = str(c).lower()
            if any(p in cl for p in patterns):
                return c
        return None

    out_rows = []
    if not dfxy.empty:
        c_pk = _find_col(dfxy, ['pk'])
        c_x  = _find_col(dfxy, ['x'])
        c_y  = _find_col(dfxy, ['y'])
        for _, row in dfxy.head(max_rows).iterrows():
            if c_pk is None: break
            pk = row[c_pk]
            if pd.isna(pk): 
                continue
            try:
                s = float(str(pk).replace(',','.'))
            except Exception:
                continue
            X,Y,_ = model.xyz(s)
            Xex, Yex = (row.get(c_x), row.get(c_y))
            out_rows.append({
                'PK': s, 'X_model': X, 'Y_model': Y,
                'X_excel': Xex, 'Y_excel': Yex,
                'dX': None if Xex is None else X - Xex,
                'dY': None if Yex is None else Y - Yex,
            })
    if not dfz.empty:
        c_pk = _find_col(dfz, ['pk'])
        c_z  = _find_col(dfz, ['z','cote','alt'])
        for _, row in dfz.head(max_rows).iterrows():
            if c_pk is None: break
            pk = row[c_pk]
            if pd.isna(pk): 
                continue
            try:
                s = float(str(pk).replace(',','.'))
            except Exception:
                continue
            _,_,Z = model.xyz(s)
            Zex = row.get(c_z)
            out_rows.append({
                'PK': s, 'Z_model': Z,
                'Z_excel': Zex,
                'dZ': None if Zex is None else Z - Zex,
            })
    return pd.DataFrame(out_rows)
