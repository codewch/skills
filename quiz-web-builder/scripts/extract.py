#!/usr/bin/env python3
"""Extract text from a study-material file (PDF / PPTX / DOCX) for quiz data.

Usage:
    py extract.py <file_path> [--out out.txt]

Prints the extracted text to stdout (UTF-8). Use --out to also write a file.
Handles the common Windows pitfalls: UTF-8 stdout, non-ASCII paths,
and mojibake-free output.
"""
import sys, os, argparse

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def extract_pdf(path):
    import pdfplumber
    parts = []
    with pdfplumber.open(path) as pdf:
        for i, pg in enumerate(pdf.pages):
            t = pg.extract_text() or ''
            parts.append('===== PAGE %d =====' % (i + 1))
            parts.append(t)
    return '\n'.join(parts)


def extract_markitdown(path):
    from markitdown import MarkItDown
    md = MarkItDown()
    res = md.convert(path)
    return res.text_content


def extract_docx_fallback(path):
    """Fallback when markitdown is unavailable: dump paragraphs + tables in order."""
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    doc = Document(path)
    out = []
    for child in doc.element.body.iterchildren():
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            out.append(Paragraph(child, doc).text)
        elif tag == 'tbl':
            t = Table(child, doc)
            for r in t.rows:
                out.append(' | '.join(c.text.replace('\n', ' ') for c in r.cells))
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file_path')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    p = args.file_path
    ext = os.path.splitext(p)[1].lower()

    if ext == '.pdf':
        text = extract_pdf(p)
    elif ext == '.pptx':
        try:
            text = extract_markitdown(p)
        except Exception:
            text = extract_markitdown(p)  # re-raise if truly unavailable
    elif ext == '.docx':
        try:
            text = extract_markitdown(p)
        except Exception:
            text = extract_docx_fallback(p)
    else:
        # Unknown type: still try markitdown
        text = extract_markitdown(p)

    sys.stdout.write(text)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(text)


if __name__ == '__main__':
    main()
