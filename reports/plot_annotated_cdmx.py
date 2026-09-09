"""NYC-style annotated vegetation + temperature maps for CDMX and each alcaldia."""
from __future__ import annotations

import io
import json
import math
import re
import unicodedata
from pathlib import Path

import ee
import geemap
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import requests
from matplotlib.cm import ScalarMappable
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "cdmx_heat_islands"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

ee.Initialize(project="ee-my-usenvdi")

START, END = "2026-04-01", "2026-06-01"
PERIOD = "Apr–May 2026"
LST_HOURS = "~10:30 local (16:30 UTC), Landsat 8/9 descending"
ECO_HOURS = "ISS overpass, mixed hours (mostly non-midday)"
LST_FORMULA = "LST = 0.00341802×DN + 149 − 273.15 (°C)"
NDVI_FORMULA = "NDVI = (NIR − Red) / (NIR + Red)"
ECO_FORMULA = "LST = LST_K − 273.15 (°C)"
LST_SOURCE = "USGS Landsat 8/9 Collection 2 Level-2 ST_B10"
NDVI_SOURCE = "USGS Landsat 8/9 Collection 2 Level-2 SR_B4/SR_B5"
ECO_SOURCE = "NASA ECOSTRESS L2T LSTE V002"

NDVI_MIN, NDVI_MAX = 0.05, 0.70
LST_MIN, LST_MAX = 22.0, 48.0
ECO_MIN, ECO_MAX = 8.0, 24.0

VEG_PALETTE = ["#f3edd8", "#dce8b4", "#8fbf7a", "#3d8c54", "#14532d"]
TEMP_PALETTE = ["#2b1155", "#6a1c80", "#c43c4a", "#f18d2a", "#fde725"]
ECO_PALETTE = ["#1b0c41", "#4b0c6b", "#b63679", "#fb8761", "#fcfdbf"]


def slug(name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_name = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", ascii_name.lower()).strip("_")


def cloud_mask(image):
    qa = image.select("QA_PIXEL")
    mask = qa.bitwiseAnd(1 << 3).Or(qa.bitwiseAnd(1 << 4))
    return image.updateMask(mask.Not())


def prep_lst(image):
    st = image.select("ST_B10").multiply(0.00341802).add(149.0).subtract(273.15).rename("ST_C")
    return cloud_mask(image).addBands(st, None, True).select("ST_C")


def prep_ndvi(image):
    img = cloud_mask(image)
    nir = img.select("SR_B5").multiply(0.0000275).add(-0.2)
    red = img.select("SR_B4").multiply(0.0000275).add(-0.2)
    return nir.subtract(red).divide(nir.add(red)).rename("NDVI")


def load_col(cid, mapper):
    return (
        ee.ImageCollection(cid)
        .filterBounds(aoi_bounds)
        .filterDate(START, END)
        .filter(ee.Filter.lt("CLOUD_COVER", 80))
        .map(mapper)
    )


def fetch_rgb(image, vis, region, dim=900):
    vis_img = image.visualize(**vis).unmask(ee.Image.constant([72, 72, 72]))
    url = vis_img.getThumbURL({"region": region, "dimensions": dim, "format": "png"})
    return Image.open(io.BytesIO(requests.get(url, timeout=180).content)).convert("RGB")


def scale_km(bounds):
    w, s, e, n = bounds
    lat = 0.5 * (s + n)
    width_km = abs(e - w) * 111.32 * math.cos(math.radians(lat))
    if width_km >= 30:
        return 5
    if width_km >= 12:
        return 2
    return 1


def add_scale_and_north(ax, bounds, km):
    w, s, e, n = bounds
    lat = 0.5 * (s + n)
    width_km = abs(e - w) * 111.32 * math.cos(math.radians(lat))
    frac = km / width_km if width_km else 0.15
    x0, x1 = 0.08, 0.08 + min(frac, 0.35)
    ax.plot([x0, x1], [0.93, 0.93], transform=ax.transAxes, color="white", lw=3.2, solid_capstyle="butt")
    ax.plot([x0, x1], [0.93, 0.93], transform=ax.transAxes, color="black", lw=1.4, solid_capstyle="butt")
    ax.text((x0 + x1) / 2, 0.965, f"{km} km", transform=ax.transAxes, ha="center", va="top", fontsize=8, color="white", fontweight="bold")
    ax.annotate("N", xy=(0.93, 0.88), xytext=(0.93, 0.97), xycoords="axes fraction",
                ha="center", va="top", fontsize=8, fontweight="bold", color="white",
                arrowprops=dict(arrowstyle="-|>", color="white", lw=1.2))


def add_watermark(fig):
    fig.text(
        0.985,
        0.025,
        "Anaplian.com",
        ha="right",
        va="bottom",
        fontsize=13,
        fontweight="bold",
        color="#4a4a4a",
        alpha=0.82,
        fontfamily="sans-serif",
    )


def add_cbar(fig, ax, cmap, vmin, vmax, label, min_txt, max_txt):
    sm = ScalarMappable(norm=mcolors.Normalize(vmin, vmax), cmap=cmap)
    sm.set_array([])
    cax = ax.inset_axes([0.12, -0.16, 0.76, 0.045])
    cbar = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cbar.set_ticks([vmin, vmax])
    cbar.set_ticklabels([min_txt, max_txt])
    cbar.ax.tick_params(labelsize=8)
    cbar.set_label(label, fontsize=9, fontweight="bold", labelpad=2)


def two_panel(veg, temp, bounds, title, veg_note, temp_note, outfile, km=None):
    km = km or scale_km(bounds)
    veg_cmap = mcolors.LinearSegmentedColormap.from_list("veg", VEG_PALETTE)
    temp_cmap = mcolors.LinearSegmentedColormap.from_list("tmp", TEMP_PALETTE)
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 7.1), facecolor="white")
    for ax, im in zip(axes, (veg, temp)):
        ax.imshow(im)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#111")
            sp.set_linewidth(0.6)
        add_scale_and_north(ax, bounds, km)
    add_cbar(fig, axes[0], veg_cmap, NDVI_MIN, NDVI_MAX, "Vegetation (NDVI)", "sparse", "dense")
    add_cbar(
        fig,
        axes[1],
        temp_cmap,
        LST_MIN,
        LST_MAX,
        "Temperature (°C)",
        f"min {LST_MIN:.0f}",
        f"max {LST_MAX:.0f}",
    )
    fig.suptitle(title, fontsize=13, fontweight="bold", y=0.98)
    fig.text(0.25, 0.015, veg_note, ha="center", va="bottom", fontsize=7, color="#333")
    fig.text(0.75, 0.015, temp_note, ha="center", va="bottom", fontsize=7, color="#333")
    add_watermark(fig)
    fig.subplots_adjust(left=0.03, right=0.97, top=0.90, bottom=0.22, wspace=0.04)
    fig.savefig(outfile, dpi=160)
    plt.close(fig)
    print("saved", outfile.name, flush=True)


def one_panel(im, bounds, title, note, outfile, cmap_colors, vmin, vmax, cbar_label, min_txt, max_txt):
    km = scale_km(bounds)
    cmap = mcolors.LinearSegmentedColormap.from_list("p", cmap_colors)
    fig, ax = plt.subplots(figsize=(6.6, 7.4), facecolor="white")
    ax.imshow(im)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color("#111")
        sp.set_linewidth(0.6)
    add_scale_and_north(ax, bounds, km)
    add_cbar(fig, ax, cmap, vmin, vmax, cbar_label, min_txt, max_txt)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=8)
    fig.text(0.5, 0.015, note, ha="center", va="bottom", fontsize=7, color="#333")
    add_watermark(fig)
    fig.subplots_adjust(left=0.04, right=0.96, top=0.90, bottom=0.20)
    fig.savefig(outfile, dpi=160)
    plt.close(fig)
    print("saved", outfile.name, flush=True)


# --- data ---
CITY_ONLY = False
city_gdf = gpd.read_file(ROOT / "data/boundaries/ciudad_de_mexico/ciudad_de_mexico.shp").to_crs("EPSG:4326")
alc_gdf = gpd.read_file(ROOT / "data/boundaries/cdmx_alcaldias/cdmx_alcaldias.shp", encoding="utf-8").to_crs("EPSG:4326")
if "alcaldia" not in alc_gdf.columns:
    alc_gdf["alcaldia"] = alc_gdf["shapeName"]
city_fc = geemap.geopandas_to_ee(city_gdf)
alc_fc = geemap.geopandas_to_ee(alc_gdf[["alcaldia", "geometry"]])
aoi = city_fc.geometry()
aoi_bounds = aoi.bounds()

roads_fc = ee.FeatureCollection([])
outline = ee.Image().paint(alc_fc, 1, 1)

lst = load_col("LANDSAT/LC08/C02/T1_L2", prep_lst).merge(load_col("LANDSAT/LC09/C02/T1_L2", prep_lst)).mean().clip(aoi)
ndvi = load_col("LANDSAT/LC08/C02/T1_L2", prep_ndvi).merge(load_col("LANDSAT/LC09/C02/T1_L2", prep_ndvi)).mean().clip(aoi)

def prep_eco(image):
    qa_mask = image.select("QC").bitwiseAnd(3).lt(2)
    cloud_ok = image.select("cloud").eq(0)
    return image.select("LST").updateMask(qa_mask).updateMask(cloud_ok).rename("ECO")


eco = (
    ee.ImageCollection("NASA/ECOSTRESS/L2T_LSTE/V2")
    .filterBounds(aoi.centroid())
    .filterDate(START, END)
    .map(prep_eco)
    .mean()
    .subtract(273.15)
    .clip(aoi)
)

veg_vis = {"min": NDVI_MIN, "max": NDVI_MAX, "palette": VEG_PALETTE}
lst_vis = {"min": LST_MIN, "max": LST_MAX, "palette": TEMP_PALETTE}
eco_vis = {"min": ECO_MIN, "max": ECO_MAX, "palette": ECO_PALETTE}

print("Fetching city panels...", flush=True)
city_bounds = tuple(city_gdf.total_bounds)
city_veg = fetch_rgb(ndvi, veg_vis, aoi, 1000)
city_lst = fetch_rgb(lst, lst_vis, aoi, 1000)

veg_note = f"{NDVI_SOURCE}\n{PERIOD}  |  {LST_HOURS}\n{NDVI_FORMULA}"
temp_note = f"{LST_SOURCE}\n{PERIOD}  |  {LST_HOURS}\n{LST_FORMULA}"
eco_note = f"{ECO_SOURCE}\n{PERIOD}  |  {ECO_HOURS}\n{ECO_FORMULA}"

two_panel(
    city_veg,
    city_lst,
    city_bounds,
    "Ciudad de México — vegetation and surface heat",
    veg_note,
    temp_note,
    FIG / "cdmx_vegetation_temperature.png",
    km=5,
)

if CITY_ONLY:
    print("city vegetation-temperature without roads", flush=True)
    raise SystemExit(0)

one_panel(
    city_veg,
    city_bounds,
    "Ciudad de México — vegetation",
    veg_note,
    FIG / "cdmx_vegetation.png",
    VEG_PALETTE,
    NDVI_MIN,
    NDVI_MAX,
    "Vegetation (NDVI)",
    "sparse",
    "dense",
)
one_panel(
    city_eco,
    city_bounds,
    "Ciudad de México — atmospheric-adjacent heat",
    eco_note,
    FIG / "cdmx_atmospheric_annotated.png",
    ECO_PALETTE,
    ECO_MIN,
    ECO_MAX,
    "Temperature (°C)",
    f"min {ECO_MIN:.0f}",
    f"max {ECO_MAX:.0f}",
)

for _, row in alc_gdf.sort_values("alcaldia").iterrows():
    name = row["alcaldia"]
    geom = ee.Feature(alc_fc.filter(ee.Filter.eq("alcaldia", name)).first()).geometry()
    bounds = tuple(row.geometry.bounds)
    print("panel", name, flush=True)
    veg_im = fetch_rgb(ndvi.clip(geom), veg_vis, geom, 720)
    lst_im = Image.open(io.BytesIO(requests.get(
        lst.clip(geom).visualize(**lst_vis)
        .blend(roads_layer.visualize(palette=["ffffff"], min=0, max=1))
        .unmask(ee.Image.constant([72, 72, 72]))
        .getThumbURL({"region": geom, "dimensions": 720, "format": "png"}),
        timeout=180,
    ).content)).convert("RGB")
    eco_im = fetch_rgb(eco.clip(geom), eco_vis, geom, 720)
    s = slug(name)
    two_panel(
        veg_im,
        lst_im,
        bounds,
        f"{name} — vegetation and surface heat",
        veg_note,
        temp_note,
        FIG / f"{s}_vegetation_temperature.png",
    )
    one_panel(
        veg_im,
        bounds,
        f"{name} — vegetation",
        veg_note,
        FIG / f"{s}_vegetation.png",
        VEG_PALETTE,
        NDVI_MIN,
        NDVI_MAX,
        "Vegetation (NDVI)",
        "sparse",
        "dense",
    )
    one_panel(
        eco_im,
        bounds,
        f"{name} — atmospheric-adjacent heat",
        eco_note,
        FIG / f"{s}_atmospheric_annotated.png",
        ECO_PALETTE,
        ECO_MIN,
        ECO_MAX,
        "Temperature (°C)",
        f"min {ECO_MIN:.0f}",
        f"max {ECO_MAX:.0f}",
    )

# refresh HTML to the new pair figures
profiles = json.loads((OUT / "profiles.json").read_text(encoding="utf-8"))
cards = []
for p in profiles["profiles"]:
    s = p["slug"]
    cards.append(f"""
    <section class="card">
      <h2>{p['alcaldia']}</h2>
      <ul class="stats">
        <li><b>Greatest surface temperature</b> {p['lst_peak_C']:.1f} °C</li>
        <li><b>Average surface temperature</b> {p['lst_mean_C']:.1f} °C</li>
        <li><b>Highest difference vs rural CDMX</b> {p['suhi_C']:+.1f} °C</li>
        <li><b>Air temperature (ERA5 2 m max)</b> {p['tair_max_C']:.1f} °C</li>
      </ul>
      <figure>
        <img src="figures/{s}_vegetation_temperature.png" alt="Vegetation and surface heat, {p['alcaldia']}">
      </figure>
      <figure>
        <img src="figures/{s}_vegetation.png" alt="Vegetation, {p['alcaldia']}">
      </figure>
      <figure>
        <img src="figures/{s}_atmospheric_annotated.png" alt="Atmospheric heat, {p['alcaldia']}">
      </figure>
    </section>
    """)

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Mexico City heat islands — April–May 2026</title>
<style>
 body {{ font-family: Georgia, serif; max-width: 1100px; margin: 32px auto; color: #1a1a1a; }}
 h1,h2 {{ font-family: Helvetica, Arial, sans-serif; }}
 img {{ width: 100%; background: #fff; }}
 .card {{ border-top: 1px solid #ddd; padding-top: 24px; margin-top: 24px; }}
</style></head><body>
<h1>Mexico City heat islands</h1>
<p>Window: <b>April–May 2026</b>. Surface heat ~10:30 local Landsat. Vegetation is NDVI from the same scenes. Atmospheric-adjacent maps are ECOSTRESS (mixed ISS hours).</p>
<figure><img src="figures/cdmx_vegetation_temperature.png" alt="CDMX vegetation and surface heat"></figure>
<figure><img src="figures/cdmx_vegetation.png" alt="CDMX vegetation"></figure>
<figure><img src="figures/cdmx_atmospheric_annotated.png" alt="CDMX atmospheric heat"></figure>
{''.join(cards)}
</body></html>
"""
(OUT / "report.html").write_text(html, encoding="utf-8")
print("updated report.html", flush=True)
print("done", flush=True)
