"""Paris April–May 2026 heat-island analysis: city, 20 arrondissements, NDVI, French report.

Amplio Landsat 8/9 composite, GHSL rural belt 20 km, overlay LST > 30/35 °C.

    python reports/generate_paris_report.py
"""
from __future__ import annotations

import csv
import json
import os
import shutil
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import ee
import geemap
import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import mapping
from fpdf import FPDF
from matplotlib.cm import ScalarMappable
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reports"))
import plot_cdmx_heat_over_streets as heat  # noqa: E402
from plot_cdmx_heat_methods import collection_for, rural_mask, year_window  # noqa: E402


def add_scale_north(ax, bounds, km):
    width_km = heat.span_km(bounds)[0]
    frac = km / width_km if width_km else 0.2
    x0, x1 = 0.72, 0.72 + min(frac, 0.22)
    y = 0.07
    ax.plot([x0, x1], [y, y], transform=ax.transAxes, color="white", lw=2.4, solid_capstyle="butt")
    ax.plot([x0, x0], [y - 0.008, y + 0.008], transform=ax.transAxes, color="white", lw=1.4)
    ax.plot([x1, x1], [y - 0.008, y + 0.008], transform=ax.transAxes, color="white", lw=1.4)
    ax.text((x0 + x1) / 2, y + 0.028, f"{km} km", transform=ax.transAxes, ha="center", color="white", fontsize=8)
    ax.text(0.93, 0.205, "N", transform=ax.transAxes, ha="center", va="bottom", fontsize=8, fontweight="bold", color="white")
    ax.annotate(
        "",
        xy=(0.93, 0.19),
        xytext=(0.93, 0.10),
        xycoords="axes fraction",
        arrowprops=dict(arrowstyle="-|>", color="white", lw=1.1),
    )


heat.add_scale_north = add_scale_north

YEAR = 2026
LST_CUT = 35.0
LST_SCALE_MAX = 45.0
RURAL_BUFFER_M = 20_000
CITY_PAD = 0.008
ARR_PAD = 0.003
BND = ROOT / "data" / "boundaries" / "paris" / "paris.geojson"
ARR = ROOT / "data" / "boundaries" / "paris" / "paris_arrondissements.geojson"
OUT = ROOT / "reports" / "paris_heat_islands"
FIG = OUT / "figures"
STREETS = OUT / "heat_over_streets"
SITE = ROOT / "reports" / "sitio_ilots_chaleur_paris"
ASSETS = SITE / "assets"
VEG_PALETTE = ["#f3edd8", "#dce8b4", "#8fbf7a", "#3d8c54", "#14532d"]
TEMP_PALETTE = ["#2b1155", "#6a1c80", "#c43c4a", "#f18d2a", "#fde725"]


def union_geom(gdf):
    geom = gdf.geometry
    return geom.union_all() if hasattr(geom, "union_all") else geom.unary_union


def fnum(value, default=None):
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def prep_ndvi(image):
    img = heat.cloud_mask(image)
    nir = img.select("SR_B5").multiply(0.0000275).add(-0.2)
    red = img.select("SR_B4").multiply(0.0000275).add(-0.2)
    ndvi = nir.subtract(red).divide(nir.add(red)).rename("NDVI")
    valid = ndvi.gt(-0.2).And(ndvi.lt(1.0))
    return ndvi.updateMask(valid)


def ndvi_collection(year, bounds_geom):
    start, end, _ = year_window(year)

    def load(cid):
        return (
            ee.ImageCollection(cid)
            .filterBounds(bounds_geom)
            .filterDate(start, end)
            .map(prep_ndvi)
        )

    return load("LANDSAT/LC08/C02/T1_L2").merge(load("LANDSAT/LC09/C02/T1_L2"))


def reduce_mean(image, geom, scale=30):
    info = image.reduceRegion(
        ee.Reducer.mean(), geom, scale, maxPixels=1e8, bestEffort=True
    ).getInfo()
    return fnum(next(iter(info.values()), None))


def fc_props(fc):
    return [f["properties"] for f in fc.getInfo()["features"]]


def two_panel(veg, temp, bounds, title, veg_note, temp_note, outfile, ndvi_lim, lst_lim):
    veg_cmap = mcolors.LinearSegmentedColormap.from_list("veg", VEG_PALETTE)
    temp_cmap = mcolors.LinearSegmentedColormap.from_list("tmp", TEMP_PALETTE)
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 7.1), facecolor="white")
    km = heat.scale_km_length(bounds)
    for ax, im in zip(axes, (veg, temp)):
        ax.imshow(im)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#111")
            sp.set_linewidth(0.6)
        heat.add_scale_north(ax, bounds, km)
    for ax, cmap, vmin, vmax, label, lo, hi in (
        (axes[0], veg_cmap, ndvi_lim[0], ndvi_lim[1], "Végétation (NDVI)", "faible", "dense"),
        (axes[1], temp_cmap, lst_lim[0], lst_lim[1], "Température (°C)", f"{lst_lim[0]:.0f}", f"{lst_lim[1]:.0f}"),
    ):
        sm = ScalarMappable(norm=mcolors.Normalize(vmin, vmax), cmap=cmap)
        sm.set_array([])
        cax = ax.inset_axes([0.12, -0.16, 0.76, 0.045])
        cbar = fig.colorbar(sm, cax=cax, orientation="horizontal")
        cbar.set_ticks([vmin, vmax])
        cbar.set_ticklabels([lo, hi])
        cbar.ax.tick_params(labelsize=8)
        cbar.set_label(label, fontsize=9, fontweight="bold", labelpad=2)
    fig.suptitle(title, fontsize=13, fontweight="bold", y=0.98)
    fig.text(0.25, 0.015, veg_note, ha="center", va="bottom", fontsize=7, color="#333")
    fig.text(0.75, 0.015, temp_note, ha="center", va="bottom", fontsize=7, color="#333")
    fig.text(0.985, 0.025, "Anaplian.com", ha="right", va="bottom", fontsize=13, fontweight="bold", color="#4a4a4a", alpha=0.82)
    fig.subplots_adjust(left=0.03, right=0.97, top=0.90, bottom=0.22, wspace=0.04)
    fig.savefig(outfile, dpi=160)
    plt.close(fig)
    print("saved", outfile.name, flush=True)


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


def bar_chart(values, names, title, xlabel, outfile, color):
    order = np.argsort(values)[::-1]
    names = [names[i] for i in order]
    vals = [values[i] for i in order]
    fig, ax = plt.subplots(figsize=(9.4, 11.2))
    ax.barh(range(len(names))[::-1], vals, color=color, height=0.72)
    ax.set_yticks(range(len(names))[::-1], names, fontsize=9)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_title(title, fontsize=13, fontweight="bold", loc="left", pad=10)
    for i, v in zip(range(len(names))[::-1], vals):
        ax.text(v + 0.02 * (max(vals) - min(vals) + 0.5), i, f"{v:.2f}", va="center", fontsize=8, color="#333")
    span = max(vals) - min(vals)
    ax.set_xlim(min(vals) - 0.08 * max(span, 1), max(vals) + 0.18 * max(span, 1))
    fig.tight_layout(rect=(0.02, 0.03, 0.98, 0.99))
    fig.text(0.99, 0.01, "Anaplian.com", ha="right", va="bottom", fontsize=10, fontweight="bold", color="#8d8d8d", alpha=0.85)
    fig.savefig(outfile, dpi=160, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    crop_uniform_border(Image.open(outfile)).save(outfile)
    print("saved", outfile.name, flush=True)


def overlay_caption(n_scenes, cut, period):
    return (
        f"{heat.LST_SOURCE}\n{period}  |  {heat.LST_HOURS}\n"
        f"Composite large : moyenne par pixel de {n_scenes} scènes\n"
        f"Masque nuages/remplissage/plage valide par pixel\n"
        f"Overlay : température de surface > {cut:.0f} °C"
    )


def write_site(meta, profiles, hero, veg, bars):
    SITE.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    n = int(meta["n_landsat"])
    t_rural = float(meta["t_rural"])
    t_city = float(meta["t_city"])
    suhi = float(meta["suhi_C"])
    peak = float(meta["lst_p98_C"])
    cut = float(meta["lst_cut"])
    ndvi_city = float(meta["ndvi_mean"])
    hottest = meta["hottest"]
    coolest = meta["coolest"]
    greenest = meta["greenest"]
    local_h = meta.get("lst_hours_local", "12 h 30")
    utc_h = meta.get("lst_hours_utc", "10 h 30")

    shutil.copy2(hero, ASSETS / "01_paris_transparence.png")
    shutil.copy2(veg, ASSETS / "02_vegetation_temperature.png")
    shutil.copy2(bars["peak"], ASSETS / "03_barres_temperature_max.png")
    shutil.copy2(bars["mean"], ASSETS / "04_barres_temperature_moyenne.png")
    shutil.copy2(bars["ndvi"], ASSETS / "05_barres_ndvi.png")

    gallery = ASSETS / "galerie_arrondissements"
    if gallery.exists():
        shutil.rmtree(gallery)
    gallery.mkdir()
    thumbs = [("Paris", hero)]
    for p in profiles:
        src = STREETS / f"{p['slug']}_heat_over_streets_{int(cut)}c.png"
        if src.exists():
            thumbs.append((p["arrondissement"], src))
    tile_html = []
    for i, (name, path) in enumerate(thumbs, 1):
        im = crop_uniform_border(Image.open(path).convert("RGB"), tol=14, pad=4)
        im.thumbnail((520, 620), Image.Resampling.LANCZOS)
        outp = gallery / f"{i:02d}_{path.stem}.jpg"
        im.save(outp, quality=85, optimize=True)
        tile_html.append(
            f'<figure class="tile"><img src="assets/galerie_arrondissements/{outp.name}" alt="{name}">'
            f"<figcaption>{name}</figcaption></figure>"
        )

    intro1 = (
        "La hausse de la température moyenne de la planète aggrave la vulnérabilité aux "
        "chaleurs excessives. Il ne s'agit pas seulement d'un degré de plus dans la moyenne "
        "globale : cette hausse pousse davantage de journées au-delà de seuils dangereux pour "
        "la santé, le travail en extérieur et les réseaux d'eau et d'énergie. En ville, le "
        "risque se concentre. L'asphalte, le béton, les toitures sombres et le métal absorbent "
        "une grande part du rayonnement solaire et le restituent en chaleur. Rues étroites et "
        "immeubles forment des canyons qui piègent l'air chaud. Le résultat : des îlots de "
        "chaleur — parkings, hangars, avenues et toitures où la surface atteint des températures "
        "que le corps ne tolère pas en exposition prolongée."
    )
    intro2 = (
        f"Avec Landsat 8 et Landsat 9, nous cartographions les surfaces les plus chaudes de "
        f"Paris et de ses 20 arrondissements. La carte est la moyenne par pixel de {n} scènes "
        f"d'avril et mai {YEAR}, acquises vers {local_h}, heure locale. Sur chaque pixel, nuages, "
        "ombres et valeurs invalides sont masqués avant de moyenner ; on ne jette pas la scène "
        "entière. Le capteur thermique — bande 10, entre 10,6 et 11,2 micromètres — estime la "
        "chaleur du sol, des toits et du bitume, pas celle de l'air à l'ombre. Seules les "
        f"surfaces au-dessus de {cut:.0f} °C sont coloriées. En parallèle, le NDVI montre où la "
        "végétation est dense. La température de la commune se compare à la moyenne des zones "
        f"rurales dans un rayon de 20 km (ceinture verte d'Île-de-France). Le 98e centile du "
        f"composite atteint {peak:.1f} °C ; l'écart urbain–rural (SUHI) est de {suhi:+.1f} °C."
    )
    intro3 = (
        "Ces pics ne sont pas un épisode isolé : avec davantage de vagues de chaleur et de "
        "surfaces imperméables, ils tendent à s'aggraver. Ils servent à repérer des lieux "
        "d'intervention. L'urbanisme tactique permet de tester ombres temporaires, peinture à "
        "fort albédo dans les cours d'école, et trottoirs plus perméables. La végétation reste "
        "le levier le plus durable : un arbre intercepte le soleil et rafraîchit l'air par "
        "transpiration. Bois de Boulogne, bois de Vincennes, coulées de la Seine et toitures "
        "végétalisées réduisent la charge thermique. La donnée satellitaire n'indique pas le "
        "projet local ; elle montre où agir d'abord."
    )
    lead = (
        f"À Paris, au printemps {YEAR}, la température moyenne de surface de la commune est de "
        f"{t_city:.1f} °C, contre {t_rural:.1f} °C dans la ceinture rurale ({suhi:+.1f} °C). "
        f"Le NDVI moyen est de {ndvi_city:.2f}. {hottest} est l'arrondissement le plus chaud "
        f"en moyenne ; {coolest} le plus frais ; {greenest} le plus végétalisé."
    )
    method = (
        f"Les cartes sont un composite large : la moyenne par pixel des {n} scènes Landsat 8 "
        f"et Landsat 9 (Collection 2, niveau 2) acquises entre le 1er avril et le 31 mai {YEAR}. "
        "On ne jette pas une scène entière pour cause de nuages : sur chaque pixel, le remplissage, "
        "les nuages, les ombres et les températures hors de la plage valide (0 à 80 °C) sont "
        "masqués, puis les observations utiles sont moyennées. Les satellites survolent Paris "
        f"vers {local_h}, heure locale (près de {utc_h} UTC). Ce qui est peint n'est pas "
        "l'air à l'ombre, mais la température de surface — toits, asphalte, sol nu et végétation — "
        "avec la bande 10 de l'infrarouge thermique (10,6 à 11,2 micromètres ; "
        "LST = 0,00341802 × DN + 149 − 273,15). En jaune à rouge n'apparaissent que les surfaces "
        f"au-dessus de {cut:.0f} °C. Le verdure est mesuré par le NDVI (rouge et proche infrarouge). "
        f"L'écart urbain–rural soustrait {t_rural:.1f} °C, moyenne des classes rurales du GHSL 2020 "
        "(SMOD 11, 12 et 13, hors eau) dans un rayon de 20 km autour de la commune. Les 20 "
        "arrondissements municipaux viennent des données ouvertes de la Ville de Paris."
    )

    rows_md = "\n".join(
        f"| {p['arrondissement']} | {p['lst_peak_C']:.1f} | {p['lst_mean_C']:.1f} | "
        f"{p['suhi_C']:+.1f} | {p['ndvi_mean']:.2f} |"
        for p in profiles
    )
    (SITE / "texte_section.md").write_text(
        f"""# Îlots de chaleur à Paris

**Surtitre.** Anaplian.com · télédétection urbaine

**Titre.** Îlots de chaleur à Paris

**Chapô.** Avril et mai {YEAR} · Landsat 8 et 9 · 20 arrondissements · température de surface et NDVI

## Introduction

{intro1}

{intro2}

{intro3}

## En une ligne

{lead}

## Méthodologie

{method}

## Arrondissements

| Arrondissement | Max (°C) | Moyenne (°C) | SUHI (°C) | NDVI |
| --- | ---: | ---: | ---: | ---: |
{rows_md}
""",
        encoding="utf-8",
    )

    table_html = "\n".join(
        f"<tr><td>{p['arrondissement']}</td><td>{p['lst_peak_C']:.1f}</td>"
        f"<td>{p['lst_mean_C']:.1f}</td><td>{p['suhi_C']:+.1f}</td>"
        f"<td>{p['ndvi_mean']:.2f}</td></tr>"
        for p in profiles
    )
    html = f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Îlots de chaleur à Paris — avril et mai {YEAR}</title>
  <style>
    :root {{ --ink:#1a1a1a; --muted:#555; --line:#e6e1d8; }}
    body {{ margin:0; color:var(--ink); background:#f7f4ef; font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif; line-height:1.55; }}
    header {{ background:#111; color:#fff; padding:36px 20px 28px; }}
    header .wrap, main, footer .wrap {{ max-width:960px; margin:0 auto; }}
    h1 {{ font-size:1.85rem; margin:0 0 8px; }}
    .kicker {{ color:#f0c27a; font-size:0.82rem; letter-spacing:0.12em; text-transform:uppercase; }}
    main {{ padding:28px 20px 64px; }}
    figure {{ margin:0 0 1.4rem; }}
    figure img {{ width:100%; height:auto; background:#111; display:block; }}
    figcaption {{ font-size:0.88rem; color:var(--muted); margin-top:8px; }}
    .method {{ background:#fff; border:1px solid var(--line); padding:1rem 1.1rem; }}
    table {{ width:100%; border-collapse:collapse; background:#fff; }}
    th, td {{ border-bottom:1px solid var(--line); padding:8px 10px; text-align:right; }}
    th:first-child, td:first-child {{ text-align:left; }}
    .gallery {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:12px; }}
    .tile figcaption {{ font-size:0.8rem; }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <div class="kicker">Anaplian.com · télédétection urbaine</div>
      <h1>Îlots de chaleur à Paris</h1>
      <p>Avril et mai {YEAR} · Landsat 8 et 9 · 20 arrondissements · température de surface et NDVI</p>
    </div>
  </header>
  <main>
    <h2>Pourquoi cette étude</h2>
    <p>{intro1}</p>
    <p>{intro2}</p>
    <p>{intro3}</p>
    <p><em>{lead}</em></p>
    <h2>La commune, surfaces les plus chaudes</h2>
    <figure>
      <img src="assets/01_paris_transparence.png" alt="Paris, température de surface">
      <figcaption>Températures de surface au-dessus de {cut:.0f} °C, en semi-transparence sur l'image satellite.</figcaption>
    </figure>
    <h2>Végétation et chaleur, côte à côte</h2>
    <figure>
      <img src="assets/02_vegetation_temperature.png" alt="NDVI et température de surface à Paris">
      <figcaption>À gauche, verdure (NDVI). À droite, température de surface de la même fenêtre.</figcaption>
    </figure>
    <h2>Les 20 arrondissements</h2>
    <figure><img src="assets/03_barres_temperature_max.png" alt="Température maximale par arrondissement"></figure>
    <figure><img src="assets/04_barres_temperature_moyenne.png" alt="Température moyenne par arrondissement"></figure>
    <figure><img src="assets/05_barres_ndvi.png" alt="NDVI moyen par arrondissement"></figure>
    <table>
      <thead><tr><th>Arrondissement</th><th>Max °C</th><th>Moyenne °C</th><th>SUHI °C</th><th>NDVI</th></tr></thead>
      <tbody>{table_html}</tbody>
    </table>
    <h2>Galerie</h2>
    <div class="gallery">{''.join(tile_html)}</div>
    <h2>Comment c'est fait</h2>
    <p class="method">{method}</p>
  </main>
  <footer>
    <div class="wrap">
      <strong>Anaplian.com</strong> · USGS Landsat 8/9 C2 L2 · NDVI (B4/B5) · LST bande 10 ·
      référence rurale GHSL 2020 · {n} scènes · avril–mai {YEAR}
    </div>
  </footer>
</body>
</html>
"""
    (SITE / "index.html").write_text(html, encoding="utf-8")

    class PDF(FPDF):
        def footer(self):
            self.set_y(-10)
            self.set_font("Helvetica", size=8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 6, f"Anaplian.com   |   {self.page_no()}", align="C")

    font = Path(r"C:\Windows\Fonts\arial.ttf")
    fontb = Path(r"C:\Windows\Fonts\arialbd.ttf")
    pdf = PDF(format="A4", unit="mm")
    pdf.set_auto_page_break(auto=False, margin=10)
    pdf.set_margins(10, 10, 10)
    if font.exists():
        pdf.add_font("Body", "", str(font))
        pdf.add_font("Body", "B", str(fontb if fontb.exists() else font))
        face = "Body"
    else:
        face = "Helvetica"
    page_w = 210 - 20
    bottom = 287
    fit_n = 0

    def write_body(text, size=11, bold=False, color=(20, 20, 20), lh=5.6):
        pdf.set_x(pdf.l_margin)
        pdf.set_font(face, "B" if bold else "", size)
        pdf.set_text_color(*color)
        pdf.multi_cell(page_w, lh, text)

    def remain():
        return max(12.0, bottom - pdf.get_y())

    def fit_image(path, caption=""):
        nonlocal fit_n
        fit_n += 1
        im = crop_uniform_border(Image.open(path).convert("RGB"))
        tmp = ASSETS / f"_pdf_fit_{fit_n}.png"
        im.save(tmp)
        iw, ih = im.size
        aspect = ih / float(iw)
        cap = 7 if caption else 0
        avail_h = remain() - cap
        w = page_w
        h = w * aspect
        if h > avail_h:
            h = avail_h
            w = h / aspect
        x = pdf.l_margin + (page_w - w) / 2.0
        y = pdf.get_y()
        pdf.image(str(tmp), x=x, y=y, w=w, h=h)
        pdf.set_y(y + h + 0.6)
        if caption:
            write_body(caption, 8, False, (80, 80, 80), 3.5)

    pdf.add_page()
    write_body("Îlots de chaleur à Paris", 13, True, (15, 15, 15), 6)
    write_body(
        f"ANAPLIAN.COM  |  Avril et mai {YEAR}  |  Landsat 8 et 9  |  LST > {cut:.0f} C",
        8.5, True, (180, 90, 20), 4.5,
    )
    pdf.ln(1.0)
    fit_image(ASSETS / "01_paris_transparence.png")

    pdf.add_page()
    write_body("Pourquoi cette étude", 12, True, (15, 15, 15), 6)
    pdf.ln(1)
    for para in (intro1, intro2, intro3, lead):
        write_body(para, 10.5, False, (20, 20, 20), 5.5)
        pdf.ln(2.4)

    pdf.add_page()
    write_body("Végétation et chaleur, côte à côte", 12, True, (15, 15, 15), 6)
    pdf.ln(1)
    fit_image(ASSETS / "02_vegetation_temperature.png", "Gauche : verdure (NDVI). Droite : température de surface.")

    pdf.add_page()
    write_body("Comment c'est fait", 14, True)
    pdf.ln(2)
    write_body(method, 11, False, (20, 20, 20), 6.2)

    pdf.add_page()
    write_body("Température maximale par arrondissement", 12, True, (15, 15, 15), 6)
    pdf.ln(1)
    fit_image(ASSETS / "03_barres_temperature_max.png")

    pdf.add_page()
    write_body("Température moyenne par arrondissement", 12, True, (15, 15, 15), 6)
    pdf.ln(1)
    fit_image(ASSETS / "04_barres_temperature_moyenne.png")

    pdf.add_page()
    write_body("NDVI moyen par arrondissement", 12, True, (15, 15, 15), 6)
    pdf.ln(1)
    fit_image(ASSETS / "05_barres_ndvi.png")

    pdf.add_page()
    write_body("Températures et NDVI par arrondissement", 12, True, (15, 15, 15), 6)
    pdf.ln(2)
    col_w = [52, 32, 36, 32, 28]
    headers = ["Arrondissement", "Max", "Moyenne", "SUHI", "NDVI"]
    pdf.set_font(face, "B", 8)
    pdf.set_fill_color(20, 20, 20)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 7, h, fill=True, align="C" if i else "L")
    pdf.ln()
    fill = False
    for p in profiles:
        pdf.set_font(face, "", 8)
        pdf.set_text_color(20, 20, 20)
        pdf.set_fill_color(247, 244, 239) if fill else pdf.set_fill_color(255, 255, 255)
        vals = [
            p["arrondissement"],
            f"{p['lst_peak_C']:.1f}",
            f"{p['lst_mean_C']:.1f}",
            f"{p['suhi_C']:+.1f}",
            f"{p['ndvi_mean']:.2f}",
        ]
        for i, v in enumerate(vals):
            pdf.cell(col_w[i], 6.2, v, fill=True, align="C" if i else "L")
        pdf.ln()
        fill = not fill

    pdf.add_page()
    write_body("Galerie des arrondissements", 12, True, (15, 15, 15), 6)
    pdf.ln(1)
    tile_w = (page_w - 8) / 3
    x0 = pdf.l_margin
    y = pdf.get_y()
    col = 0
    for i, (name, path) in enumerate(thumbs):
        im = crop_uniform_border(Image.open(path).convert("RGB"), tol=14, pad=4)
        tmp = ASSETS / f"_pdf_gal_{i}.jpg"
        im.thumbnail((640, 760), Image.Resampling.LANCZOS)
        im.save(tmp, quality=80)
        iw, ih = im.size
        h = tile_w * (ih / float(iw))
        if y + h + 8 > bottom:
            pdf.add_page()
            y = 12
            col = 0
        x = x0 + col * (tile_w + 4)
        pdf.image(str(tmp), x=x, y=y, w=tile_w)
        pdf.set_xy(x, y + h + 0.4)
        pdf.set_font(face, "", 7)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(tile_w, 4, name)
        col += 1
        if col == 3:
            col = 0
            y += h + 8

    pdf_path = SITE / f"Ilots_de_chaleur_Paris_{YEAR}.pdf"
    pdf.output(str(pdf_path))
    for leftover in ASSETS.glob("_pdf_fit_*.png"):
        leftover.unlink(missing_ok=True)
    for leftover in ASSETS.glob("_pdf_gal_*.jpg"):
        leftover.unlink(missing_ok=True)
    print("PDF", pdf_path, flush=True)
    print("HTML", SITE / "index.html", flush=True)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    STREETS.mkdir(parents=True, exist_ok=True)
    city_gdf = gpd.read_file(BND).to_crs("EPSG:4326")
    arr_gdf = gpd.read_file(ARR).to_crs("EPSG:4326")
    city_geom = union_geom(city_gdf)
    city_fc = geemap.geopandas_to_ee(city_gdf)
    arr_fc = geemap.geopandas_to_ee(arr_gdf[["c_ar", "arrondissement", "slug", "geometry"]])
    aoi = city_fc.geometry()
    west, south, east, north = city_gdf.total_bounds
    city_bounds = (west - CITY_PAD, south - CITY_PAD, east + CITY_PAD, north + CITY_PAD)
    city_region = ee.Geometry.Rectangle(list(city_bounds), proj="EPSG:4326", geodesic=False)
    rural_aoi = aoi.buffer(RURAL_BUFFER_M)

    start, end, period_en = year_window(YEAR)
    period = f"Avr–mai {YEAR}"
    heat.START, heat.END, heat.PERIOD = start, end, period
    hours = heat.lst_overpass_hours(
        city_region, start, end, "Europe/Paris", lang="fr",
        fallback={"label": "~12 h 30 locale (10 h 30 UTC)", "local": "12 h 30", "utc": "10 h 30", "tz_name": "Europe/Paris"},
    )
    heat.LST_HOURS = hours["label"]
    heat.CITY_PAD = CITY_PAD
    print(f"Paris composite {period_en}  survol {hours['label']}", flush=True)

    col = collection_for(YEAR, city_region, None)
    n_scenes = int(col.size().getInfo())
    print("scènes", n_scenes, flush=True)
    lst = col.mean()
    lst_city = lst.clip(aoi)
    ndvi = ndvi_collection(YEAR, city_region).mean()
    ndvi_city = ndvi.clip(aoi)
    rural = rural_mask(rural_aoi)
    t_city = reduce_mean(lst_city, aoi, 30)
    t_rural = reduce_mean(lst.updateMask(rural).clip(rural_aoi), rural_aoi, 100)
    ndvi_mean = reduce_mean(ndvi_city, aoi, 30)
    peak_info = lst_city.reduceRegion(
        ee.Reducer.minMax().combine(ee.Reducer.percentile([98]), sharedInputs=True),
        aoi, 30, maxPixels=1e8, bestEffort=True,
    ).getInfo()
    lst_max_img = col.max().clip(aoi)
    scene_peak = fnum(lst_max_img.reduceRegion(ee.Reducer.max(), aoi, 30, maxPixels=1e8, bestEffort=True).getInfo().get("ST_C"))
    p98 = fnum(peak_info.get("ST_C_p98"), t_city)
    comp_max = fnum(peak_info.get("ST_C_max"), p98)
    suhi = None if t_city is None or t_rural is None else t_city - t_rural
    print(
        f"T_city {t_city:.2f}  T_rural {t_rural:.2f}  SUHI {suhi:+.2f}  "
        f"p98 {p98:.1f}  composite_max {comp_max:.1f}  scene_max {scene_peak:.1f}  NDVI {ndvi_mean:.3f}",
        flush=True,
    )

    cut = LST_CUT
    if p98 is not None and p98 < 31:
        cut = 25.0
    elif p98 is not None and p98 < cut + 1:
        cut = 30.0
    if cut != LST_CUT:
        print(f"p98 {p98:.1f} °C, seuil porté à {cut:.0f} °C", flush=True)
    heat.THRESHOLD = cut
    scale_max = max(cut + 8.0, min(LST_SCALE_MAX, (p98 or cut + 8) + 2))
    vis = {"min": cut, "max": scale_max, "palette": heat.HEAT_PALETTE}
    hot = lst.updateMask(lst.gt(cut))
    caption = overlay_caption(n_scenes, cut, period)
    footer = f"{n_scenes} scènes   ·   seuil {cut:.0f} °C   ·   p98 {p98:.1f} °C"

    hero = STREETS / f"paris_heat_over_streets_{int(cut)}c.png"
    print("carte ville", flush=True)
    heat.make_map(
        city_geom, city_bounds, heat.zoom_for(city_bounds), hot, vis,
        "Îlots de chaleur à Paris",
        hero, scale_max, p98 or scale_max, outline_w=3,
        overlay_caption=caption, cbar_label="Température de surface (°C)", footer=footer,
    )

    print("stats arrondissements", flush=True)
    lst_red = ee.Reducer.mean().combine(ee.Reducer.minMax(), sharedInputs=True).combine(
        ee.Reducer.percentile([98]), sharedInputs=True
    )
    lst_rows = {int(p["c_ar"]): p for p in fc_props(lst_city.reduceRegions(arr_fc, lst_red, 30))}
    ndvi_rows = {int(p["c_ar"]): p for p in fc_props(ndvi_city.reduceRegions(arr_fc, ee.Reducer.mean(), 30))}
    peak_rows = {int(p["c_ar"]): p for p in fc_props(lst_max_img.reduceRegions(arr_fc, ee.Reducer.max(), 30))}

    ndvi_stats = ndvi_city.reduceRegion(
        ee.Reducer.percentile([5, 95]), aoi, 30, maxPixels=1e8, bestEffort=True
    ).getInfo()
    ndvi_lo = fnum(ndvi_stats.get("NDVI_p5"), 0.05)
    ndvi_hi = fnum(ndvi_stats.get("NDVI_p95"), 0.70)
    lst_lo = max(10.0, (t_rural or 18) - 4)
    lst_hi = max(lst_lo + 8, min(48.0, (p98 or 40) + 2))
    veg_note = f"USGS Landsat 8/9 C2 L2  ·  NDVI = (PIR − rouge) / (PIR + rouge)  ·  {period}"
    temp_note = f"USGS Landsat 8/9 C2 L2  ·  {heat.LST_FORMULA}  ·  {heat.LST_HOURS}"

    print("NDVI + LST ville", flush=True)
    region = ee.Geometry.Rectangle(list(city_bounds), proj="EPSG:4326", geodesic=False)
    veg_im = heat.fetch_gee_rgb(ndvi_city, {"min": ndvi_lo, "max": ndvi_hi, "palette": VEG_PALETTE}, region, 1100, 900)
    tmp_im = heat.fetch_gee_rgb(lst_city, {"min": lst_lo, "max": lst_hi, "palette": TEMP_PALETTE}, region, 1100, 900)
    veg_path = FIG / "paris_vegetation_temperature.png"
    two_panel(veg_im, tmp_im, city_bounds, "Paris — végétation et température de surface", veg_note, temp_note, veg_path, (ndvi_lo, ndvi_hi), (lst_lo, lst_hi))

    profiles = []
    for _, row in arr_gdf.sort_values("c_ar").iterrows():
        num = int(row["c_ar"])
        name = row["arrondissement"]
        slug = row["slug"]
        geom = row.geometry
        lp = lst_rows.get(num, {})
        np_ = ndvi_rows.get(num, {})
        pp = peak_rows.get(num, {})
        mean_c = fnum(lp.get("ST_C_mean") or lp.get("mean") or lp.get("ST_C"))
        p98_c = fnum(lp.get("ST_C_p98"))
        max_c = fnum(pp.get("ST_C") or pp.get("max") or lp.get("ST_C_max"))
        ndvi_c = fnum(np_.get("NDVI") or np_.get("mean") or np_.get("NDVI_mean"))
        suhi_c = None if mean_c is None or t_rural is None else mean_c - t_rural
        print(
            f"  {name}: mean {mean_c:.2f}  peak {max_c:.1f}  NDVI {ndvi_c:.3f}  SUHI {suhi_c:+.2f}",
            flush=True,
        )
        w, s, e, n = geom.bounds
        bounds = (w - ARR_PAD, s - ARR_PAD, e + ARR_PAD, n + ARR_PAD)
        heat.make_map(
            geom, bounds, heat.zoom_for(bounds), hot, vis,
            f"Îlots de chaleur — {name}",
            STREETS / f"{slug}_heat_over_streets_{int(cut)}c.png",
            scale_max, p98 or scale_max, outline_w=2,
            overlay_caption=caption, cbar_label="Température de surface (°C)", footer=footer,
        )
        ee_geom = ee.Geometry(mapping(geom))
        arr_region = ee.Geometry.Rectangle(list(bounds), proj="EPSG:4326", geodesic=False)
        veg_a = heat.fetch_gee_rgb(ndvi.clip(ee_geom), {"min": ndvi_lo, "max": ndvi_hi, "palette": VEG_PALETTE}, arr_region, 900, 800)
        tmp_a = heat.fetch_gee_rgb(lst.clip(ee_geom), {"min": lst_lo, "max": lst_hi, "palette": TEMP_PALETTE}, arr_region, 900, 800)
        two_panel(
            veg_a, tmp_a, bounds,
            f"{name} — végétation et température de surface",
            veg_note, temp_note,
            FIG / f"{slug}_vegetation_temperature.png",
            (ndvi_lo, ndvi_hi), (lst_lo, lst_hi),
        )
        profiles.append({
            "c_ar": num,
            "arrondissement": name,
            "slug": slug,
            "lst_mean_C": round(mean_c, 2) if mean_c is not None else None,
            "lst_peak_C": round(max_c, 2) if max_c is not None else None,
            "lst_p98_C": round(p98_c, 2) if p98_c is not None else None,
            "ndvi_mean": round(ndvi_c, 3) if ndvi_c is not None else None,
            "suhi_C": round(suhi_c, 2) if suhi_c is not None else None,
        })

    profiles.sort(key=lambda p: (-(p["lst_mean_C"] or 0), p["c_ar"]))
    names = [p["arrondissement"] for p in profiles]
    bar_chart([p["lst_peak_C"] for p in profiles], names, "Température maximale de surface par arrondissement", "Maximum (°C) — Landsat 8/9, avril–mai 2026", FIG / "barres_temperature_max.png", "#d94801")
    bar_chart([p["lst_mean_C"] for p in profiles], names, "Température moyenne de surface par arrondissement", "Moyenne (°C) — composite avril–mai 2026", FIG / "barres_temperature_moyenne.png", "#e6550d")
    bar_chart([p["ndvi_mean"] for p in profiles], names, "NDVI moyen par arrondissement", "NDVI — Landsat 8/9, avril–mai 2026", FIG / "barres_ndvi.png", "#3d8c54")

    hottest = max(profiles, key=lambda p: p["lst_mean_C"] or -99)["arrondissement"]
    coolest = min(profiles, key=lambda p: p["lst_mean_C"] or 99)["arrondissement"]
    greenest = max(profiles, key=lambda p: p["ndvi_mean"] or -99)["arrondissement"]
    meta = {
        "title": "Îlots de chaleur à Paris",
        "window": f"1 avril – 31 mai {YEAR}",
        "n_landsat": n_scenes,
        "t_city": round(t_city, 2) if t_city is not None else None,
        "t_rural": round(t_rural, 2) if t_rural is not None else None,
        "suhi_C": round(suhi, 2) if suhi is not None else None,
        "lst_p98_C": round(p98, 2) if p98 is not None else None,
        "lst_scene_max_C": round(scene_peak, 2) if scene_peak is not None else None,
        "lst_composite_max_C": round(comp_max, 2) if comp_max is not None else None,
        "ndvi_mean": round(ndvi_mean, 3) if ndvi_mean is not None else None,
        "lst_cut": cut,
        "scale_max_C": scale_max,
        "rural_buffer_m": RURAL_BUFFER_M,
        "hottest": hottest,
        "coolest": coolest,
        "greenest": greenest,
        "lst_hours": hours["label"],
        "lst_hours_local": hours["local"],
        "lst_hours_utc": hours["utc"],
        "timezone": hours["tz_name"],
        "geometry": "OSM relation 7444 + opendata.paris.fr arrondissements",
        "profiles": profiles,
    }
    (OUT / "profiles.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    with (OUT / "profiles.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(profiles[0].keys()))
        w.writeheader()
        w.writerows(profiles)
    print(json.dumps({k: meta[k] for k in meta if k != "profiles"}, ensure_ascii=False, indent=2), flush=True)
    write_site(
        meta, profiles, hero, veg_path,
        {
            "peak": FIG / "barres_temperature_max.png",
            "mean": FIG / "barres_temperature_moyenne.png",
            "ndvi": FIG / "barres_ndvi.png",
        },
    )
    print("done", flush=True)


if __name__ == "__main__":
    main()
