#!/usr/bin/env python
"""Extract text (column-aware) and images (as JPEG) from an academic paper PDF.

Usage:
    py extract_pdf.py <pdf_path> [--out <output_dir>] [--max-width 1400] [--quality 85]

Outputs:
    <output_dir>/extracted_text.txt   column-reconstructed plain text
    <output_dir>/images/FigN.jpg      extracted figures converted to JPEG
    <output_dir>/images_manifest.txt  figure -> page / size mapping

The text is reconstructed for two-column journal layouts: words are grouped into
visual lines, lines are classified as full-width / left-column / right-column, and
emitted as "TOP/FULL-WIDTH", "LEFT COLUMN", "RIGHT COLUMN" sections per page so a
translator can read each column in the correct order.

Requires: pymupdf (fitz), Pillow.
"""
import argparse
import io
import os
import sys

import pymupdf

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

# A4 two-column layout thresholds (points). Adjust if the PDF has a different page
# width or column gutter. Left column ends ~265, right column starts ~295 for A4.
COL_LEFT_MAX = 285   # a line entirely left of this x1 is a LEFT column line
COL_RIGHT_MIN = 290  # a line entirely right of this x0 is a RIGHT column line
FULL_X0_MAX = 200    # a line starting left of this AND ...
FULL_X1_MIN = 390    # ... ending right of this is full-width
LINE_Y_TOL = 4.5     # words within this vertical distance belong to the same line
WORD_GAP = 18        # horizontal gap larger than this splits a line (column gutter)


def build_visual_lines(words):
    """Group words into visual lines, splitting at the column gutter."""
    words = [w for w in words if w[4].strip()]
    words.sort(key=lambda w: (round(w[1], 1), w[0]))
    lines = []
    cur = []
    for w in words:
        if not cur:
            cur = [w]
            continue
        prev = cur[-1]
        same_y = abs(w[1] - prev[1]) <= LINE_Y_TOL
        gap = w[0] - prev[2]
        if same_y and gap <= WORD_GAP:
            cur.append(w)
        else:
            lines.append(sorted(cur, key=lambda z: z[0]))
            cur = [w]
    if cur:
        lines.append(sorted(cur, key=lambda z: z[0]))
    return lines


def classify_line(line):
    xs = [w[0] for w in line]
    xe = [w[2] for w in line]
    x0 = min(xs)
    x1 = max(xe)
    yc = sum(w[1] for w in line) / len(line)
    text = " ".join(w[4] for w in line)
    if x0 < FULL_X0_MAX and x1 > FULL_X1_MIN:
        kind = "F"
    elif x1 < COL_LEFT_MAX:
        kind = "L"
    elif x0 > COL_RIGHT_MIN:
        kind = "R"
    else:
        kind = "F"
    return yc, kind, text


def render_page(page):
    lines = [classify_line(ln) for ln in build_visual_lines(page.get_text("words"))]
    top = [t for y, k, t in lines if k == "F" and y < 700]
    left = [(y, t) for y, k, t in lines if k == "L"]
    right = [(y, t) for y, k, t in lines if k == "R"]
    left.sort()
    right.sort()
    out = ["== TOP/FULL-WIDTH =="]
    out.extend(top)
    out.append("== LEFT COLUMN ==")
    out.extend(t for y, t in left)
    out.append("== RIGHT COLUMN ==")
    out.extend(t for y, t in right)
    return "\n".join(out)


def extract_text(doc):
    parts = []
    for i, page in enumerate(doc):
        parts.append(f"\n########################## PAGE {i + 1} ##########################\n")
        parts.append(render_page(page))
    return "\n".join(parts)


def save_image_jpeg(doc, xref, outpath, max_w, quality):
    """Convert an embedded image xref to a downscaled RGB JPEG. Returns (w, h)."""
    pix = pymupdf.Pixmap(doc, xref)
    if pix.n - pix.alpha >= 4:  # CMYK / alpha -> flatten to RGB
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    png_bytes = pix.tobytes("png")
    if Image is None:
        # Fallback: write PNG directly (no JPEG / no downscale).
        outpath = outpath.rsplit(".", 1)[0] + ".png"
        with open(outpath, "wb") as f:
            f.write(png_bytes)
        return pix.width, pix.height
    im = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, int(im.height * max_w / im.width)), Image.LANCZOS)
    im.save(outpath, "JPEG", quality=quality, optimize=True)
    return im.width, im.height


def extract_images(doc, outdir, max_w, quality):
    os.makedirs(outdir, exist_ok=True)
    seen = set()
    manifest = []
    fig_no = 0
    for pno in range(len(doc)):
        for img in doc[pno].get_images(full=True):
            xref = img[0]
            if xref in seen:
                continue
            seen.add(xref)
            fig_no += 1
            name = f"Fig{fig_no}"
            outpath = os.path.join(outdir, name + ".jpg")
            try:
                w, h = save_image_jpeg(doc, xref, outpath, max_w, quality)
            except Exception as exc:  # pragma: no cover
                manifest.append(f"{name}: page {pno + 1} FAILED ({exc})")
                continue
            manifest.append(f"{name}: page {pno + 1}, size {w}x{h}, file {name}.jpg")
    return manifest


def main():
    ap = argparse.ArgumentParser(description="Extract text and images from a paper PDF")
    ap.add_argument("pdf", help="path to the PDF file")
    ap.add_argument("--out", help="output directory (default: alongside PDF)")
    ap.add_argument("--max-width", type=int, default=1400, help="max image width (px)")
    ap.add_argument("--quality", type=int, default=85, help="JPEG quality 1-100")
    args = ap.parse_args()

    pdf = os.path.abspath(args.pdf)
    if not os.path.exists(pdf):
        print(f"ERROR: PDF not found: {pdf}")
        sys.exit(1)
    outdir = args.out or os.path.join(os.path.dirname(pdf), "bilingual_work")
    os.makedirs(outdir, exist_ok=True)

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    doc = pymupdf.open(pdf)

    text_path = os.path.join(outdir, "extracted_text.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(extract_text(doc))

    img_dir = os.path.join(outdir, "images")
    manifest = extract_images(doc, img_dir, args.max_width, args.quality)
    manifest_path = os.path.join(outdir, "images_manifest.txt")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(manifest))

    print(f"pages: {len(doc)}")
    print(f"text  -> {text_path}")
    print(f"images -> {img_dir} ({len(manifest)} figures)")
    print(f"manifest -> {manifest_path}")
    for line in manifest:
        print("  " + line)


if __name__ == "__main__":
    main()
