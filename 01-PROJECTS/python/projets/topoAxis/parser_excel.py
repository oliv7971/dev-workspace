
from __future__ import annotations
from typing import Dict, List
import pandas as pd
from .engine import build_plan_from_defs, build_vertical_from_defs

def _guess_headers(df: pd.DataFrame) -> Dict[str,str]:
    mapping = {}
    for col in df.columns:
        c = str(col).strip().lower()
        if any(k in c for k in ['type','élément','element']):
            mapping['type'] = col
        elif c in ('pk','pk debut','pk début','debut','début','pkd'):
            mapping.setdefault('pk_start', col)
        elif any(k in c for k in ['fin','pkf','long','longueur','lcum']):
            mapping.setdefault('pk_end_or_L', col)
        elif 'azimut' in c or 'azi' in c or 'tang' in c:
            mapping['azimut'] = col   # values are in gons (per user)
        elif c == 'r' or 'rayon' in c:
            mapping['R'] = col
        elif 'clotho' in c or 'a clot' in c or c == 'a':
            mapping['A'] = col
        elif 'sens' in c or 'g/d' in c:
            mapping['sens'] = col
    return mapping

def _build_plan_defs(df: pd.DataFrame) -> List[Dict]:
    H = _guess_headers(df)
    out = []
    for _, row in df.iterrows():
        t = str(row.get(H.get('type'), '')).strip()
        if not t:
            continue
        rec = {'type': t}
        if 'azimut' in H:
            try:
                rec['azimut_gon'] = float(str(row.get(H['azimut'])).replace(',','.'))
            except Exception:
                pass
        # Length from PK start/end or L column
        L = None
        if 'pk_end_or_L' in H and 'pk_start' in H:
            try:
                a = float(str(row.get(H['pk_start'])).replace(',','.'))
                b = float(str(row.get(H['pk_end_or_L'])).replace(',','.'))
                L = max(0.0, b - a)
            except Exception:
                pass
        if L is None and 'pk_end_or_L' in H:
            try:
                L = float(str(row.get(H['pk_end_or_L'])).replace(',','.'))
            except Exception:
                pass
        if L is None:
            continue
        rec['L'] = L
        # Parameters
        if 'R' in H:
            try:
                rec['R'] = float(str(row.get(H['R'])).replace(',','.'))
            except Exception:
                pass
        if 'A' in H:
            try:
                rec['A'] = float(str(row.get(H['A'])).replace(',','.'))
            except Exception:
                pass
        if 'sens' in H:
            v = str(row.get(H['sens'])).strip().upper()
            if 'D' in v:
                rec['k_sign'] = +1   # user: droite = +1
            elif 'G' in v:
                rec['k_sign'] = -1   # user: gauche = -1
        out.append(rec)
    return out

def _build_vertical_defs(df: pd.DataFrame) -> List[Dict]:
    out = []
    H = {}
    for c in df.columns:
        cl = str(c).strip().lower()
        if any(k in cl for k in ['type','élément','element']):
            H['type'] = c
        elif cl in ('pk','pk debut','pk début','debut','début','pkd'):
            H.setdefault('pk_start', c)
        elif any(k in cl for k in ['fin','pkf','long','longueur','lcum']):
            H.setdefault('pk_end_or_L', c)
        elif 'pente' in cl or 'rampe' in cl or cl in ('g','g%','g %','pente %','pente%'):
            H['g'] = c
        elif 'g1' in cl or 'pente fin' in cl or 'pente2' in cl:
            H['g1'] = c
        elif 'z0' in cl or 'cote debut' in cl or 'cote début' in cl:
            H['Z0'] = c

    for _, row in df.iterrows():
        t = str(row.get(H.get('type'), '')).strip()
        if not t:
            continue
        rec = {'type': t}
        L = None
        if 'pk_end_or_L' in H and 'pk_start' in H:
            try:
                a = float(str(row.get(H['pk_start'])).replace(',','.'))
                b = float(str(row.get(H['pk_end_or_L'])).replace(',','.'))
                L = max(0.0, b - a)
            except Exception:
                pass
        if L is None and 'pk_end_or_L' in H:
            try:
                L = float(str(row.get(H['pk_end_or_L'])).replace(',','.'))
            except Exception:
                pass
        if L is None:
            continue
        rec['L'] = L
        if 'g' in H and row.get(H['g']) not in (None, ''):
            try:
                rec['g_percent'] = float(str(row.get(H['g'])).replace(',','.'))
            except Exception:
                pass
        if 'g1' in H and row.get(H['g1']) not in (None, ''):
            try:
                rec['g1_percent'] = float(str(row.get(H['g1'])).replace(',','.'))
            except Exception:
                pass
        out.append(rec)
    return out

def build_from_workbook(xlsx_path: str,
                        sheet_plan: str = 'définition axe en plan',
                        sheet_vert: str = 'définition profil en long'):
    xls = pd.ExcelFile(xlsx_path)
    def _read_sheet(name: str) -> pd.DataFrame:
        try:
            df = pd.read_excel(xls, name)
        except Exception:
            dfs = [pd.read_excel(xls, s) for s in xls.sheet_names if name.lower() in s.lower()]
            df = max(dfs, key=lambda d: (d.shape[0]*d.shape[1])) if dfs else pd.DataFrame()
        df = df.dropna(axis=0, how='all').dropna(axis=1, how='all')
        return df

    dfp = _read_sheet(sheet_plan)
    dfv = _read_sheet(sheet_vert)

    plan_defs = _build_plan_defs(dfp)
    vert_defs = _build_vertical_defs(dfv)

    # Use first azimuth in gons if available, else 0
    az0 = 0.0
    if plan_defs and 'azimut_gon' in plan_defs[0]:
        az0 = plan_defs[0]['azimut_gon']

    plan_axis = build_plan_from_defs(plan_defs, azimut_gon=az0)
    vert_axis = build_vertical_from_defs(vert_defs)

    return plan_axis, vert_axis, {'plan_defs': plan_defs, 'vert_defs': vert_defs}
