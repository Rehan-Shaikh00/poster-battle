"""Build the final poster: embed charts as base64, write poster.html,
render poster.pdf (A4 landscape) + poster_preview.png for review."""
import base64, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
CHARTS = os.path.join(HERE, "..", "code", "output")

tpl = open(os.path.join(HERE, "poster_template.html"), encoding="utf-8").read()

def embed(m):
    name = m.group(1)
    with open(os.path.join(CHARTS, name), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"

html = re.sub(r"IMG:([\w.]+\.png)", embed, tpl)
with open(os.path.join(HERE, "poster.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("wrote poster.html  (self-contained, charts embedded)")

from weasyprint import HTML
HTML(string=html, base_url=HERE).write_pdf(os.path.join(HERE, "poster.pdf"))
print("wrote poster.pdf   (A4 landscape, print-ready)")

import pypdfium2 as pdfium
pdf = pdfium.PdfDocument(os.path.join(HERE, "poster.pdf"))
img = pdf[0].render(scale=110 / 72).to_pil()
img.save(os.path.join(HERE, "poster_preview.png"))
print("wrote poster_preview.png", img.size)
