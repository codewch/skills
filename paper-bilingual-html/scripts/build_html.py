#!/usr/bin/env python
"""Inject base64 images into a bilingual HTML template and write the final file.

The template contains placeholders of the form {{FIG1}}, {{FIG2}}, ... that are
replaced with `data:image/...;base64,...` data URLs built from JPEG/PNG files in
the image directory.

Usage:
    py build_html.py <template.html> <images_dir> <output.html>

The script maps placeholder {{FIGn}} to the first file matching Fign.{jpg,png,webp}
in <images_dir> (case-insensitive). Unmatched placeholders are reported.
"""
import argparse
import base64
import glob
import os
import re
import sys

MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".webp": "image/webp"}


def find_image(images_dir, n):
    for ext in MIME:
        p = os.path.join(images_dir, f"Fig{n}{ext}")
        if os.path.exists(p):
            return p
        p = os.path.join(images_dir, f"fig{n}{ext}")
        if os.path.exists(p):
            return p
    return None


def main():
    ap = argparse.ArgumentParser(description="Inject base64 images into HTML template")
    ap.add_argument("template", help="path to the template HTML with {{FIGn}} placeholders")
    ap.add_argument("images_dir", help="directory containing FigN.jpg/png files")
    ap.add_argument("output", help="path to write the final HTML")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    with open(args.template, "r", encoding="utf-8") as f:
        html = f.read()

    placeholders = sorted(set(re.findall(r"\{\{FIG(\d+)\}\}", html)))
    if not placeholders:
        print("WARNING: no {{FIGn}} placeholders found in template; nothing to inject.")
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"written: {args.output}")
        return

    injected = 0
    for n in placeholders:
        img_path = find_image(args.images_dir, int(n))
        if img_path is None:
            print(f"WARNING: no image found for {{FIG{n}}} in {args.images_dir}")
            continue
        ext = os.path.splitext(img_path)[1].lower()
        mime = MIME.get(ext, "image/jpeg")
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        html = html.replace("{{FIG%s}}" % n, b64)
        injected += 1
        print(f"  {{FIG{n}}} <- {os.path.basename(img_path)} ({len(b64)} chars)")

    leftover = re.findall(r"\{\{FIG\d+\}\}", html)
    if leftover:
        print(f"WARNING: leftover placeholders: {leftover}")

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"injected {injected}/{len(set(placeholders))} images -> {args.output}")


if __name__ == "__main__":
    main()
