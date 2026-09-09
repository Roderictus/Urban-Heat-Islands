"""Build Spanish HTML + PDF report and a website-ready folder."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fpdf import FPDF
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "reports" / "cdmx_heat_islands"
OUT = ROOT / "reports" / "sitio_islas_calor_cdmx"
ASSETS = OUT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

meta = json.loads((SRC / "profiles.json").read_text(encoding="utf-8"))
df = pd.DataFrame(meta["profiles"])
T_RURAL = float(meta["t_rural"])
N_LANDSAT = int(meta["n_landsat"])

HERO = SRC / "heat_over_streets_35c" / "cdmx_heat_over_streets_35c.png"
VEG = SRC / "figures" / "cdmx_vegetation_temperature.png"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.facecolor": "white",
    "figure.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def watermark(fig):
    fig.text(
        0.99, 0.01, "Anaplian.com", ha="right", va="bottom",
        fontsize=10, fontweight="bold", color="#8d8d8d", alpha=0.85,
    )


def crop_uniform_border(im: Image.Image, tol: int = 12, pad: int = 6) -> Image.Image:
    arr = np.asarray(im.convert("RGB"))
    bg = arr[0, 0].astype(int)
    diff = np.abs(arr.astype(int) - bg).sum(axis=2)
    content = diff > tol
    if not content.any():
        return im
    ys, xs = np.where(content)
    left = max(0, int(xs.min()) - pad)
    top = max(0, int(ys.min()) - pad)
    right = min(im.width, int(xs.max()) + 1 + pad)
    bottom = min(im.height, int(ys.max()) + 1 + pad)
    return im.crop((left, top, right, bottom))


def bar_chart(series, names, title, xlabel, outfile, color):
    order = series.argsort()[::-1]
    names = [names[i] for i in order]
    vals = series.iloc[order] if hasattr(series, "iloc") else series[order]
    fig, ax = plt.subplots(figsize=(9.4, 12.6))
    ax.barh(range(len(names))[::-1], vals, color=color, height=0.72)
    ax.set_yticks(range(len(names))[::-1], names, fontsize=9)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_title(title, fontsize=13, fontweight="bold", loc="left", pad=10)
    for i, v in zip(range(len(names))[::-1], vals):
        ax.text(v + 0.25, i, f"{v:.1f}", va="center", fontsize=8, color="#333")
    ax.set_xlim(0, max(vals) * 1.12)
    fig.tight_layout(rect=(0.02, 0.03, 0.98, 0.99))
    watermark(fig)
    fig.savefig(outfile, dpi=160, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    crop_uniform_border(Image.open(outfile)).save(outfile)


bar_chart(
    df["lst_peak_C"],
    df["alcaldia"].tolist(),
    "Temperatura máxima de superficie por alcaldía",
    "Máxima (°C) — Landsat 8/9, abril–mayo 2026, ~10:30 local",
    ASSETS / "03_barras_temperatura_maxima.png",
    "#d94801",
)
bar_chart(
    df["lst_mean_C"],
    df["alcaldia"].tolist(),
    "Temperatura promedio de superficie por alcaldía",
    "Promedio (°C) — Landsat 8/9, abril–mayo 2026, ~10:30 local",
    ASSETS / "04_barras_temperatura_promedio.png",
    "#e6550d",
)

shutil.copy2(HERO, ASSETS / "01_cdmx_transparencia.png")
shutil.copy2(VEG, ASSETS / "02_cdmx_vegetacion_lado_a_lado.png")

GALLERY_DIR = ASSETS / "galeria_38c"
if GALLERY_DIR.exists():
    shutil.rmtree(GALLERY_DIR)
GALLERY_DIR.mkdir()
gallery_src = [("Ciudad de México", SRC / "figures" / "cdmx_heat_over_streets.png")]
for r in df.itertuples():
    p = SRC / "figures" / f"{r.slug}_heat_over_streets.png"
    if p.exists():
        gallery_src.append((r.alcaldia, p))
thumbs = []
for i, (name, path) in enumerate(gallery_src, 1):
    im = crop_uniform_border(Image.open(path).convert("RGB"), tol=14, pad=4)
    im.thumbnail((520, 620), Image.Resampling.LANCZOS)
    outp = GALLERY_DIR / f"{i:02d}_{path.stem}.jpg"
    im.save(outp, quality=85, optimize=True)
    thumbs.append((name, outp))
gallery_html = "\n".join(
    f'<figure class="tile"><img src="assets/galeria_38c/{p.name}" alt="{name}"><figcaption>{name}</figcaption></figure>'
    for name, p in thumbs
)

PARRAFO = (
    f"Este reporte se basa en {N_LANDSAT} imágenes de los satélites Landsat 8 y Landsat 9 "
    "(Colección 2, nivel 2) adquiridas entre el 1 de abril y el 31 de mayo de 2026. "
    "Ese periodo de dos meses de primavera fue el que mejor cubrió la ciudad con cielo relativamente despejado; "
    "un recorte de tres meses (marzo a mayo) se evaluó, pero abril y mayo ofrecen un retrato más limpio de 2026. "
    "Los satélites cruzan el Valle de México hacia las 10:30 de la mañana, hora local (cerca de las 16:30 UTC). "
    "Lo que se muestra no es la temperatura del aire a la sombra, sino la de la superficie: techos, asfalto, suelo desnudo y vegetación. "
    "Por eso un techo o un estacionamiento puede marcar más de 50 °C cuando el aire ronda los 25 °C. "
    "La temperatura se calculó con la banda 10 del infrarrojo térmico (unos 10,6 a 11,2 micrómetros). "
    "El verdor se midió con el NDVI, un índice que compara la luz roja y la del infrarrojo cercano: "
    "la vegetación sana refleja poco el rojo y mucho el infrarrojo cercano, y aparece en verde oscuro en el mapa de al lado. "
    f"La columna de diferencia resta {T_RURAL:.1f} °C, que es la temperatura media de las zonas vegetales y rurales "
    "del sur y poniente de la ciudad —suelo de conservación con bosque y poca urbanización, sobre todo en "
    "La Magdalena Contreras, Cuajimalpa de Morelos, Tlalpan y Milpa Alta—, identificadas con el mapa global de "
    "asentamientos humanos de 2020 (clases rurales, sin agua)."
)

LEAD = (
    "En la Ciudad de México, las superficies urbanas más compactas del oriente y el centro "
    "se calientan claramente más que el bosque del sur-poniente. "
    f"Venustiano Carranza tiene el promedio más alto ({df.loc[df.alcaldia=='Venustiano Carranza','lst_mean_C'].iloc[0]:.1f} °C) "
    f"y Azcapotzalco el pico más extremo ({df.loc[df.alcaldia=='Azcapotzalco','lst_peak_C'].iloc[0]:.1f} °C). "
    f"La Magdalena Contreras, con más vegetación, queda {abs(df.loc[df.alcaldia=='La Magdalena Contreras','suhi_C'].iloc[0]):.1f} °C "
    "por debajo de esa referencia rural."
)

INTRO_P1 = (
    "El incremento de la temperatura media del planeta agrava la vulnerabilidad a las temperaturas "
    "excesivas. No se trata solo de un grado más en el promedio global: esa alza empuja más días "
    "hacia umbrales peligrosos para la salud, el trabajo al aire libre y las redes de agua y energía. "
    "En las ciudades el riesgo se concentra. El asfalto, el concreto, los techos oscuros y el metal "
    "absorben gran parte de la radiación solar y la devuelven como calor; a diferencia de un árbol "
    "o un suelo húmedo, casi no evaporan agua ni dan sombra. Las calles estrechas y los edificios "
    "altos forman cañones que atrapan el aire caliente, y el tráfico y los aires acondicionados "
    "suman más energía al entorno. El resultado son islas de calor: estacionamientos, naves, "
    "avenidas y cubiertas donde la superficie llega a temperaturas que el cuerpo no tolera si se "
    "está expuesto."
)

INTRO_P2 = (
    f"Con imágenes de los satélites Landsat 8 y Landsat 9 mapeamos, en la Ciudad de México, las "
    f"áreas urbanas con los picos más altos de temperatura de superficie. Usamos {N_LANDSAT} escenas "
    "de abril y mayo de 2026, tomadas hacia las 10:30 de la mañana, hora local, con cielo "
    "relativamente despejado. El sensor térmico —banda 10 del infrarrojo, entre 10,6 y 11,2 "
    "micrómetros— estima el calor del suelo, los techos y el pavimento, no el del aire a la sombra. "
    "En paralelo, el NDVI —un índice de verdor a partir del rojo y el infrarrojo cercano— muestra "
    "dónde hay vegetación densa. La temperatura de la ciudad se compara con la media de las "
    "zonas rurales y boscosas del sur-poniente (suelo de conservación). El contraste es nítido: "
    "Azcapotzalco alcanza picos de "
    f"{df.loc[df.alcaldia=='Azcapotzalco','lst_peak_C'].iloc[0]:.1f} °C en superficie, mientras "
    "La Magdalena Contreras y Cuajimalpa de Morelos permanecen cerca o por debajo de esa "
    "referencia vegetal."
)

INTRO_P3 = (
    "Esos picos no son un episodio aislado: con más olas de calor y más superficie impermeable, "
    "tienden a empeorar. Por eso sirven para identificar áreas de intervención. El urbanismo "
    "táctico permite probar, en semanas, sombras temporales, pintura de alto albedo en patios "
    "escolares o calles de juego, y banquetas más permeables, sin esperar un megaproyecto. La "
    "vegetación es la palanca más persistente: un árbol intercepta el sol, refresca el aire por "
    "transpiración y, como se ve en los mapas de NDVI, las colonias más verdes coinciden con "
    "superficies más frescas. Corredores de sombra, camellones arbolados, azoteas y muros verdes, "
    "y la protección del suelo de conservación del sur, reducen la carga térmica. Otras medidas "
    "suman: techos y pavimentos fríos, recuperar agua en chinampas y parques, limitar el "
    "estacionamiento descubierto y priorizar a quienes viven junto a las manchas más calientes "
    "—adultos mayores, infancia, trabajo al aire libre—. El dato satelital no sustituye el "
    "diseño local; señala dónde conviene actuar primero."
)

INTRO_HTML = f"<p>{INTRO_P1}</p>\n    <p>{INTRO_P2}</p>\n    <p>{INTRO_P3}</p>"

rows_html = "\n".join(
    f"<tr><td>{r.alcaldia}</td><td>{r.lst_peak_C:.1f}</td><td>{r.lst_mean_C:.1f}</td>"
    f"<td>{r.suhi_C:+.1f}</td></tr>"
    for r in df.itertuples()
)

html = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Islas de calor en la Ciudad de México — abril y mayo de 2026</title>
  <style>
    :root {{ --ink:#1a1a1a; --muted:#555; --line:#e6e1d8; --accent:#c2410c; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; color: var(--ink); background: #f7f4ef;
      font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      line-height: 1.55;
    }}
    header {{
      background: #111; color: #fff; padding: 36px 20px 28px;
    }}
    header .wrap, main, footer .wrap {{ max-width: 920px; margin: 0 auto; }}
    h1 {{ font-size: 1.85rem; margin: 0 0 8px; letter-spacing: -0.02em; }}
    .kicker {{ color: #f0c27a; font-size: 0.82rem; letter-spacing: 0.12em; text-transform: uppercase; }}
    main {{ padding: 28px 20px 64px; }}
    h2 {{ font-size: 1.25rem; margin: 2.2rem 0 0.7rem; }}
    figure {{ margin: 0 0 1.4rem; }}
    figure img {{ width: 100%; height: auto; background: #111; display: block; }}
    figcaption {{ font-size: 0.88rem; color: var(--muted); margin-top: 8px; }}
    .intro-wrap {{ overflow: hidden; }}
    .intro-map {{
      float: left; width: 33%; margin: 0 1.25rem 0.75rem 0;
    }}
    .intro-map img {{ width: 100%; height: auto; background: #111; display: block; }}
    .intro-map figcaption {{ font-size: 0.78rem; color: var(--muted); margin-top: 6px; }}
    .lead p {{ margin: 0 0 1rem; }}
    .lead p:last-child {{ margin-bottom: 0; }}
    @media (max-width: 640px) {{
      .intro-map {{ float: none; width: 100%; margin: 0 0 1rem; }}
    }}
    .method {{ background: #fff; border: 1px solid var(--line); padding: 1rem 1.1rem; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; font-size: 0.92rem; }}
    th, td {{ padding: 8px 10px; border-bottom: 1px solid var(--line); text-align: left; }}
    th {{ background: #111; color: #fff; font-weight: 600; }}
    td:nth-child(n+2), th:nth-child(n+2) {{ text-align: right; }}
    tr:last-child td {{ border-bottom: none; }}
    .gallery {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px 10px; }}
    .gallery .tile {{ margin: 0; }}
    .gallery .tile img {{ background: #050505; }}
    .gallery .tile figcaption {{ text-align: center; font-size: 0.78rem; margin-top: 4px; }}
    footer strong {{ color: #ddd; }}
    @media print {{
      body {{ background: #fff; }}
      header {{ break-after: avoid; }}
      figure {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <div class="kicker">Anaplian.com · teledetección urbana</div>
      <h1>Islas de calor en la Ciudad de México</h1>
      <p>Abril y mayo de 2026 · Landsat 8 y 9 · temperatura de superficie y vegetación</p>
    </div>
  </header>
  <main>
    <h2>Por qué este estudio</h2>
    <div class="intro-wrap">
      <figure class="intro-map">
        <img src="assets/01_cdmx_transparencia.png" alt="Ciudad de México: temperatura de superficie semitransparente sobre imagen satelital">
        <figcaption>Temperaturas de superficie por encima de 35 °C, en semitransparencia sobre la imagen satelital.</figcaption>
      </figure>
      <div class="lead">
    {INTRO_HTML}
      </div>
    </div>
    <p><em>{LEAD}</em></p>

    <h2>1. La ciudad, con las superficies más calientes a la vista</h2>
    <figure>
      <img src="assets/01_cdmx_transparencia.png" alt="Ciudad de México: temperatura de superficie semitransparente sobre imagen satelital">
      <figcaption>Temperaturas de superficie por encima de 35 °C, en semitransparencia sobre la imagen satelital. El sur boscoso casi no se colorea: permanece más fresco.</figcaption>
    </figure>

    <h2>2. Vegetación y calor, lado a lado</h2>
    <figure>
      <img src="assets/02_cdmx_vegetacion_lado_a_lado.png" alt="NDVI y temperatura de superficie de la Ciudad de México">
      <figcaption>A la izquierda, verdor (NDVI): de beige (escaso) a verde oscuro (denso). A la derecha, temperatura de la misma ventana. Donde hay más vegetación, la superficie suele estar más fresca.</figcaption>
    </figure>

    <h2>3. Máximas y promedios por alcaldía</h2>
    <figure>
      <img src="assets/03_barras_temperatura_maxima.png" alt="Gráfica de barras de temperatura máxima por alcaldía">
      <figcaption>Pico de temperatura de superficie. Estos valores caen sobre techos y pavimento, no sobre el aire.</figcaption>
    </figure>
    <figure>
      <img src="assets/04_barras_temperatura_promedio.png" alt="Gráfica de barras de temperatura promedio por alcaldía">
      <figcaption>Promedio de toda la alcaldía. Venustiano Carranza, Iztacalco, Azcapotzalco e Iztapalapa concentran el calor; Magdalena Contreras y Cuajimalpa, el fresco.</figcaption>
    </figure>

    <h2>Cómo se hizo</h2>
    <p class="method">{PARRAFO}</p>

    <h2>Temperaturas por alcaldía</h2>
    <p>Diferencia = promedio de la alcaldía menos {T_RURAL:.1f} °C de las zonas vegetales del sur-poniente.</p>
    <table>
      <thead>
        <tr>
          <th>Alcaldía</th>
          <th>Máxima (°C)</th>
          <th>Promedio (°C)</th>
          <th>Diferencia vs zona vegetal (°C)</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>

    <h2>Alcaldías: islas de calor con transparencia (corte 38 °C)</h2>
    <p>Mismas escenas Landsat; se colorean solo las superficies por encima de 38 °C, en semitransparencia sobre la imagen satelital. Miniaturas a tamaño reducido, seis por bloque.</p>
    <div class="gallery">
      {gallery_html}
    </div>
  </main>
  <footer>
    <div class="wrap">
      <strong>Anaplian.com</strong> · USGS Landsat 8/9 C2 L2 · NDVI (B4/B5) · LST banda 10 (10,6–11,2 µm) ·
      referencia rural GHSL 2020 · {N_LANDSAT} escenas · abril–mayo 2026 · ~10:30 local
    </div>
  </footer>
</body>
</html>
"""
(OUT / "index.html").write_text(html, encoding="utf-8")

(OUT / "texto_seccion.md").write_text(
    f"""# Islas de calor en la Ciudad de México

*Texto listo para pegar más adelante como sección del sitio. Imágenes en `assets/`.*

**Antetítulo.** Anaplian.com · teledetección urbana

**Título.** Islas de calor en la Ciudad de México

**Bajada.** Abril y mayo de 2026 · Landsat 8 y 9 · temperatura de superficie y vegetación

## Introducción

{INTRO_P1}

{INTRO_P2}

{INTRO_P3}

## Hallazgo en una línea

{LEAD}

## Pie de la primera imagen (`01_cdmx_transparencia.png`)

Temperaturas de superficie por encima de 35 °C, en semitransparencia sobre la imagen satelital. El sur boscoso casi no se colorea: permanece más fresco.

## Pie de la segunda imagen (`02_cdmx_vegetacion_lado_a_lado.png`)

A la izquierda, verdor (NDVI): de beige (escaso) a verde oscuro (denso). A la derecha, temperatura de la misma ventana. Donde hay más vegetación, la superficie suele estar más fresca.

## Metodología (un párrafo)

{PARRAFO}

## Notas para la tabla

Diferencia = promedio de la alcaldía menos {T_RURAL:.1f} °C de las zonas vegetales del sur-poniente (La Magdalena Contreras, Cuajimalpa de Morelos, Tlalpan y Milpa Alta; clases rurales GHSL 2020).

## Galería 38 °C (`assets/galeria_38c/`)

Islas de calor con transparencia y corte a 38 °C, ciudad y 16 alcaldías, miniaturas para unas 6 por página.

## Créditos

Anaplian.com · USGS Landsat 8/9 Collection 2 Level-2 · NDVI bandas 4 y 5 · infrarrojo térmico banda 10 (10,6–11,2 µm) · {N_LANDSAT} imágenes · ~10:30 hora local
""",
    encoding="utf-8",
)

(OUT / "README.md").write_text(
    """# Sección web: islas de calor CDMX

Esta carpeta está lista para copiarse al sitio más adelante.

| Archivo | Uso |
|---|---|
| `index.html` | Página o bloque embebible |
| `texto_seccion.md` | Copy en español, pies de foto y párrafo metodológico |
| `Islas_de_calor_CDMX_2026.pdf` | Versión para LinkedIn |
| `assets/` | Imágenes del reporte, en orden |

No hace falta regenerar mapas: las figuras ya están copiadas aquí.
""",
    encoding="utf-8",
)


class PDF(FPDF):
    def footer(self):
        self.set_y(-10)
        self.set_font("Helvetica", size=8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, f"Anaplian.com   |   {self.page_no()}", align="C")


FONT = Path(r"C:\Windows\Fonts\arial.ttf")
FONTB = Path(r"C:\Windows\Fonts\arialbd.ttf")
pdf = PDF(format="A4", unit="mm")
pdf.set_auto_page_break(auto=False, margin=10)
pdf.set_margins(10, 10, 10)
if FONT.exists():
    pdf.add_font("Body", "", str(FONT))
    pdf.add_font("Body", "B", str(FONTB if FONTB.exists() else FONT))
    face = "Body"
else:
    face = "Helvetica"

page_w = 210 - 20
BOTTOM = 287  # leave footer band


def write_body(text, size=11, bold=False, color=(20, 20, 20), lh=5.6):
    pdf.set_x(pdf.l_margin)
    pdf.set_font(face, "B" if bold else "", size)
    pdf.set_text_color(*color)
    pdf.multi_cell(page_w, lh, text)


def remain():
    return max(12.0, BOTTOM - pdf.get_y())


_fit_n = 0


def fit_image(path, caption=""):
    global _fit_n
    _fit_n += 1
    im = crop_uniform_border(Image.open(path).convert("RGB"))
    tmp = ASSETS / f"_pdf_fit_{_fit_n}.png"
    im.save(tmp)
    iw, ih = im.size
    aspect = ih / float(iw)
    cap = 7 if caption else 0
    avail_w = page_w
    avail_h = remain() - cap
    w = avail_w
    h = w * aspect
    if h > avail_h:
        h = avail_h
        w = h / aspect
    x = pdf.l_margin + (avail_w - w) / 2.0
    y = pdf.get_y()
    pdf.image(str(tmp), x=x, y=y, w=w, h=h)
    pdf.set_y(y + h + 0.6)
    if caption:
        write_body(caption, 8, False, (80, 80, 80), 3.5)


def page_title(text):
    pdf.add_page()
    write_body(text, 12, True, (15, 15, 15), 6)
    pdf.ln(1)


def write_flow(paragraphs, img_bottom, img_right, size=10.5, lh=5.5, para_gap=2.8):
    """Write paragraphs wrapping to the right of a left image, then full width below."""
    pdf.set_font(face, "", size)
    pdf.set_text_color(20, 20, 20)
    beside = True

    def column(y):
        if beside and y + lh < img_bottom:
            return img_right, page_w - (img_right - pdf.l_margin)
        return pdf.l_margin, page_w

    for para in paragraphs:
        words = para.split()
        line = ""
        for word in words:
            y = pdf.get_y()
            if beside and y + lh >= img_bottom:
                beside = False
                if y < img_bottom:
                    pdf.set_y(img_bottom + 1.2)
                    y = pdf.get_y()
            if y + lh > BOTTOM:
                pdf.add_page()
                beside = False
                y = pdf.get_y()
            x, w = column(y)
            test = word if not line else f"{line} {word}"
            if pdf.get_string_width(test) <= w:
                line = test
                continue
            if line:
                pdf.set_xy(x, y)
                pdf.cell(w, lh, line)
                pdf.set_y(y + lh)
            line = word
        if line:
            y = pdf.get_y()
            if beside and y + lh >= img_bottom:
                beside = False
                if y < img_bottom:
                    pdf.set_y(img_bottom + 1.2)
                    y = pdf.get_y()
            if y + lh > BOTTOM:
                pdf.add_page()
                beside = False
                y = pdf.get_y()
            x, w = column(y)
            pdf.set_xy(x, y)
            pdf.cell(w, lh, line)
            pdf.set_y(y + lh)
        pdf.ln(para_gap)


page_title("Islas de calor en la Ciudad de México")
write_body("ANAPLIAN.COM  |  Abril y mayo de 2026  |  Landsat 8 y 9", 9, True, (180, 90, 20), 5)
pdf.ln(1.5)

_fit_n += 1
_intro_im = crop_uniform_border(Image.open(ASSETS / "01_cdmx_transparencia.png").convert("RGB"))
_intro_tmp = ASSETS / f"_pdf_fit_{_fit_n}.png"
_intro_im.save(_intro_tmp)
_aspect = _intro_im.size[1] / float(_intro_im.size[0])
# ~1/3 of the A4 page, left column; text wraps to the right and below.
_img_h = 99.0
_img_w = _img_h / _aspect
_img_x = pdf.l_margin
_img_y = pdf.get_y()
pdf.image(str(_intro_tmp), x=_img_x, y=_img_y, w=_img_w, h=_img_h)
pdf.set_font(face, "", 7.5)
pdf.set_text_color(90, 90, 90)
pdf.set_xy(_img_x, _img_y + _img_h + 0.8)
pdf.multi_cell(_img_w, 3.2, "Temperatura de superficie > 35 °C, semitransparente sobre la imagen satelital.")
_img_right = _img_x + _img_w + 4.5
_img_bottom = pdf.get_y() + 1.0
pdf.set_xy(_img_right, _img_y)

write_flow(
    [INTRO_P1, INTRO_P2, INTRO_P3, LEAD],
    img_bottom=_img_bottom,
    img_right=_img_right,
    size=10.2,
    lh=5.35,
    para_gap=2.6,
)

page_title("La ciudad, con las superficies más calientes a la vista")
fit_image(
    ASSETS / "01_cdmx_transparencia.png",
    "Temperaturas de superficie > 35 °C, semitransparentes sobre la imagen satelital.",
)

page_title("Vegetacion y calor, lado a lado")
fit_image(
    ASSETS / "02_cdmx_vegetacion_lado_a_lado.png",
    "Izquierda: verdor (NDVI). Derecha: temperatura de superficie, sin carreteras vectoriales.",
)

pdf.add_page()
write_body("Como se hizo", 14, True)
pdf.ln(2)
write_body(PARRAFO, 11, False, (20, 20, 20), 6.2)

page_title("Temperatura maxima por alcaldia")
fit_image(ASSETS / "03_barras_temperatura_maxima.png")

page_title("Temperatura promedio por alcaldia")
fit_image(ASSETS / "04_barras_temperatura_promedio.png")

page_title("Temperaturas por alcaldia")
write_body(
    f"Diferencia = promedio menos {T_RURAL:.1f} C de las zonas vegetales del sur-poniente.",
    9, False, (80, 80, 80), 4.2,
)
pdf.ln(2)
n_rows = 1 + len(df)
row_h = remain() / n_rows
col_w = [page_w * 0.40, page_w * 0.20, page_w * 0.20, page_w * 0.20]
headers = ["Alcaldia", "Maxima (C)", "Promedio (C)", "Dif. vegetal (C)"]
pdf.set_x(pdf.l_margin)
pdf.set_font(face, "B", 12)
pdf.set_fill_color(20, 20, 20)
pdf.set_text_color(255, 255, 255)
for i, h in enumerate(headers):
    pdf.cell(col_w[i], row_h, h, fill=True, align="C" if i else "L")
pdf.ln()
pdf.set_text_color(20, 20, 20)
pdf.set_font(face, "", 12)
fill = False
for r in df.itertuples():
    pdf.set_x(pdf.l_margin)
    pdf.set_fill_color(247, 244, 239) if fill else pdf.set_fill_color(255, 255, 255)
    pdf.cell(col_w[0], row_h, r.alcaldia, fill=True)
    pdf.cell(col_w[1], row_h, f"{r.lst_peak_C:.1f}", fill=True, align="R")
    pdf.cell(col_w[2], row_h, f"{r.lst_mean_C:.1f}", fill=True, align="R")
    pdf.cell(col_w[3], row_h, f"{r.suhi_C:+.1f}", fill=True, align="R")
    pdf.ln()
    fill = not fill

PER_PAGE, COLS = 6, 2
gap = 2.4
for page_i in range(0, len(thumbs), PER_PAGE):
    page_title("Islas de calor con transparencia, corte a 38 C" + (" (cont.)" if page_i else ""))
    if page_i == 0:
        write_body(
            "Ciudad y 16 alcaldias. Solo se colorean superficies por encima de 38 C.",
            8, False, (80, 80, 80), 4,
        )
    chunk = thumbs[page_i:page_i + PER_PAGE]
    n_rows_g = max(1, (len(chunk) + COLS - 1) // COLS)
    cell_w = (page_w - (COLS - 1) * gap) / COLS
    cell_h = remain() / n_rows_g
    cap_h = 5.2
    start_y = pdf.get_y()
    for j, (name, path) in enumerate(chunk):
        col = j % COLS
        row = j // COLS
        x = pdf.l_margin + col * (cell_w + gap)
        y = start_y + row * cell_h
        im = Image.open(path)
        iw, ih = im.size
        box_h = cell_h - cap_h
        scale = min(cell_w / iw, box_h / ih)
        w = iw * scale
        h = ih * scale
        ix = x + (cell_w - w) / 2.0
        iy = y + (box_h - h) / 2.0
        pdf.image(str(path), x=ix, y=iy, w=w, h=h)
        pdf.set_xy(x, y + box_h + 0.2)
        pdf.set_font(face, "", 8)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(cell_w, cap_h - 0.4, name, align="C")

pdf_path = OUT / "Islas_de_calor_CDMX_2026.pdf"
pdf.output(str(pdf_path))
for leftover in ASSETS.glob("_pdf_fit_*.png"):
    leftover.unlink(missing_ok=True)
print("HTML", OUT / "index.html")
print("PDF", pdf_path)
print("thumbs", len(thumbs))
