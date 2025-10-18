#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch PDF standardizer to A4 landscape with adaptive margins (table vs. graph pages),
while preserving vector content (no rasterization).

Requirements:
    pip install pymupdf

Examples:
    python batch_pdf_standardize.py --root "/path/to/folder" --out "/path/to/out"
    python batch_pdf_standardize.py --file "/path/to/file.pdf" --margin-table-mm 20 --margin-graph-mm 5
"""

import argparse
import sys
import os
import fitz  # PyMuPDF
from typing import Optional, Tuple

A4_PORTRAIT = (595.28, 841.89)
A4_LANDSCAPE = (841.89, 595.28)
PT_PER_MM = 2.83465

def mm_to_pt(mm: float) -> float:
    return mm * PT_PER_MM

def guess_page_kind(page: fitz.Page, text_len_threshold: int = 300,
                    img_weight: float = 1.0, draw_weight: float = 0.7) -> str:
    """
    Heuristic classifier:
      - If lots of text and few images/drawings -> 'table'
      - If lots of images/drawings relative to text -> 'graph'
    """
    text = page.get_text("text") or ""
    text_len = len(text.strip())

    # Count image xrefs on the page
    try:
        images = page.get_images(full=True)
        img_count = len(images)
    except Exception:
        img_count = 0

    # Count vector drawings (lines, curves... typical for charts)
    try:
        drawings = page.get_drawings()
        draw_count = len(drawings)
    except Exception:
        draw_count = 0

    # Feature score
    # More text pushes toward "table", more images/draws push toward "graph"
    # Tuneable weights
    score = text_len - img_weight * (img_count * 500) - draw_weight * (draw_count * 60)

    # Light hint if the text contains common table-ish separators
    if any(sep in text for sep in ["\t", "  ", "|"]):
        score += 200

    # Decide
    return "table" if (text_len > text_len_threshold and score >= 0) else "graph"

def place_source_page_on_a4_landscape(new_doc: fitz.Document,
                                      src_doc: fitz.Document,
                                      page: fitz.Page,
                                      margin_pt: float,
                                      keep_centered: bool = True) -> None:
    """Create an A4 landscape page and place src page scaled inside margins, preserving vectors."""
    a4w, a4h = A4_LANDSCAPE
    new_page = new_doc.new_page(width=a4w, height=a4h)

    rect = page.rect
    avail_w = a4w - 2 * margin_pt
    avail_h = a4h - 2 * margin_pt
    scale = min(avail_w / rect.width, avail_h / rect.height)

    # compute target rectangle
    new_w = rect.width * scale
    new_h = rect.height * scale
    if keep_centered:
        x0 = (a4w - new_w) / 2.0
        y0 = (a4h - new_h) / 2.0
    else:
        x0 = margin_pt
        y0 = margin_pt
    target = fitz.Rect(x0, y0, x0 + new_w, y0 + new_h)

    # Copy vector content
    new_page.show_pdf_page(target, src_doc, page.number)

def process_pdf(in_pdf_path: str,
                out_pdf_path: str,
                margin_table_mm: float = 20.0,
                margin_graph_mm: float = 5.0,
                text_len_threshold: int = 300) -> Tuple[int, int]:
    """Process a single PDF. Returns (#pages_table, #pages_graph)."""
    doc = fitz.open(in_pdf_path)
    new_doc = fitz.open()

    table_count = 0
    graph_count = 0

    for p in doc:
        kind = guess_page_kind(p, text_len_threshold=text_len_threshold)
        margin_pt = mm_to_pt(margin_table_mm if kind == "table" else margin_graph_mm)
        if kind == "table":
            table_count += 1
        else:
            graph_count += 1
        place_source_page_on_a4_landscape(new_doc, doc, p, margin_pt)

    # ensure output directory exists
    os.makedirs(os.path.dirname(out_pdf_path) or ".", exist_ok=True)
    new_doc.save(out_pdf_path)
    new_doc.close()
    doc.close()

    return table_count, graph_count

def iter_pdf_files(root: str):
    for base, _, files in os.walk(root):
        for f in files:
            if f.lower().endswith(".pdf"):
                yield os.path.join(base, f)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Standardize PDFs to A4 landscape with adaptive margins (table vs graph), preserving vectors.")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--root", help="Root folder to search PDFs (recursive).")
    g.add_argument("--file", help="Single PDF file to process.")
    parser.add_argument("--out", help="Output folder (if not set, write next to input).")
    parser.add_argument("--margin-table-mm", type=float, default=20.0, help="Margin for table-like pages in mm (default: 20).")
    parser.add_argument("--margin-graph-mm", type=float, default=5.0, help="Margin for graph-like pages in mm (default: 5).")
    parser.add_argument("--text-len-threshold", type=int, default=300, help="Min text length to consider a page as 'table' (default: 300).")

    args = parser.parse_args(argv)

    inputs = []
    if args.file:
        if not os.path.isfile(args.file):
            print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
            return 2
        inputs = [args.file]
    else:
        if not os.path.isdir(args.root):
            print(f"[ERROR] Folder not found: {args.root}", file=sys.stderr)
            return 2
        inputs = list(iter_pdf_files(args.root))

    if not inputs:
        print("[INFO] No PDF files found.", file=sys.stderr)
        return 1

    total_tables = 0
    total_graphs = 0
    for in_path in inputs:
        base = os.path.basename(in_path)
        name, ext = os.path.splitext(base)

        if args.out:
            os.makedirs(args.out, exist_ok=True)
            out_path = os.path.join(args.out, f"{name}_A4_landscape_marged.pdf")
        else:
            out_path = os.path.join(os.path.dirname(in_path), f"{name}_A4_landscape_marged.pdf")

        try:
            t_count, g_count = process_pdf(
                in_path,
                out_path,
                margin_table_mm=args.margin_table_mm,
                margin_graph_mm=args.margin_graph_mm,
                text_len_threshold=args.text_len_threshold,
            )
            total_tables += t_count
            total_graphs += g_count
            print(f"[OK] {base}: {t_count} table-like pages, {g_count} graph-like pages -> {out_path}")
        except Exception as e:
            print(f"[ERROR] Failed on {in_path}: {e}", file=sys.stderr)

    print(f"\n[SUMMARY] Tables: {total_tables} | Graphs: {total_graphs} | Files processed: {len(inputs)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
