"""
Batch-export Excel workbooks to multi-page PDFs (preset SMC) with config file or in-file variables.

Designed for Windows + Excel Desktop (COM). Tested with Excel 2021/365.

What this script does (for each workbook):
- Sheet Convergences → PDF (multi-page height allowed):
  - Repeat rows 1–9 on every page
  - Fit all columns on one page width (FitToPagesWide=1)
  - Detect last column from row 9 headers OR widest merged cell on row 5 (takes the max)
  - Print area from A1 to (last_col, last_data_row_in_col_A), clamped to UsedRange
- Sheet Déplacements → same rules as Convergences, but last column can stop at merged A5 or label "point bas droit" in header row.
- Sheet Graphiques → export each grey-bounded zone (cells inside grey frames) to a single A4 page, with filters to avoid blanks/tiny fragments.
- Merge all parts into a single PDF named like the workbook.

Configuration
-------------
You can configure via config.json placed next to the script, OR by editing the CONFIG dict below. If both exist, config.json wins.

Example config.json:
{
  "root": "C:/Temp/1-tableaux/GGS",
  "out":  "C:/Temp/exports_pdf",
  "locale": "fr",
  "patterns": {
    "convergences": ["^convergences$"],
    "deplacements": ["^d[ée]placements$"],
    "graphiques": ["^graphiques?$"]
  },
  "titles_repeat_rows": "1:9",
  "header_row": 9,
  "merged_hint_row": 5,
  "fit_to_one_page_width": true,
  "include_chart_sheets": false,
  "grey_ref_cell": "A1",        # cell whose color is the grey of the frames
    "scan_row": 15,                 # row index used to scan columns for grey separators (scanline mode)
    "scan_col": 5,                  # col index used to scan rows for grey separators (scanline mode)
    "grid_mode": "axes",           # "axes" = use row/col axes below; anything else = scanline
    "grid_axis_row": 2,             # detect vertical separators by reading this row (e.g., row 2)
    "grid_axis_col": 2,             # detect horizontal separators by reading this column (e.g., column B=2)
    "max_rows": 256,
    "max_cols": 128,
    # Déplacements stopping logic
    "deplacements_stop_label": "point bas droit",
    "include_chart_sheets": False,  # avoid chartsheets (can differ in paper size)
    # File scan
    "recursive": False,                 # False = only root folder; True = include subfolders
    "include_globs": ["*.xlsx", "*.xlsm"],
    "exclude_globs": ["~$*"],          # exclude Excel temp files
    "allowed_subdirs": [],              # e.g., ["2025/GHA", "2025/GVA"] relative to root
    "forbidden_subdirs": [],            # e.g., ["archive", "_old"]
    "dry_run": False,                   # True = list files only
    "max_files": 0,                     # 0 = unlimited
    # Filters for Graphiques
    "min_zone_rows": 5,
    "min_zone_cols": 5,
    "min_zone_nonempty": 10,
    # Config loading guard
    "allow_cwd_config": False           # load config.json from CWD? default: no
}
"""

from __future__ import annotations
import json, re, sys, tempfile, time, os, uuid, fnmatch
from pathlib import Path
from typing import List, Optional

from unidecode import unidecode
from PyPDF2 import PdfMerger

try:
    import pythoncom, pywintypes
    import win32com.client as win32
except Exception as e:
    print("This script requires Windows + Excel (pywin32).", file=sys.stderr)
    raise

# Excel numeric constants (avoid makepy)
XL_TYPE_PDF = 0       # xlTypePDF
XL_TOLEFT = -4159     # xlToLeft
XL_UP = -4162         # xlUp
XL_LANDSCAPE = 2      # xlLandscape
XL_PORTRAIT = 1       # xlPortrait
XL_PAPERSIZE_A4 = 9   # xlPaperA4

# ---------------- Default in-file CONFIG (used if no config.json) ----------------
CONFIG = {
    "root": "",
    "out": "",
    "locale": "fr",
    "patterns": {
        "convergences": [r"^convergences$"],
        "deplacements": [r"^d[ée]placements$"],
        "graphiques": [r"^graphiques?$"],
    },
    "titles_repeat_rows": "1:9",
    "header_row": 9,
    "merged_hint_row": 5,
    "fit_to_one_page_width": True,
    "include_chart_sheets": False,
    "grey_ref_cell": "A1",
    "scan_row": 15,
    "scan_col": 5,
    "grid_mode": "axes",
    "grid_axis_row": 2,
    "grid_axis_col": 2,
    "max_rows": 256,
    "max_cols": 128,
    "deplacements_stop_label": "point bas droit",
    "orientation": "landscape",
    "margins_pts": 18,
    "ask_if_missing": True,
    "force_active_printer": "",

    # File scan
    "recursive": False,
    "include_globs": ["*.xlsx", "*.xlsm"],
    "exclude_globs": ["~$*"],
    "allowed_subdirs": [],
    "forbidden_subdirs": [],
    "dry_run": False,
    "max_files": 0,

    # Filters for Graphiques
    "min_zone_rows": 5,
    "min_zone_cols": 5,
    "min_zone_nonempty": 10,
    "strict_grey_borders": True,
    "require_full_grey_borders": True,
    "grey_color_tolerance": 0,
    "grey_border_ratio": 0.8,

    # Config loading guard
    "allow_cwd_config": False,
}


def pick_folder(title: str) -> Optional[Path]:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk(); root.withdraw()
        chosen = filedialog.askdirectory(title=title)
        root.destroy()
        return Path(chosen) if chosen else None
    except Exception:
        return None


# ---------------- Excel lifecycle ----------------

def start_excel():
    """Start Excel with late binding only (no makepy)."""
    try:
        pythoncom.CoInitialize()
    except Exception:
        pass
    attempts = 0
    while attempts < 5:
        try:
            excel = win32.DispatchEx("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False
            return excel
        except pywintypes.com_error as e:
            # RPC_E_CALL_REJECTED (Excel busy) → retry
            if getattr(e, 'hresult', None) == -2147418111:
                time.sleep(0.7 + 0.5 * attempts)
                attempts += 1
                continue
            raise
    raise RuntimeError("Could not start Excel after retries")


def close_excel(excel) -> None:
    try:
        excel.Quit()
    except Exception:
        pass


# ---------------- Utilities ----------------

def normalize_name(name: str) -> str:
    s = unidecode(str(name)).lower()
    s = re.sub(r"[ _]+", " ", s).strip()
    return s


def compile_patterns(lst: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in lst]


def expand_path(p: str | None, *, script_dir: Path) -> Optional[Path]:
    """Expand macros/env/relative paths.
    Macros: ${SCRIPT_DIR}, ${CWD}. Also supports ~ and %VARS%.
    Relative paths resolve against script_dir.
    """
    if not p:
        return None
    base = str(p)
    base = base.replace("${SCRIPT_DIR}", str(script_dir))
    base = base.replace("${CWD}", str(Path.cwd()))
    base = os.path.expandvars(os.path.expanduser(base))
    path = Path(base)
    if not path.is_absolute():
        path = script_dir / path
    return path

# ---------------- Detection helpers ----------------

def find_sheet_by_patterns(wb, patterns: List[re.Pattern]):
    for sh in wb.Worksheets:
        if any(p.search(normalize_name(sh.Name)) for p in patterns):
            return sh
    return None


def chartsheets_by_patterns(wb, patterns: List[re.Pattern]):
    out = []
    try:
        for ch in getattr(wb, "Charts", []):
            if any(p.search(normalize_name(ch.Name)) for p in patterns):
                out.append(ch)
    except Exception:
        pass
    return out


def last_col_from_header_row(ws, header_row: int) -> int:
    try:
        last_col = ws.Cells(header_row, ws.Columns.Count).End(XL_TOLEFT).Column
        return max(1, int(last_col))
    except Exception:
        return 1


def last_col_from_merged_row(ws, merged_row: int) -> int:
    """Return rightmost column covered by the widest merged area on the given row."""
    try:
        used_last_col = ws.Cells(merged_row, ws.Columns.Count).End(XL_TOLEFT).Column
        best_right = 1
        col = 1
        while col <= used_last_col:
            rng = ws.Cells(merged_row, col)
            ma = rng.MergeArea
            right = ma.Column + ma.Columns.Count - 1 if ma else col
            col = right + 1
            if right > best_right:
                best_right = right
        return max(1, int(best_right))
    except Exception:
        return 1


def last_data_row_in_col_a(ws) -> int:
    try:
        a_last = ws.Cells(ws.Rows.Count, 1).End(XL_UP).Row
        used = ws.UsedRange
        used_last = used.Row + used.Rows.Count - 1
        return max(1, min(int(a_last), int(used_last)))
    except Exception:
        return 1


# ---------------- Export helpers ----------------

def _apply_common_layout(ps, *, fit_w: bool, fit_tall: bool, orientation: str = "landscape", margins_pts: int = 18) -> None:
    try:
        ps.Zoom = False
    except Exception:
        pass
    try:
        ps.FitToPagesWide = 1 if fit_w else False
        ps.FitToPagesTall = 1 if fit_tall else False
    except Exception:
        pass
    try:
        ps.Orientation = XL_LANDSCAPE if str(orientation).lower().startswith("land") else XL_PORTRAIT
    except Exception:
        pass
    try:
        ps.LeftMargin = ps.RightMargin = margins_pts
        ps.TopMargin = ps.BottomMargin = margins_pts
    except Exception:
        pass
    try:
        ps.PaperSize = XL_PAPERSIZE_A4
    except Exception:
        pass
    try:
        ps.CenterHorizontally = True
        ps.CenterVertically = True
    except Exception:
        pass


def configure_pagesetup_for_table(ws, titles_repeat_rows: str, fit_one_page_width: bool, *, orientation: str = "landscape", margins_pts: int = 18) -> None:
    app = getattr(ws, "Application", None) or getattr(ws.Parent, "Application", None)
    if app is not None:
        try: app.PrintCommunication = False
        except Exception: pass
    ps = ws.PageSetup
    try:
        start, end = titles_repeat_rows.split(":")
        ps.PrintTitleRows = f"{chr(36)}{start}:{chr(36)}{end}"  # "$1:$9"
    except Exception:
        try: ps.PrintTitleRows = f"{chr(36)}1:{chr(36)}9"
        except Exception: pass
    _apply_common_layout(ps, fit_w=bool(fit_one_page_width), fit_tall=False, orientation=orientation, margins_pts=margins_pts)
    if app is not None:
        try: app.PrintCommunication = True
        except Exception: pass


def set_print_area(ws, last_row: int, last_col: int) -> None:
    try:
        addr = ws.Range(ws.Cells(1, 1), ws.Cells(last_row, last_col)).Address
        ws.PageSetup.PrintArea = addr
    except Exception:
        pass


def export_worksheet_to_pdf(ws, out_pdf: Path) -> bool:
    try:
        ws.ExportAsFixedFormat(XL_TYPE_PDF, str(out_pdf))
        return True
    except Exception as e:
        print(f"  [!] Export worksheet '{ws.Name}' failed: {e}")
        return False


def export_chartsheet_to_pdf(ch, out_pdf: Path, *, orientation: str = "landscape", margins_pts: int = 18) -> bool:
    try:
        app = getattr(ch, "Application", None) or getattr(ch.Parent, "Application", None)
        if app is not None:
            try: app.PrintCommunication = False
            except Exception: pass
        try:
            ps = ch.PageSetup
            _apply_common_layout(ps, fit_w=True, fit_tall=True, orientation=orientation, margins_pts=margins_pts)
        except Exception:
            pass
        ch.ExportAsFixedFormat(XL_TYPE_PDF, str(out_pdf))
        if app is not None:
            try: app.PrintCommunication = True
            except Exception: pass
        return True
    except Exception as e:
        print(f"  [!] Export chart sheet '{ch.Name}' failed: {e}")
        return False


def _snapshot_pagesetup(ws):
    snap = {}
    try:
        ps = ws.PageSetup
        for k in ("PrintArea","PrintTitleRows","Zoom","FitToPagesWide","FitToPagesTall","LeftMargin","RightMargin","TopMargin","BottomMargin","Orientation"):
            try: snap[k] = getattr(ps, k)
            except Exception: pass
    except Exception:
        pass
    return snap


def _restore_pagesetup(ws, snap):
    try:
        ps = ws.PageSetup
        for k, v in snap.items():
            try: setattr(ps, k, v)
            except Exception: pass
    except Exception:
        pass


def export_chartobject_area_to_pdf(ws, chartobj, out_pdf: Path, *, orientation: str = "landscape", margins_pts: int = 18) -> bool:
    """Export exactly the area covering an embedded ChartObject by temporarily
    setting the worksheet's print area to the chart's bounding cells.
    """
    try:
        snap = _snapshot_pagesetup(ws)
        app = getattr(ws, "Application", None) or getattr(ws.Parent, "Application", None)
        if app is not None:
            try: app.PrintCommunication = False
            except Exception: pass
        tl = chartobj.TopLeftCell
        br = chartobj.BottomRightCell
        rng = ws.Range(tl, br)
        ps = ws.PageSetup
        _apply_common_layout(ps, fit_w=True, fit_tall=True, orientation=orientation, margins_pts=margins_pts)
        ps.PrintTitleRows = ""
        ws.PageSetup.PrintArea = rng.Address
        ok = export_worksheet_to_pdf(ws, out_pdf)
        if app is not None:
            try: app.PrintCommunication = True
            except Exception: pass
        _restore_pagesetup(ws, snap)
        return ok
    except Exception as e:
        print(f"  [!] Export chart area failed: {e}")
        return False


def make_temp_path(suffix: str) -> Path:
    td = Path(tempfile.gettempdir())
    return td / f"smc_{uuid.uuid4().hex}{suffix}"


def merge_pdfs(parts: List[Path], final_pdf: Path) -> None:
    merger = PdfMerger()
    try:
        for p in parts:
            if p and p.exists() and p.stat().st_size > 0:
                merger.append(str(p))
        final_pdf.parent.mkdir(parents=True, exist_ok=True)
        merger.write(str(final_pdf))
    finally:
        try: merger.close()
        except Exception: pass


# ---------------- Grey-frame detection (Graphiques) ----------------

def _cell_color(ws, r: int, c: int) -> Optional[int]:
    try:
        return int(ws.Cells(r, c).Interior.Color)
    except Exception:
        return None

def _color_components(v: Optional[int]) -> tuple[int,int,int]:
    if v is None:
        return (0,0,0)
    try:
        r = v & 0xFF
        g = (v >> 8) & 0xFF
        b = (v >> 16) & 0xFF
        return (r,g,b)
    except Exception:
        return (0,0,0)

def _color_matches(c1: Optional[int], c2: Optional[int], tol: int = 0) -> bool:
    if c1 is None or c2 is None:
        return False
    if tol <= 0:
        return int(c1) == int(c2)
    r1,g1,b1 = _color_components(int(c1))
    r2,g2,b2 = _color_components(int(c2))
    return abs(r1-r2) <= tol and abs(g1-g2) <= tol and abs(b1-b2) <= tol

# --- Axes-based grid detection (exact match to A1 color on fixed axes) ---

def detect_axes_separators(ws, *, ref_color: Optional[int], row_axis: int, col_axis: int,
                           u_r1: int, u_c1: int, u_r2: int, u_c2: int, tol: int = 0) -> tuple[list[int], list[int]]:
    """Find grey separator lines by sampling exactly one row and one column
    (e.g., row 2 and column B) against `ref_color` (usually A1's color).
    Returns ONLY true separators (cells exactly matching A1, within `tol`).
    No artificial outer bounds are added.
    """
    row_seps: list[int] = []
    col_seps: list[int] = []

    # Horizontal separators → look down the chosen column
    col_axis = max(1, int(col_axis))
    for r in range(u_r1, u_r2 + 1):
        if _color_matches(_cell_color(ws, r, col_axis), ref_color, tol):
            row_seps.append(r)

    # Vertical separators → look across the chosen row
    row_axis = max(1, int(row_axis))
    for c in range(u_c1, u_c2 + 1):
        if _color_matches(_cell_color(ws, row_axis, c), ref_color, tol):
            col_seps.append(c)

    row_seps = sorted(set(row_seps))
    col_seps = sorted(set(col_seps))
    return row_seps, col_seps


def build_zones_from_separators(ws, row_seps: list[int], col_seps: list[int]) -> list[str]:
    zones: list[str] = []
    for j in range(1, len(row_seps)):
        r1 = row_seps[j-1]; r2 = row_seps[j]
        for i in range(1, len(col_seps)):
            c1 = col_seps[i-1]; c2 = col_seps[i]
            # interior rectangle (exclude the grey borders themselves)
            top_left = ws.Cells(r1 + 1, c1 + 1)
            bottom_right = ws.Cells(r2 - 1, c2 - 1)
            zones.append(ws.Range(top_left, bottom_right).Address)
    return zones


def detect_grey_separators(ws, *, grey_ref_cell: str, scan_row: int, scan_col: int, max_rows: int, max_cols: int, tol: int = 0) -> tuple[list[int], list[int]]:
    """Return (row_separators, col_separators) indices matching the reference color on scan lines.
    Color equality is evaluated against the color of grey_ref_cell (default A1),
    with an optional RGB tolerance `tol` (0 = exact).
    """
    try:
        ref_color = int(ws.Range(grey_ref_cell).Interior.Color)
    except Exception:
        try:
            ref_color = int(ws.Cells(1, 1).Interior.Color)
        except Exception:
            ref_color = None

    row_seps: list[int] = []
    col_seps: list[int] = []

    for r in range(1, max_rows + 1):
        clr = _cell_color(ws, r, scan_col)
        if _color_matches(clr, ref_color, tol):
            row_seps.append(r)
    for c in range(1, max_cols + 1):
        clr = _cell_color(ws, scan_row, c)
        if _color_matches(clr, ref_color, tol):
            col_seps.append(c)

    if 1 not in row_seps: row_seps = [1] + row_seps
    if max_rows not in row_seps: row_seps = row_seps + [max_rows]
    if 1 not in col_seps: col_seps = [1] + col_seps
    if max_cols not in col_seps: col_seps = col_seps + [max_cols]

    row_seps = sorted(set(row_seps))
    col_seps = sorted(set(col_seps))
    return row_seps, col_seps


def build_grey_zones(ws, *, grey_ref_cell: str, scan_row: int, scan_col: int, max_rows: int, max_cols: int, tol: int = 0) -> list[str]:
    rows, cols = detect_grey_separators(ws, grey_ref_cell=grey_ref_cell, scan_row=scan_row, scan_col=scan_col, max_rows=max_rows, max_cols=max_cols, tol=tol)
    zones: list[str] = []
    for j in range(1, len(rows)):
        r1 = rows[j-1]; r2 = rows[j]
        for i in range(1, len(cols)):
            c1 = cols[i-1]; c2 = cols[i]
            top_left = ws.Cells(r1 + 1, c1 + 1)
            bottom_right = ws.Cells(r2 - 1, c2 - 1)
            zones.append(ws.Range(top_left, bottom_right).Address)
    return zones


def _addr_to_bounds(ws, addr: str) -> tuple[int,int,int,int]:
    rng = ws.Range(addr)
    tl = rng.Cells(1,1)
    br = rng.Cells(rng.Rows.Count, rng.Columns.Count)
    return tl.Row, tl.Column, br.Row, br.Column


def _zone_has_chart(ws, r1, c1, r2, c2) -> bool:
    try:
        cos = ws.ChartObjects()
        for i in range(1, cos.Count + 1):
            ch = cos.Item(i)
            tl = ch.TopLeftCell; br = ch.BottomRightCell
            if (tl.Row >= r1 and tl.Column >= c1 and br.Row <= r2 and br.Column <= c2):
                return True
    except Exception:
        pass
    return False


def _zone_nonempty_count(ws, addr: str) -> int:
    try:
        return int(ws.Parent.Application.WorksheetFunction.CountA(ws.Range(addr)))
    except Exception:
        return 0

def _is_grey_row_span(ws, r: int, c1: int, c2: int, ref_color: int | None, tol: int = 0, required_ratio: float = 1.0) -> bool:
    if ref_color is None:
        return False
    c1 = max(1, c1); c2 = max(c1, c2)
    width = max(1, c2 - c1 + 1)
    step = max(1, width // 25)
    hits = 0; total = 0
    for c in range(c1, c2 + 1, step):
        clr = _cell_color(ws, r, c)
        if _color_matches(clr, ref_color, tol):
            hits += 1
        total += 1
    return total > 0 and (hits / total) >= required_ratio

def _is_grey_col_span(ws, c: int, r1: int, r2: int, ref_color: int | None, tol: int = 0, required_ratio: float = 1.0) -> bool:
    if ref_color is None:
        return False
    r1 = max(1, r1); r2 = max(r1, r2)
    height = max(1, r2 - r1 + 1)
    step = max(1, height // 25)
    hits = 0; total = 0
    for r in range(r1, r2 + 1, step):
        clr = _cell_color(ws, r, c)
        if _color_matches(clr, ref_color, tol):
            hits += 1
        total += 1
    return total > 0 and (hits / total) >= required_ratio


def export_grey_zones_to_pdfs(ws, cfg: dict) -> List[Path]:
    """Export each detected grey-bounded zone as its own single-page A4 PDF.
    Filters out empty/tiny areas and, if strict_grey_borders is True, keeps
    only rectangles whose four outer edges are (mostly) the reference grey.
    """
    out_paths: List[Path] = []
    snap = _snapshot_pagesetup(ws)
    try:
        used = ws.UsedRange
        u_r1, u_c1 = used.Row, used.Column
        u_r2 = u_r1 + used.Rows.Count - 1
        u_c2 = u_c1 + used.Columns.Count - 1

        scan_row = max(u_r1, min(u_r2, int(cfg.get("scan_row", 15))))
        scan_col = max(u_c1, min(u_c2, int(cfg.get("scan_col", 5))))

        # reference grey
        try:
            ref_color = int(ws.Range(cfg.get("grey_ref_cell", "A1")).Interior.Color)
        except Exception:
            try:
                ref_color = int(ws.Cells(1, 1).Interior.Color)
            except Exception:
                ref_color = None

        # Build zones via configured mode
        if str(cfg.get("grid_mode", "axes")).lower() == "axes":
            row_seps, col_seps = detect_axes_separators(
                ws,
                ref_color=ref_color,
                row_axis=int(cfg.get("grid_axis_row", 2)),
                col_axis=int(cfg.get("grid_axis_col", 2)),
                u_r1=u_r1, u_c1=u_c1, u_r2=u_r2, u_c2=u_c2,
                tol=int(cfg.get("grey_color_tolerance", 0))
            )
            # Need at least 2 separators on each axis to form rectangles
            zones = build_zones_from_separators(ws, row_seps, col_seps) if (len(row_seps) >= 2 and len(col_seps) >= 2) else []
        else:
            zones = build_grey_zones(
                ws,
                grey_ref_cell=cfg.get("grey_ref_cell", "A1"),
                scan_row=scan_row,
                scan_col=scan_col,
                max_rows=u_r2,
                max_cols=u_c2,
                tol=int(cfg.get("grey_color_tolerance", 0)),
            )
        if not zones:
            return []

        min_r = int(cfg.get("min_zone_rows", 5))
        min_c = int(cfg.get("min_zone_cols", 5))
        min_nonempty = int(cfg.get("min_zone_nonempty", 10))
        strict = bool(cfg.get("strict_grey_borders", True))
        required_ratio = 1.0 if bool(cfg.get("require_full_grey_borders", True)) else float(cfg.get("grey_border_ratio", 0.8))
        tol = int(cfg.get("grey_color_tolerance", 0))

        kept: list[str] = []
        seen = set()
        for addr in zones:
            r1, c1, r2, c2 = _addr_to_bounds(ws, addr)
            # size
            if (r2 - r1 + 1) < min_r or (c2 - c1 + 1) < min_c:
                continue
            # inside UsedRange
            if r2 < u_r1 or r1 > u_r2 or c2 < u_c1 or c1 > u_c2:
                continue
            key = (r1, c1, r2, c2)
            if key in seen:
                continue

            # optional strict border check (top/bottom/left/right mostly grey)
            borders_ok = True
            if strict:
                top_ok   = _is_grey_row_span(ws, max(1, r1-1), max(1, c1-1), c2, ref_color, tol, required_ratio)
                bot_ok   = _is_grey_row_span(ws, min(u_r2, r2+1), max(1, c1-1), c2, ref_color, tol, required_ratio)
                left_ok  = _is_grey_col_span(ws, max(1, c1-1), max(1, r1-1), r2, ref_color, tol, required_ratio)
                right_ok = _is_grey_col_span(ws, min(u_c2, c2+1), max(1, r1-1), r2, ref_color, tol, required_ratio)
                borders_ok = (top_ok and bot_ok and left_ok and right_ok)
            if not borders_ok:
                continue

            # keep if content or chart inside
            if _zone_has_chart(ws, r1, c1, r2, c2) or _zone_nonempty_count(ws, addr) >= min_nonempty:
                kept.append(addr)
                seen.add(key)

        if not kept:
            return []

        for idx, addr in enumerate(kept, start=1):
            try:
                app = getattr(ws, "Application", None) or getattr(ws.Parent, "Application", None)
                if app is not None:
                    try: app.PrintCommunication = False
                    except Exception: pass
                ws.PageSetup.PrintArea = addr
                _apply_common_layout(
                    ws.PageSetup,
                    fit_w=True,
                    fit_tall=True,
                    orientation=cfg.get("orientation", "landscape"),
                    margins_pts=int(cfg.get("margins_pts", 18)),
                )
                tmp = make_temp_path(f"_graph_zone_{idx}.pdf")
                if export_worksheet_to_pdf(ws, tmp):
                    out_paths.append(tmp)
                if app is not None:
                    try: app.PrintCommunication = True
                    except Exception: pass
            except Exception as e:
                print(f"  [!] Zone {idx} export failed: {e}")
    finally:
        _restore_pagesetup(ws, snap)
    return out_paths


def _log_pdf_pagesizes(pdf_path: Path) -> None:
    try:
        from PyPDF2 import PdfReader
        r = PdfReader(str(pdf_path))
        sizes = []
        for p in r.pages:
            mb = p.mediabox
            w = float(mb.width)
            h = float(mb.height)
            sizes.append(f"{int(round(w))}x{int(round(h))}")
        uniq = ", ".join(sorted(set(sizes)))
        print(f"    page sizes (pt): {uniq}")
    except Exception as e:
        print(f"    [log] could not read page sizes: {e}")

# ---------------- Main per-workbook logic ----------------

def process_workbook(excel, in_path: Path, out_dir: Path, cfg: dict) -> Optional[Path]:
    print(f"\n[+] {in_path}")
    wb = None
    temp_parts: List[Path] = []

    pats_conv = compile_patterns(cfg["patterns"].get("convergences", []))
    pats_depl = compile_patterns(cfg["patterns"].get("deplacements", []))
    pats_graph = compile_patterns(cfg["patterns"].get("graphiques", []))

    try:
        wb = excel.Workbooks.Open(str(in_path))

        # ---------- Convergences ----------
        sh_conv = find_sheet_by_patterns(wb, pats_conv)
        if sh_conv is not None:
            try:
                configure_pagesetup_for_table(
                    sh_conv,
                    cfg.get("titles_repeat_rows", "1:9"),
                    cfg.get("fit_to_one_page_width", True),
                    orientation=cfg.get("orientation", "landscape"),
                    margins_pts=int(cfg.get("margins_pts", 18))
                )
                last_col = max(
                    last_col_from_header_row(sh_conv, int(cfg.get("header_row", 9))),
                    last_col_from_merged_row(sh_conv, int(cfg.get("merged_hint_row", 5)))
                )
                last_row = last_data_row_in_col_a(sh_conv)
                set_print_area(sh_conv, last_row, last_col)
                tmp_pdf = make_temp_path("_convergences.pdf")
                if export_worksheet_to_pdf(sh_conv, tmp_pdf):
                    temp_parts.append(tmp_pdf)
                try: sh_conv.PageSetup.PrintArea = ""
                except Exception: pass
            except Exception as e:
                print(f"  [!] Convergences failure: {e}")
        else:
            print("  [-] Sheet Convergences not found (skipped)")

        # ---------- Déplacements ----------
        def _last_col_deplacements(ws):
            # Prefer merged A5 (column 1) extent
            try:
                ma = ws.Cells(int(cfg.get("merged_hint_row", 5)), 1).MergeArea
                if ma is not None:
                    return ma.Column + ma.Columns.Count - 1
            except Exception:
                pass
            # Fallback: look for stop label in header row
            label = normalize_name(cfg.get("deplacements_stop_label", "point bas droit"))
            hdr_row = int(cfg.get("header_row", 9))
            try:
                last_c = ws.Cells(hdr_row, ws.Columns.Count).End(XL_TOLEFT).Column
                for c in range(1, last_c + 1):
                    try:
                        val = normalize_name(ws.Cells(hdr_row, c).Value)
                    except Exception:
                        val = ""
                    if val == label:
                        return c
            except Exception:
                pass
            return last_col_from_header_row(ws, hdr_row)

        sh_depl = find_sheet_by_patterns(wb, pats_depl)
        if sh_depl is not None:
            try:
                configure_pagesetup_for_table(
                    sh_depl,
                    cfg.get("titles_repeat_rows", "1:9"),
                    cfg.get("fit_to_one_page_width", True),
                    orientation=cfg.get("orientation", "landscape"),
                    margins_pts=int(cfg.get("margins_pts", 18))
                )
                last_col = _last_col_deplacements(sh_depl)
                last_row = last_data_row_in_col_a(sh_depl)
                set_print_area(sh_depl, last_row, last_col)
                tmp_pdf = make_temp_path("_deplacements.pdf")
                if export_worksheet_to_pdf(sh_depl, tmp_pdf):
                    temp_parts.append(tmp_pdf)
                try: sh_depl.PageSetup.PrintArea = ""
                except Exception: pass
            except Exception as e:
                print(f"  [!] Déplacements failure: {e}")
        else:
            print("  [-] Sheet Déplacements not found (skipped)")

        # ---------- Graphiques ----------
        sh_graph = find_sheet_by_patterns(wb, pats_graph)
        if bool(cfg.get("include_chart_sheets", False)):
            for ch in chartsheets_by_patterns(wb, pats_graph):
                tmp_pdf = make_temp_path("_chartsheet.pdf")
                if export_chartsheet_to_pdf(
                    ch,
                    tmp_pdf,
                    orientation=cfg.get("orientation", "landscape"),
                    margins_pts=int(cfg.get("margins_pts", 18))
                ):
                    temp_parts.append(tmp_pdf)
        if sh_graph is not None:
            try:
                zone_pdfs = export_grey_zones_to_pdfs(sh_graph, cfg)
                if zone_pdfs:
                    temp_parts.extend(zone_pdfs)
                else:
                    # Fallback disabled by default; enable via config if desired
                    if bool(cfg.get("fallback_chart_objects", False)):
                        cos = sh_graph.ChartObjects()
                        for i in range(1, cos.Count + 1):
                            tmpc = make_temp_path("_chart.pdf")
                            if export_chartobject_area_to_pdf(
                                sh_graph, cos.Item(i), tmpc,
                                orientation=cfg.get("orientation", "landscape"),
                                margins_pts=int(cfg.get("margins_pts", 18))
                            ):
                                temp_parts.append(tmpc)
            except Exception as e:
                print(f"  [!] Graphiques failure: {e}")
        else:
            print("  [-] Sheet Graphiques not found (skipped embedded charts)")

        if not temp_parts:
            print("  [!] Nothing exported for this workbook.")
            return None

        final_pdf = out_dir / (in_path.stem + ".pdf")
        merge_pdfs(temp_parts, final_pdf)
        print(f"  [✔] Exported -> {final_pdf}")
        _log_pdf_pagesizes(final_pdf)
        return final_pdf

    except Exception as e:
        print(f"  [!] Error on {in_path.name}: {e}")
        return None
    finally:
        try:
            if wb is not None:
                wb.Close(SaveChanges=False)
        except Exception:
            pass
        for p in temp_parts:
            try:
                if p and p.exists():
                    p.unlink()
            except Exception:
                pass


# ---------------- Walk & run ----------------

def load_config(script_dir: Path) -> dict:
    """Load config.json from:
    1) SMC_CONFIG env var (full path), else
    2) next to the script, else
    3) current working directory (only if allow_cwd_config=True).
    Tolerates empty files/BOM and falls back to built-in CONFIG with clear logs.
    """
    cfg = CONFIG.copy()

    # 1) Env var override
    env_path = os.environ.get("SMC_CONFIG")
    tried = []
    if env_path:
        p = Path(env_path)
        tried.append(p)
        if p.exists():
            json_path = p
        else:
            print(f"SMC_CONFIG points to missing file: {p}")
            json_path = None
    else:
        json_path = None

    # 2) Next to script
    if json_path is None:
        p = script_dir / "config.json"
        tried.append(p)
        if p.exists():
            json_path = p

    # 3) Current working directory (optional)
    if json_path is None and bool(cfg.get("allow_cwd_config", False)):
        p = Path.cwd() / "config.json"
        tried.append(p)
        if p.exists():
            json_path = p

    if json_path is None:
        print("Using built-in CONFIG (no config.json found). Tried:")
        for t in tried:
            print(f"  - {t}")
        return cfg

    print(f"Attempting to load config from: {json_path}")

    try:
        raw = Path(json_path).read_text(encoding="utf-8-sig")
    except Exception as e:
        print(f"Could not read {json_path} ({e}); using built-in CONFIG")
        return cfg

    if not raw.strip():
        print(f"{json_path} is empty; using built-in CONFIG")
        return cfg

    try:
        loaded = json.loads(raw)
        for k, v in loaded.items():
            if k == "patterns":
                cfg.setdefault("patterns", {})
                cfg["patterns"].update(v or {})
            else:
                cfg[k] = v
        print(f"Using config file: {json_path}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {json_path} (line {e.lineno}, col {e.colno}): {e.msg}. Using built-in CONFIG.")
    except Exception as e:
        print(f"Error parsing {json_path}: {e}. Using built-in CONFIG.")

    try:
        print("Effective settings:")
        print(f"  root = {cfg.get('root')}")
        print(f"  out  = {cfg.get('out')}")
        pats = cfg.get('patterns', {})
        print(f"  patterns.convergences = {pats.get('convergences')}")
        print(f"  patterns.deplacements = {pats.get('deplacements')}")
        print(f"  patterns.graphiques  = {pats.get('graphiques')}")
    except Exception:
        pass

    return cfg


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    cfg = load_config(script_dir)

    root_path = expand_path(cfg.get("root"), script_dir=script_dir)
    out_path = expand_path(cfg.get("out"), script_dir=script_dir)

    ask = bool(cfg.get("ask_if_missing", True))

    if (root_path is None or not root_path.exists()) and ask:
        picked = pick_folder("Sélectionnez le dossier ROOT (Excel)")
        if picked:
            root_path = picked
        else:
            print("No ROOT selected. Aborting.", file=sys.stderr)
            sys.exit(2)

    if out_path is None and ask:
        picked = pick_folder("Sélectionnez le dossier de sortie (PDF)")
        if picked:
            out_path = picked
        else:
            print("No OUTPUT selected. Aborting.", file=sys.stderr)
            sys.exit(2)

    if root_path is None or out_path is None:
        print("Please set 'root' and 'out' in config.json or CONFIG.", file=sys.stderr)
        sys.exit(2)

    root = root_path.resolve()
    out_dir = out_path.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not root.exists():
        print(f"Root folder not found: {root}", file=sys.stderr)
        sys.exit(1)

    excel = start_excel()
    # Optionally lock ActivePrinter for consistent A4 behaviour
    try:
        want_prn = str(cfg.get("force_active_printer", "")).strip()
        cur_prn = getattr(excel, "ActivePrinter", "")
        print(f"ActivePrinter (before): {cur_prn}")
        if want_prn:
            try:
                excel.ActivePrinter = want_prn
                print(f"ActivePrinter (set):   {excel.ActivePrinter}")
            except Exception as e:
                print(f"[warn] cannot set ActivePrinter='{want_prn}': {e}")
    except Exception:
        pass
    ok = 0
    total = 0

    # --- Build file list according to config
    recursive = bool(cfg.get("recursive", False))
    include_globs = list(cfg.get("include_globs", ["*.xlsx", "*.xlsm"]))
    exclude_globs = list(cfg.get("exclude_globs", ["~$*"]))
    allowed_subdirs = [str(Path(s).as_posix()).strip("/") for s in cfg.get("allowed_subdirs", []) if str(s).strip()]
    forbidden_subdirs = [str(Path(s).as_posix()).strip("/") for s in cfg.get("forbidden_subdirs", []) if str(s).strip()]
    dry_run = bool(cfg.get("dry_run", False))
    max_files = int(cfg.get("max_files", 0))

    def _allowed_by_subdirs(relpath_posix: str) -> bool:
        if allowed_subdirs:
            if not any(relpath_posix.startswith(d + "/") or relpath_posix == d for d in allowed_subdirs):
                return False
        if forbidden_subdirs:
            if any(relpath_posix.startswith(d + "/") or relpath_posix == d for d in forbidden_subdirs):
                return False
        return True

    candidates: List[Path] = []
    iterator = root.rglob("*") if recursive else root.glob("*")
    for p in iterator:
        if not p.is_file():
            continue
        # Jail under root, even via symlink
        try:
            _ = p.resolve().relative_to(root.resolve())
        except Exception:
            continue
        rel = p.relative_to(root).as_posix()
        name = p.name
        if not any(fnmatch.fnmatch(name, pat) for pat in include_globs):
            continue
        if any(fnmatch.fnmatch(name, pat) for pat in exclude_globs):
            continue
        if not _allowed_by_subdirs(rel):
            continue
        candidates.append(p)
        if max_files > 0 and len(candidates) >= max_files:
            break

    print("\nScan summary:")
    print(f"  root           = {root}")
    print(f"  recursive      = {recursive}")
    print(f"  files matched  = {len(candidates)}")
    if allowed_subdirs:
        print(f"  allowed_subdirs = {allowed_subdirs}")
    if forbidden_subdirs:
        print(f"  forbidden_subdirs = {forbidden_subdirs}")

    if dry_run:
        print("\n[dry_run] Files that would be processed:")
        for p in candidates:
            print(f"  - {p}")
        close_excel(excel)
        return

    try:
        for p in candidates:
            total += 1
            if process_workbook(excel, p, out_dir, cfg):
                ok += 1
        print(f"\nDone. {ok}/{total} workbooks exported.")
    finally:
        close_excel(excel)


if __name__ == "__main__":
    main()
