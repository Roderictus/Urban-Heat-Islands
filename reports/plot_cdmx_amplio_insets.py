"""CDMX April–May all-scene LST composite with AICM and Central de Abasto insets.

Uses every Landsat 8/9 scene in the window (pixel cloud/fill mask, no 80%
scene cut) and overlays LST above LST_CUT.

    python reports/plot_cdmx_amplio_insets.py
    python reports/plot_cdmx_amplio_insets.py --year 2026 --lst-cut 35
"""
from __future__ import annotations

import argparse
import os
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
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Rectangle
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reports"))
import plot_cdmx_heat_over_streets as heat  # noqa: E402
from plot_cdmx_heat_methods import collection_for, year_window  # noqa: E402

LST_CUT = 35.0
LST_SCALE_MAX = 48.0
YEAR = 2026
INSET_PAD = 0.004
OUT = ROOT / "reports" / "cdmx_heat_islands" / "timelapse_methods" / "m3_amplio_35c_insets"
AICM = ROOT / "data/boundaries/aicm/aicm.geojson"
CEDA = ROOT / "data/boundaries/central_de_abasto/central_de_abasto.geojson"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=YEAR)
    p.add_argument("--lst-cut", type=float, default=LST_CUT)
    return p.parse_args()


def union_geom(gdf):
    geom = gdf.geometry
    return geom.union_all() if hasattr(geom, "union_all") else geom.unary_union


def padded_bounds(geom, pad=INSET_PAD):
    w, s, e, n = geom.bounds
    return (w - pad, s - pad, e + pad, n + pad)


def overlay_rgb(clip_geom, bounds, zoom, hot, vis, outline_w=3) -> Image.Image:
    base = heat.style_base(heat.fetch_esri(bounds, zoom))
    width, height = heat.cap_size(*base.size)
    if (width, height) != base.size:
        base = base.resize((width, height), Image.Resampling.LANCZOS)
    region = ee.Geometry.Rectangle(list(bounds), proj="EPSG:4326", geodesic=False)
    heat_img = heat.fetch_gee_rgb(
        hot.clip(ee.Geometry(clip_geom.__geo_interface__)), vis, region, width, height
    )
    composite = heat.compose_overlay(np.array(base), np.array(heat_img))
    mask = np.array(heat.raster_mask(clip_geom, bounds, (width, height)))
    composite[mask == 0] = (6, 6, 6)
    poster = heat.draw_outline(Image.fromarray(composite), clip_geom, bounds, width=outline_w)
    return poster.filter(ImageFilter.SMOOTH)


def box_pixels(box_bounds, map_bounds, width, height):
    west, south, east, north = map_bounds
    bw, bs, be, bn = box_bounds
    left, bottom = heat.lonlat_to_merc(west, south)
    right, top = heat.lonlat_to_merc(east, north)

    def xy(lon, lat):
        x, y = heat.lonlat_to_merc(lon, lat)
        px = (x - left) / (right - left) * (width - 1)
        py = (top - y) / (top - bottom) * (height - 1)
        return px, py

    x0, y0 = xy(bw, bn)
    x1, y1 = xy(be, bs)
    return min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0)


def main():
    args = parse_args()
    year = args.year
    lst_cut = float(args.lst_cut)
    heat.THRESHOLD = lst_cut
    OUT.mkdir(parents=True, exist_ok=True)

    city_gdf = gpd.read_file(ROOT / "data/boundaries/ciudad_de_mexico/ciudad_de_mexico.shp").to_crs("EPSG:4326")
    city_geom = union_geom(city_gdf)
    city_fc = geemap.geopandas_to_ee(city_gdf)
    aoi = city_fc.geometry()
    west, south, east, north = city_gdf.total_bounds
    city_bounds = (
        west - heat.CITY_PAD, south - heat.CITY_PAD,
        east + heat.CITY_PAD, north + heat.CITY_PAD,
    )
    city_region = ee.Geometry.Rectangle(list(city_bounds), proj="EPSG:4326", geodesic=False)

    aicm_geom = union_geom(gpd.read_file(AICM).to_crs("EPSG:4326"))
    ceda_geom = union_geom(gpd.read_file(CEDA).to_crs("EPSG:4326"))
    air_bounds = padded_bounds(aicm_geom, 0.005)
    ceda_bounds = padded_bounds(ceda_geom, 0.0035)

    start, end, period = year_window(year)
    heat.START, heat.END, heat.PERIOD = start, end, period
    print(f"Composite amplio {period}, corte LST {lst_cut:.0f} °C", flush=True)
    col = collection_for(year, city_region, None)
    n_scenes = int(col.size().getInfo())
    print("escenas", n_scenes, flush=True)
    lst = col.mean().clip(aoi)
    stats = lst.updateMask(lst.gt(lst_cut)).reduceRegion(
        ee.Reducer.minMax().combine(ee.Reducer.percentile([98]), sharedInputs=True),
        aoi, 100, maxPixels=1e8, bestEffort=True,
    ).getInfo()
    abs_max = float(stats.get("ST_C_max") or 50.0)
    print("hot stats", stats, flush=True)

    vis = {"min": lst_cut, "max": LST_SCALE_MAX, "palette": heat.HEAT_PALETTE}
    hot = lst.updateMask(lst.gt(lst_cut))

    print("ciudad", flush=True)
    city_im = overlay_rgb(city_geom, city_bounds, 13, hot, vis, outline_w=3)
    print("aeropuerto", flush=True)
    air_im = overlay_rgb(aicm_geom, air_bounds, 16, hot, vis, outline_w=2)
    print("central de abasto", flush=True)
    ceda_im = overlay_rgb(ceda_geom, ceda_bounds, 16, hot, vis, outline_w=2)

    fig = plt.figure(figsize=(11.4, 14.2), facecolor="#050505")
    ax = fig.add_axes([0.04, 0.34, 0.92, 0.60])
    ax.imshow(city_im)
    ax.set_axis_off()
    wpx, hpx = city_im.size
    for bounds, color, label in (
        (air_bounds, "#22d3ee", "A"),
        (ceda_bounds, "#fbbf24", "B"),
    ):
        x, y, bw, bh = box_pixels(bounds, city_bounds, wpx, hpx)
        ax.add_patch(
            Rectangle((x, y), bw, bh, fill=False, edgecolor=color, linewidth=1.8, zorder=5)
        )
        ax.text(
            x + 6, y + 14, label, color=color, fontsize=11, fontweight="bold",
            va="top", ha="left", zorder=6,
        )
    heat.add_scale_north(ax, city_bounds, heat.scale_km_length(city_bounds))

    ax_a = fig.add_axes([0.04, 0.07, 0.44, 0.24])
    ax_b = fig.add_axes([0.52, 0.07, 0.44, 0.24])
    ax_a.imshow(air_im)
    ax_b.imshow(ceda_im)
    for a, color, title in (
        (ax_a, "#22d3ee", "A  Aeropuerto AICM"),
        (ax_b, "#fbbf24", "B  Central de Abasto"),
    ):
        a.set_axis_off()
        for sp in a.spines.values():
            sp.set_visible(True)
            sp.set_color(color)
            sp.set_linewidth(1.8)
        a.set_title(title, color=color, fontsize=10, fontweight="bold", pad=6)

    fig.text(
        0.5, 0.975,
        f"Islas de calor en la Ciudad de México — {year}",
        ha="center", va="top", color="white", fontsize=17, fontweight="bold",
    )
    fig.text(
        0.5, 0.948,
        f"Composite amplio abril–mayo  ·  {n_scenes} escenas Landsat 8/9  ·  LST > {lst_cut:.0f} °C",
        ha="center", va="top", color="#c8c8c8", fontsize=9,
    )
    cmap = mcolors.LinearSegmentedColormap.from_list("lst", heat.HEAT_PALETTE)
    sm = ScalarMappable(norm=mcolors.Normalize(lst_cut, LST_SCALE_MAX), cmap=cmap)
    sm.set_array([])
    cax = fig.add_axes([0.33, 0.028, 0.34, 0.016])
    cbar = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cbar.set_ticks([lst_cut, LST_SCALE_MAX])
    cbar.set_ticklabels([f"{lst_cut:.0f}", f"{LST_SCALE_MAX:.0f}"])
    cbar.ax.tick_params(colors="white", labelsize=8)
    cbar.outline.set_edgecolor("white")
    cbar.set_label("Temperatura de superficie (°C)", color="white", fontsize=9, labelpad=4)
    fig.text(0.97, 0.012, "Anaplian.com", ha="right", va="bottom", fontsize=18, fontweight="bold", color="#c4c4c4")
    fig.text(
        0.04, 0.012,
        f"Máximo observado {abs_max:.1f} °C  ·  todas las escenas, máscara de nubes por píxel",
        ha="left", va="bottom", color="#9a9a9a", fontsize=7.5,
    )
    outfile = OUT / f"cdmx_{year}_amplio_{int(lst_cut)}c_insets.png"
    fig.savefig(outfile, dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("saved", outfile, flush=True)


if __name__ == "__main__":
    main()
