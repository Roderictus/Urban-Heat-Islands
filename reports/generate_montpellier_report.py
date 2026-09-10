"""Montpellier April–May 2026 heat-island analysis and French PDF.

City-level only (no arrondissements). Pixel-mean of all Landsat 8/9 scenes,
rural SUHI in a 20 km GHSL belt, overlay LST > 35 °C.

    python reports/generate_montpellier_report.py
"""
from __future__ import annotations

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
BND = ROOT / "data" / "boundaries" / "montpellier" / "montpellier.geojson"
OUT = ROOT / "reports" / "montpellier_heat_islands"
FIG = OUT / "figures"
SITE = ROOT / "reports" / "sitio_ilots_chaleur_montpellier"
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


def write_pdf(meta, hero, veg):
    SITE.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(hero, ASSETS / "01_montpellier_transparence.png")
    shutil.copy2(veg, ASSETS / "02_vegetation_temperature.png")

    n = int(meta["n_landsat"])
    t_rural = float(meta["t_rural"])
    t_city = float(meta["t_city"])
    suhi = float(meta["suhi_C"])
    peak = float(meta["lst_peak_C"])
    cut = float(meta["lst_cut"])
    local_h = meta.get("lst_hours_local", "12 h 30")
    utc_h = meta.get("lst_hours_utc", "10 h 30")

    intro1 = (
        "La hausse de la température moyenne de la planète aggrave la vulnérabilité aux "
        "chaleurs excessives. Il ne s'agit pas seulement d'un degré de plus dans la moyenne "
        "globale : cette hausse pousse davantage de journées au-delà de seuils dangereux pour "
        "la santé, le travail en extérieur et les réseaux d'eau et d'énergie. En ville, le "
        "risque se concentre. L'asphalte, le béton, les toitures sombres et le métal absorbent "
        "une grande part du rayonnement solaire et le restituent en chaleur ; contrairement à "
        "un arbre ou un sol humide, ils n'évaporent presque pas d'eau et n'offrent pas d'ombre. "
        "Rues étroites et immeubles forment des canyons qui piègent l'air chaud. Le résultat : "
        "des îlots de chaleur — parkings, hangars, avenues et toitures où la surface atteint "
        "des températures que le corps ne tolère pas en exposition prolongée."
    )
    intro2 = (
        f"Avec Landsat 8 et Landsat 9, nous cartographions les surfaces les plus chaudes de "
        f"Montpellier. La carte est la moyenne par pixel de {n} scènes d'avril et mai {YEAR}, "
        f"acquises vers {local_h}, heure locale. Sur chaque pixel, nuages, ombres et valeurs "
        "invalides sont masqués avant de moyenner ; on ne jette pas la scène entière. Le "
        "capteur thermique — bande 10, entre 10,6 et 11,2 micromètres — estime la chaleur du "
        "sol, des toits et du bitume, pas celle de l'air à l'ombre. Seules les surfaces "
        f"au-dessus de {cut:.0f} °C sont coloriées. En parallèle, le NDVI montre où la "
        "végétation est dense. La température de la commune se compare à la moyenne des zones "
        f"rurales dans un rayon de 20 km (garrigue, vignoble, hinterland de l'Hérault). "
        f"Le 98e centile du composite atteint {peak:.1f} °C en surface ; l'écart urbain–rural (SUHI) est de "
        f"{suhi:+.1f} °C."
    )
    intro3 = (
        "Ces pics ne sont pas un épisode isolé : avec davantage de vagues de chaleur et de "
        "surfaces imperméables, ils tendent à s'aggraver. Ils servent à repérer des lieux "
        "d'intervention. L'urbanisme tactique permet de tester, en quelques semaines, des "
        "ombres temporaires, de la peinture à fort albédo dans les cours d'école ou les rues "
        "de jeu, et des trottoirs plus perméables. La végétation reste le levier le plus "
        "durable : un arbre intercepte le soleil et rafraîchit l'air par transpiration. "
        "Coulées vertes, toitures et murs végétalisés, préservation des parcs (Lez, Mosson, "
        "garrigue) réduisent la charge thermique. Toits et revêtements froids, désimperméabilisation "
        "et priorité aux personnes les plus exposées — personnes âgées, enfance, travail en "
        "extérieur — complètent le tableau. La donnée satellitaire ne remplace pas le projet "
        "local ; elle indique où agir d'abord."
    )
    lead = (
        f"À Montpellier, au printemps {YEAR}, la température moyenne de surface de la commune "
        f"est de {t_city:.1f} °C, contre {t_rural:.1f} °C dans la ceinture rurale "
        f"({suhi:+.1f} °C). Le 98e centile du composite est de {peak:.1f} °C. Ce n'est pas la "
        "température de l'air : un toit ou un parking peut dépasser 40 °C quand l'air reste "
        "proche de 20 °C."
    )
    method = (
        f"Les cartes sont un composite large : la moyenne par pixel des {n} scènes Landsat 8 "
        f"et Landsat 9 (Collection 2, niveau 2) acquises entre le 1er avril et le 31 mai {YEAR}. "
        "On ne jette pas une scène entière pour cause de nuages : sur chaque pixel, le remplissage, "
        "les nuages, les ombres et les températures hors de la plage valide (0 à 80 °C) sont "
        "masqués, puis les observations utiles sont moyennées. Les satellites survolent "
        f"l'Hérault vers {local_h}, heure locale (près de {utc_h} UTC). Ce qui est peint "
        "n'est pas l'air à l'ombre, mais la température de surface — toits, asphalte, sol nu "
        "et végétation — avec la bande 10 de l'infrarouge thermique (10,6 à 11,2 micromètres ; "
        "LST = 0,00341802 × DN + 149 − 273,15). En jaune à rouge, en semi-transparence sur "
        f"l'image satellite, n'apparaissent que les surfaces au-dessus de {cut:.0f} °C. "
        "Le verdure est mesuré par le NDVI (rouge et proche infrarouge). L'écart urbain–rural "
        f"soustrait {t_rural:.1f} °C, moyenne des classes rurales du GHSL 2020 (SMOD 11, 12 et 13, "
        "hors eau) dans un rayon de 20 km autour de la commune."
    )

    (SITE / "texte_section.md").write_text(
        f"""# Îlots de chaleur à Montpellier

**Surtitre.** Anaplian.com · télédétection urbaine

**Titre.** Îlots de chaleur à Montpellier

**Chapô.** Avril et mai {YEAR} · Landsat 8 et 9 · température de surface et végétation

## Introduction

{intro1}

{intro2}

{intro3}

## En une ligne

{lead}

## Méthodologie

{method}

## Chiffres

- Scènes Landsat : {n}
- Moyenne commune : {t_city:.1f} °C
- Maximum du composite (p98) : {peak:.1f} °C
- Référence rurale (20 km) : {t_rural:.1f} °C
- SUHI : {suhi:+.1f} °C
- Seuil d'affichage : {cut:.0f} °C
""",
        encoding="utf-8",
    )

    html = f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Îlots de chaleur à Montpellier — avril et mai {YEAR}</title>
  <style>
    :root {{ --ink:#1a1a1a; --muted:#555; --line:#e6e1d8; }}
    body {{ margin:0; color:var(--ink); background:#f7f4ef; font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif; line-height:1.55; }}
    header {{ background:#111; color:#fff; padding:36px 20px 28px; }}
    header .wrap, main, footer .wrap {{ max-width:920px; margin:0 auto; }}
    h1 {{ font-size:1.85rem; margin:0 0 8px; }}
    .kicker {{ color:#f0c27a; font-size:0.82rem; letter-spacing:0.12em; text-transform:uppercase; }}
    main {{ padding:28px 20px 64px; }}
    figure {{ margin:0 0 1.4rem; }}
    figure img {{ width:100%; height:auto; background:#111; display:block; }}
    figcaption {{ font-size:0.88rem; color:var(--muted); margin-top:8px; }}
    .method {{ background:#fff; border:1px solid var(--line); padding:1rem 1.1rem; }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <div class="kicker">Anaplian.com · télédétection urbaine</div>
      <h1>Îlots de chaleur à Montpellier</h1>
      <p>Avril et mai {YEAR} · Landsat 8 et 9 · température de surface et végétation</p>
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
      <img src="assets/01_montpellier_transparence.png" alt="Montpellier, température de surface">
      <figcaption>Températures de surface au-dessus de {cut:.0f} °C, en semi-transparence sur l'image satellite.</figcaption>
    </figure>
    <h2>Végétation et chaleur, côte à côte</h2>
    <figure>
      <img src="assets/02_vegetation_temperature.png" alt="NDVI et température de surface à Montpellier">
      <figcaption>À gauche, verdure (NDVI). À droite, température de surface de la même fenêtre.</figcaption>
    </figure>
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
    write_body("Îlots de chaleur à Montpellier", 13, True, (15, 15, 15), 6)
    write_body(
        f"ANAPLIAN.COM  |  Avril et mai {YEAR}  |  Landsat 8 et 9  |  LST > {cut:.0f} C",
        8.5, True, (180, 90, 20), 4.5,
    )
    pdf.ln(1.0)
    fit_image(ASSETS / "01_montpellier_transparence.png")

    pdf.add_page()
    write_body("Pourquoi cette étude", 12, True, (15, 15, 15), 6)
    pdf.ln(1)
    for para in (intro1, intro2, intro3, lead):
        write_body(para, 10.5, False, (20, 20, 20), 5.5)
        pdf.ln(2.4)

    pdf.add_page()
    write_body("Végétation et chaleur, côte à côte", 12, True, (15, 15, 15), 6)
    pdf.ln(1)
    fit_image(
        ASSETS / "02_vegetation_temperature.png",
        "Gauche : verdure (NDVI). Droite : température de surface.",
    )

    pdf.add_page()
    write_body("Comment c'est fait", 14, True)
    pdf.ln(2)
    write_body(method, 11, False, (20, 20, 20), 6.2)
    pdf.ln(6)
    write_body("Chiffres clés", 12, True)
    pdf.ln(2)
    stats = [
        f"Scènes Landsat 8/9 : {n}",
        f"Température moyenne de la commune : {t_city:.1f} °C",
        f"Maximum du composite (p98) : {peak:.1f} °C",
        f"Référence rurale (20 km, GHSL) : {t_rural:.1f} °C",
        f"SUHI (urbain − rural) : {suhi:+.1f} °C",
        f"Seuil d'affichage : {cut:.0f} °C",
    ]
    for line in stats:
        write_body(line, 11, False, (20, 20, 20), 6.2)

    pdf_path = SITE / f"Ilots_de_chaleur_Montpellier_{YEAR}.pdf"
    pdf.output(str(pdf_path))
    for leftover in ASSETS.glob("_pdf_fit_*.png"):
        leftover.unlink(missing_ok=True)
    print("PDF", pdf_path, flush=True)
    print("HTML", SITE / "index.html", flush=True)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    city_gdf = gpd.read_file(BND).to_crs("EPSG:4326")
    city_geom = union_geom(city_gdf)
    city_fc = geemap.geopandas_to_ee(city_gdf)
    aoi = city_fc.geometry()
    west, south, east, north = city_gdf.total_bounds
    city_bounds = (west - CITY_PAD, south - CITY_PAD, east + CITY_PAD, north + CITY_PAD)
    city_region = ee.Geometry.Rectangle(list(city_bounds), proj="EPSG:4326", geodesic=False)
    rural_aoi = aoi.buffer(RURAL_BUFFER_M)

    start, end, period = year_window(YEAR)
    heat.START, heat.END, heat.PERIOD = start, end, "Avr–mai 2026"
    hours = heat.lst_overpass_hours(
        city_region, start, end, "Europe/Paris", lang="fr",
        fallback={"label": "~12 h 30 locale (10 h 30 UTC)", "local": "12 h 30", "utc": "10 h 30", "tz_name": "Europe/Paris"},
    )
    heat.LST_HOURS = hours["label"]
    heat.CITY_PAD = CITY_PAD
    print(f"Montpellier composite {period}  survol {hours['label']}", flush=True)

    col = collection_for(YEAR, city_region, None)
    n_scenes = int(col.size().getInfo())
    print("scènes", n_scenes, flush=True)
    lst = col.mean()
    lst_city = lst.clip(aoi)
    rural = rural_mask(rural_aoi)
    t_city = reduce_mean(lst_city, aoi, 30)
    t_rural = reduce_mean(lst.updateMask(rural).clip(rural_aoi), rural_aoi, 100)
    peak_info = lst_city.reduceRegion(
        ee.Reducer.minMax().combine(ee.Reducer.percentile([98]), sharedInputs=True),
        aoi, 30, maxPixels=1e8, bestEffort=True,
    ).getInfo()
    lst_max = col.max().clip(aoi)
    scene_peak = fnum(
        lst_max.reduceRegion(ee.Reducer.max(), aoi, 30, maxPixels=1e8, bestEffort=True).getInfo().get("ST_C")
    )
    p98 = fnum(peak_info.get("ST_C_p98"), t_city)
    comp_max = fnum(peak_info.get("ST_C_max"), p98)
    peak = scene_peak or comp_max
    suhi = None if t_city is None or t_rural is None else t_city - t_rural
    peak_display = p98 or comp_max
    print(
        f"T_city {t_city:.2f}  T_rural {t_rural:.2f}  SUHI {suhi:+.2f}  "
        f"scene_max {peak:.1f}  composite_max {comp_max:.1f}  p98 {p98:.1f}",
        flush=True,
    )

    cut = LST_CUT
    if p98 is not None and p98 < cut + 1:
        cut = 30.0
        print(f"p98 bas, seuil porté à {cut:.0f} °C", flush=True)
    heat.THRESHOLD = cut
    scale_max = max(cut + 8.0, min(LST_SCALE_MAX, (p98 or cut + 8) + 2))
    vis = {"min": cut, "max": scale_max, "palette": heat.HEAT_PALETTE}
    hot = lst.updateMask(lst.gt(cut))

    hero = FIG / f"montpellier_heat_over_streets_{int(cut)}c.png"
    print("carte overlay", flush=True)
    heat.make_map(
        city_geom, city_bounds, heat.zoom_for(city_bounds), hot, vis,
        "Îlots de chaleur à Montpellier",
        hero, scale_max, peak_display or scale_max, outline_w=3,
        overlay_caption=(
            f"{heat.LST_SOURCE}\nAvr–mai {YEAR}  |  {heat.LST_HOURS}\n"
            f"Composite large : moyenne par pixel de {n_scenes} scènes\n"
            f"Masque nuages/remplissage/plage valide par pixel\n"
            f"Overlay : température de surface > {cut:.0f} °C"
        ),
        cbar_label="Température de surface (°C)",
        footer=f"{n_scenes} scènes   ·   seuil {cut:.0f} °C   ·   p98 {peak_display:.1f} °C",
    )

    print("NDVI + LST", flush=True)
    ndvi = ndvi_collection(YEAR, city_region).mean().clip(aoi)
    ndvi_stats = ndvi.reduceRegion(
        ee.Reducer.percentile([5, 95]), aoi, 30, maxPixels=1e8, bestEffort=True
    ).getInfo()
    ndvi_lo = fnum(ndvi_stats.get("NDVI_p5"), 0.05)
    ndvi_hi = fnum(ndvi_stats.get("NDVI_p95"), 0.70)
    lst_lo = max(10.0, (t_rural or 18) - 4)
    lst_hi = max(lst_lo + 8, min(48.0, (p98 or 40) + 2))
    region = ee.Geometry.Rectangle(list(city_bounds), proj="EPSG:4326", geodesic=False)
    veg_im = heat.fetch_gee_rgb(
        ndvi, {"min": ndvi_lo, "max": ndvi_hi, "palette": VEG_PALETTE}, region, 1100, 900
    )
    tmp_im = heat.fetch_gee_rgb(
        lst_city, {"min": lst_lo, "max": lst_hi, "palette": TEMP_PALETTE}, region, 1100, 900
    )
    veg_path = FIG / "montpellier_vegetation_temperature.png"
    two_panel(
        veg_im, tmp_im, city_bounds,
        "Montpellier — végétation et température de surface",
        f"USGS Landsat 8/9 C2 L2  ·  NDVI = (PIR − rouge) / (PIR + rouge)  ·  {period}",
        f"USGS Landsat 8/9 C2 L2  ·  {heat.LST_FORMULA}  ·  {heat.LST_HOURS}",
        veg_path, (ndvi_lo, ndvi_hi), (lst_lo, lst_hi),
    )

    meta = {
        "title": "Îlots de chaleur à Montpellier",
        "window": f"1 avril – 31 mai {YEAR}",
        "n_landsat": n_scenes,
        "t_city": round(t_city, 2) if t_city is not None else None,
        "t_rural": round(t_rural, 2) if t_rural is not None else None,
        "suhi_C": round(suhi, 2) if suhi is not None else None,
        "lst_peak_C": round(peak_display, 2) if peak_display is not None else None,
        "lst_scene_max_C": round(peak, 2) if peak is not None else None,
        "lst_composite_max_C": round(comp_max, 2) if comp_max is not None else None,
        "lst_p98_C": round(p98, 2) if p98 is not None else None,
        "lst_cut": cut,
        "rural_buffer_m": RURAL_BUFFER_M,
        "lst_hours": hours["label"],
        "lst_hours_local": hours["local"],
        "lst_hours_utc": hours["utc"],
        "timezone": hours["tz_name"],
        "geometry": "OSM relation 28722, commune de Montpellier",
    }
    (OUT / "profiles.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2), flush=True)
    write_pdf(meta, hero, veg_path)
    print("done", flush=True)


if __name__ == "__main__":
    main()
