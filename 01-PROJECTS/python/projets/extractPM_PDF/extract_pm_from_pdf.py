#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import re
import unicodedata
from pathlib import Path

try:
    from pdfminer.high_level import extract_text
except Exception:
    extract_text = None

try:
    import PyPDF2
except Exception:
    PyPDF2 = None

def strip_accents(s: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def normalize_text(s: str) -> str:
    return strip_accents(s).lower()

def normalize_num(s: str) -> str:
    return s.replace("\xa0", "").replace(" ", "").replace(",", ".")

def plausible_elevation(x: float) -> bool:
    return 10.0 <= x <= 100.0

def text_from_pdf(path: Path) -> str:
    if extract_text is not None:
        try:
            txt = extract_text(str(path))
            if txt and txt.strip():
                return txt
        except Exception:
            pass
    if PyPDF2 is not None:
        try:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                parts = []
                for page in reader.pages:
                    parts.append(page.extract_text() or "")
                return "\n".join(parts)
        except Exception:
            pass
    return ""

NUM_RE = re.compile(r"(?<!\d)(\d{2}(?:[.,]\d{1,2})?)(?!\d)")
PM_TOKENS = ("pm", "p.m", "p m")
MOY_TOKENS = ("moy", "moyen", "moyenne", "moy.", "mean")
CINTRE_TOKENS = ("cint", "cintre", "cint.", "c.")
TRAV_WORD_TOKENS = ("travee", "trave", "trv", "trv.")
TRAV_CODE_RE = re.compile(r"\b([a-z]?\d{2,4})\b", re.IGNORECASE)
TRAV_INLINE_RE = re.compile(r"\btrav(?:ee)?\s*([a-z]?\d{2,4})\b", re.IGNORECASE)

def first_number_in(s: str):
    m = NUM_RE.search(s)
    if not m:
        return None
    val = normalize_num(m.group(1))
    try:
        x = float(val)
    except ValueError:
        return None
    return x, val

def find_pm_moyen(lines):
    for l in lines:
        n = normalize_text(l)
        if ("pm" in n or any(t in n for t in PM_TOKENS)) and any(t in n for t in MOY_TOKENS):
            hit = first_number_in(l)
            if hit and plausible_elevation(hit[0]):
                return hit[1]
    for l in lines:
        n = normalize_text(l)
        if any(t in n for t in MOY_TOKENS):
            hit = first_number_in(l)
            if hit and plausible_elevation(hit[0]):
                return hit[1]
    return ""

def find_pm_cintre(lines):
    for l in lines:
        n = normalize_text(l)
        if any(t in n for t in CINTRE_TOKENS):
            hit = first_number_in(l)
            if hit and plausible_elevation(hit[0]):
                return hit[1]
    return ""

def find_pm_in_title(lines):
    head = lines[:40]
    title_like = list(head)
    for l in lines:
        n = normalize_text(l)
        if ("front" in n) or ("leve" in n) or ("ggs" in n) or ("trav" in n):
            title_like.append(l)
        if " pm" in " " + n or any(t in n for t in PM_TOKENS):
            title_like.append(l)
    seen, tlist = set(), []
    for l in title_like:
        if l not in seen:
            seen.add(l); tlist.append(l)
    for l in tlist:
        hit = first_number_in(l)
        if hit and plausible_elevation(hit[0]) and any(tok in normalize_text(l) for tok in (PM_TOKENS + ("pm",))):
            return hit[1], l
    for l in tlist:
        hit = first_number_in(l)
        if hit and plausible_elevation(hit[0]):
            return hit[1], l
    return "", ""

def find_travee(lines, filename):
    for l in lines:
        m = TRAV_INLINE_RE.search(l)
        if m:
            return m.group(1).upper()
    for l in lines:
        n = normalize_text(l)
        if any(tok in n for tok in TRAV_WORD_TOKENS):
            m = TRAV_CODE_RE.search(l)
            if m:
                return m.group(1).upper()
    m = re.search(r"\b([A-Z])\s?(\d{2,4})\b", filename, re.IGNORECASE)
    if m:
        return (m.group(1) + m.group(2)).upper()
    for l in lines:
        n = normalize_text(l)
        if any(tok in n for tok in CINTRE_TOKENS):
            m = TRAV_CODE_RE.search(l)
            if m:
                return m.group(1).upper()
    return ""

def extract_fields(full_text: str, filename: str):
    lines = [l.strip() for l in full_text.splitlines() if l and l.strip()]
    return {
        "pm_moyen":  find_pm_moyen(lines),
        "pm_cintre": find_pm_cintre(lines),
        "pm_title":  find_pm_in_title(lines)[0],
        "travee":    find_travee(lines, filename),
        "title_line": find_pm_in_title(lines)[1],
    }

def scan_dir(root: Path, out_csv: Path, verbose: bool, keep_without_front: bool):
    rows = []
    scanned = 0
    matched = 0
    empty_text = 0

    all_pdfs = list(root.rglob("*.pdf"))
    if verbose:
        print(f"[INFO] PDFs trouvés (récursif): {len(all_pdfs)}")

    for pdf_path in all_pdfs:
        scanned += 1
        name_has_front = ("front" in pdf_path.name.lower())
        if not name_has_front and not keep_without_front:
            if verbose:
                print(f"[SKIP] (filtre 'front') {pdf_path.name}")
            continue

        matched += 1
        if verbose:
            print(f"[RUN ] {pdf_path}")

        txt = text_from_pdf(pdf_path)
        if not txt.strip():
            empty_text += 1
            rows.append({
                "file": str(pdf_path),
                "filename": pdf_path.name,
                "pm_moyen": "",
                "pm_cintre": "",
                "pm_in_title": "",
                "travee": "",
                "title_line": "",
                "notes": "Aucun texte extrait (scan probable / OCR requis)",
            })
            if verbose:
                print(f"[WARN] Texte vide → {pdf_path.name}")
            continue

        data = extract_fields(txt, pdf_path.name)
        rows.append({
            "file": str(pdf_path),
            "filename": pdf_path.name,
            "pm_moyen": data["pm_moyen"],
            "pm_cintre": data["pm_cintre"],
            "pm_in_title": data["pm_title"],
            "travee": data["travee"],
            "title_line": data["title_line"],
            "notes": "",
        })

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["file", "filename", "pm_moyen", "pm_cintre", "pm_in_title", "travee", "title_line", "notes"]
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    return {
        "scanned": scanned,
        "matched": matched,
        "written": len(rows),
        "empty_text": empty_text
    }

def main():
    ap = argparse.ArgumentParser(description="Extraction souple des PM depuis des PDFs.")
    ap.add_argument("root", nargs="?", help="Dossier racine à analyser (récursif)")
    ap.add_argument("-o", "--out", default="pm_extraction.csv", help="CSV de sortie")
    ap.add_argument("-v", "--verbose", action="store_true", help="Affiche le détail des opérations")
    ap.add_argument("--include-no-front", action="store_true",
                    help="Inclure aussi les PDFs dont le nom ne contient pas 'front' (pour débogage)")
    args = ap.parse_args()

    # Valeurs par défaut si lancé sans arguments (évite SystemExit:2 et 'rien ne se passe')
    if not args.root:
        # >>>> ADAPTE ICI TES CHEMINS PAR DÉFAUT <<<<
        args.root = r"C:\data\11-CHANTIERS\BURE\PDF"
        args.out  = r"C:\data\11-CHANTIERS\BURE\pm_extraction.csv"
        args.verbose = True
        print("[INFO] Aucune racine fournie, utilisation des chemins par défaut.")
        print(f"[INFO] root = {args.root}")
        print(f"[INFO] out  = {args.out}")

    root = Path(args.root).expanduser().resolve()
    out_csv = Path(args.out).expanduser().resolve()

    if args.verbose:
        print(f"[INFO] Analyse de: {root}")
        print(f"[INFO] CSV sortie: {out_csv}")
        print(f"[INFO] Filtre nom contient 'front' = {not args.include_no_front}")

    stats = scan_dir(root, out_csv, args.verbose, args.include_no_front)

    print("\n=== RÉSUMÉ ===")
    print(f"PDFs scannés  : {stats['scanned']}")
    print(f"PDFs retenus  : {stats['matched']} (filtre 'front' appliqué: {not args.include_no_front})")
    print(f"Lignes écrites: {stats['written']}")
    print(f"Texte vide    : {stats['empty_text']} (probable OCR requis)")
    print(f"CSV           : {out_csv}")

if __name__ == "__main__":
    main()
