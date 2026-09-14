"""Build the standard-layout (sample wireframe) TREMORWATCH poster.

Reads poster_standard_template.html, base64-embeds the light-theme charts,
renders the PDF with WeasyPrint, and rasterises a high-res PNG preview
(400 DPI) with pypdfium2.

Run:  python build_standard_poster.py
      (regenerate charts first with make_charts.py)
"""
import base64
from pathlib import Path

HERE = Path(__file__).parent
TEMPLATE = HERE / "poster_standard_template.html"
CHARTS = HERE / "charts"
PDF_OUT = HERE / "poster_standard.pdf"
PNG_OUT = HERE / "poster_standard.png"


def data_uri(p: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode("ascii")


def main() -> None:
    html = TEMPLATE.read_text(encoding="utf-8")
    for name in ("process_diagram.png", "mag_bands_light.png",
                 "risk_zones_bars_light.png", "risk_map_light.png"):
        html = html.replace(f"IMG:{name}", data_uri(CHARTS / name))
    (HERE / "poster_standard.html").write_text(html, encoding="utf-8")

    from weasyprint import HTML
    HTML(string=html, base_url=str(HERE)).write_pdf(str(PDF_OUT))
    print(f"PDF: {PDF_OUT}")

    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(str(PDF_OUT))
    page = pdf[0]
    bmp = page.render(scale=400 / 72)
    bmp.to_pil().save(PNG_OUT)
    print(f"PNG (400 DPI): {PNG_OUT}")


if __name__ == "__main__":
    main()
