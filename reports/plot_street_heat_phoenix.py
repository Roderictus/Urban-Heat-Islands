"""Phoenix-style LST mapped only onto OSM streets for Iztapalapa and Central de Abasto."""
from __future__ import annotations

import sys
from pathlib import Path

import ee
import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
from shapely.geometry import LineString, MultiLineString

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import plot_cdmx_heat_over_streets as heat  # noqa: E402

OUT = ROOT / "reports" / "cdmx_heat_islands" / "street_network_heat"
OUT.mkdir(parents=True, exist_ok=True)
CACHE = ROOT / "data" / "boundaries" / "osm_streets"
CACHE.mkdir(parents=True, exist_ok=True)

OVERPASS = "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
HIGHWAY_RE = "motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|service"
THRESHOLD = 38.0
PALETTE = ["#F6E27A", "#F5A623", "#E53935", "#8E24AA", "#4A148C"]
STREET_ALPHA = 0.72
# Pixel widths at scale 1.0 (original). Iztapalapa uses a higher scale so the grid reads at borough extent.
STREET_WIDTH_SCALE = 1.0
IZTAPALAPA_STREET_WIDTH_SCALE = 2.0
CEDA_STREET_WIDTH_SCALE = 2.0
LINE_WIDTH = {
    "motorway": 4,
    "trunk": 4,
    "primary": 3,
    "secondary": 3,
    "tertiary": 2,
    "residential": 2,
    "unclassified": 2,
    "living_street": 2,
    "service": 1,
}

heat.THRESHOLD = THRESHOLD


def overpass_ways(bounds, timeout=180):
    west, south, east, north = bounds
    query = f"""
    [out:json][timeout:{timeout}];
    way["highway"~"^({HIGHWAY_RE})$"]({south},{west},{north},{east});
    out geom;
    """
    r = heat.SESSION.post(
        OVERPASS,
        data={"data": query},
        timeout=timeout + 40,
        headers={"User-Agent": "HeatIslandsECOSTRESS/1.0"},
    )
    r.raise_for_status()
    recs = []
    for el in r.json().get("elements", []):
        if el.get("type") != "way" or "geometry" not in el:
            continue
        coords = [(p["lon"], p["lat"]) for p in el["geometry"]]
        if len(coords) < 2:
            continue
        tags = el.get("tags", {})
        recs.append(
            {
                "osm_id": el["id"],
                "highway": tags.get("highway"),
                "name": tags.get("name"),
                "geometry": LineString(coords),
            }
        )
    if not recs:
        return gpd.GeoDataFrame(columns=["osm_id", "highway", "name", "geometry"], crs="EPSG:4326")
    return gpd.GeoDataFrame(recs, crs="EPSG:4326")


def fetch_streets(bounds, cache_path, tiles=1):
    if cache_path.exists():
        print("cache", cache_path.name, flush=True)
        return gpd.read_file(cache_path)
    west, south, east, north = bounds
    frames = []
    if tiles <= 1:
        print("Overpass", cache_path.stem, flush=True)
        frames.append(overpass_ways(bounds))
    else:
        xs = np.linspace(west, east, tiles + 1)
        ys = np.linspace(south, north, tiles + 1)
        for i in range(tiles):
            for j in range(tiles):
                bb = (float(xs[i]), float(ys[j]), float(xs[i + 1]), float(ys[j + 1]))
                print("Overpass tile", i, j, flush=True)
                frames.append(overpass_ways(bb))
    gdf = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs="EPSG:4326")
    gdf = gdf.drop_duplicates(subset=["osm_id"])
    gdf.to_file(cache_path, driver="GeoJSON")
    print("streets", len(gdf), "->", cache_path.name, flush=True)
    return gdf


def to_px(lon, lat, bounds, size):
    width, height = size
    west, south, east, north = bounds
    left, bottom = heat.lonlat_to_merc(west, south)
    right, top = heat.lonlat_to_merc(east, north)
    x, y = heat.lonlat_to_merc(lon, lat)
    px = (x - left) / (right - left) * (width - 1)
    py = (top - y) / (top - bottom) * (height - 1)
    return px, py


def line_pts(geom, bounds, size):
    geoms = [geom] if geom.geom_type == "LineString" else list(geom.geoms)
    out = []
    for g in geoms:
        out.append([to_px(x, y, bounds, size) for x, y in g.coords])
    return out


def rasterize_streets(gdf, bounds, size, width_scale=STREET_WIDTH_SCALE):
    img = Image.new("L", size, 0)
    draw = ImageDraw.Draw(img)
    for _, row in gdf.iterrows():
        width = max(1, int(round(LINE_WIDTH.get(row.get("highway"), 2) * width_scale)))
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        for pts in line_pts(geom, bounds, size):
            if len(pts) >= 2:
                draw.line(pts, fill=255, width=width)
    return np.array(img) > 0


def style_base(img):
    img = ImageEnhance.Color(img).enhance(0.88)
    img = ImageEnhance.Brightness(img).enhance(0.92)
    img = ImageEnhance.Contrast(img).enhance(1.08)
    return img


def add_label(ax, x, y, text):
    ax.text(
        x,
        y,
        text,
        color="white",
        fontsize=8,
        fontweight="bold",
        ha="center",
        va="center",
        zorder=6,
        bbox=dict(boxstyle="round,pad=0.28", facecolor="black", edgecolor="none", alpha=0.72),
    )


def save_phoenix(poster, bounds, title, outfile, heat_max, heat_abs_max, labels, scale_km, width_scale=STREET_WIDTH_SCALE):
    cmap = mcolors.LinearSegmentedColormap.from_list("burn", PALETTE)
    fig = plt.figure(figsize=(11.4, 12.6), facecolor="#050505")
    ax = fig.add_axes([0.03, 0.145, 0.94, 0.78])
    ax.imshow(poster)
    ax.set_axis_off()
    h, w = np.array(poster).shape[:2]
    for lon, lat, text in labels:
        x, y = to_px(lon, lat, bounds, (w, h))
        add_label(ax, x, y, text)
    heat.add_scale_north(ax, bounds, scale_km)
    fig.text(
        0.5,
        0.968,
        title,
        ha="center",
        va="top",
        color="white",
        fontsize=15,
        fontweight="bold",
        fontfamily="sans-serif",
    )
    fig.text(
        0.04,
        0.112,
        f"{heat.LST_SOURCE}\n{heat.PERIOD}  |  {heat.LST_HOURS}\n{heat.LST_FORMULA}\nCalles OSM; color solo sobre la red vial (alpha {STREET_ALPHA:.0%}; street width scale {width_scale:g}, original = 1)",
        ha="left",
        va="top",
        color="white",
        fontsize=7.5,
        linespacing=1.35,
        fontfamily="sans-serif",
    )
    sm = ScalarMappable(norm=mcolors.Normalize(THRESHOLD, heat_max), cmap=cmap)
    sm.set_array([])
    cax = fig.add_axes([0.30, 0.048, 0.40, 0.018])
    cbar = fig.colorbar(sm, cax=cax, orientation="horizontal")
    ticks = [THRESHOLD, (THRESHOLD + heat_max) / 2, heat_max]
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f"{THRESHOLD:.0f}\nModerado", f"{(THRESHOLD + heat_max) / 2:.0f}\nAlto", f"{heat_max:.0f}\nMuy alto"])
    cbar.ax.tick_params(colors="white", labelsize=7)
    cbar.outline.set_edgecolor("white")
    cbar.set_label("Temperatura de superficie en calles (°C)", color="white", fontsize=9, labelpad=10)
    fig.text(
        0.50,
        0.016,
        f"sin color < {THRESHOLD:.0f} °C   ·   máximo observado {heat_abs_max:.1f} °C",
        ha="center",
        color="#c8c8c8",
        fontsize=7.5,
    )
    fig.text(
        0.97,
        0.016,
        "Anaplian.com",
        ha="right",
        va="bottom",
        fontsize=13,
        fontweight="bold",
        color="#8d8d8d",
        alpha=0.88,
        fontfamily="sans-serif",
    )
    fig.savefig(outfile, dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("saved", outfile.name, flush=True)


def make_street_heat(clip_geom, bounds, zoom, lst, vis, streets, title, outfile, heat_max, heat_abs_max, labels, scale_km, outline_w=2, width_scale=STREET_WIDTH_SCALE):
    print("basemap", title, "z", zoom, "width_scale", width_scale, flush=True)
    base = style_base(heat.fetch_esri(bounds, zoom))
    width, height = heat.cap_size(*base.size, max_side=2000)
    if (width, height) != base.size:
        base = base.resize((width, height), Image.Resampling.LANCZOS)
    region = ee.Geometry.Rectangle(list(bounds), proj="EPSG:4326", geodesic=False)
    lst_img = heat.fetch_gee_rgb(lst.updateMask(lst.gt(THRESHOLD)).clip(ee.Geometry(clip_geom.__geo_interface__)), vis, region, width, height)
    lst_arr = np.array(lst_img.resize((width, height), Image.Resampling.BILINEAR))
    clipped = streets.clip(clip_geom)
    print("clipped streets", len(clipped), flush=True)
    street_mask = rasterize_streets(clipped, bounds, (width, height), width_scale=width_scale)
    hot = lst_arr.max(axis=2) > 18
    use = street_mask & hot
    composite = np.array(base)
    composite[use] = (
        (1.0 - STREET_ALPHA) * composite[use] + STREET_ALPHA * lst_arr[use]
    ).astype(np.uint8)
    poly_mask = np.array(heat.raster_mask(clip_geom, bounds, (width, height)))
    composite[poly_mask == 0] = (6, 6, 6)
    poster = heat.draw_outline(Image.fromarray(composite), clip_geom, bounds, width=outline_w)
    poster = poster.filter(ImageFilter.SMOOTH)
    save_phoenix(poster, bounds, title, outfile, heat_max, heat_abs_max, labels, scale_km, width_scale=width_scale)


alc = gpd.read_file(ROOT / "data/boundaries/cdmx_alcaldias/cdmx_alcaldias.shp", encoding="utf-8").to_crs("EPSG:4326")
izt = alc.loc[alc["alcaldia"].str.contains("Iztapalapa", case=False)].copy()
izt_geom = izt.geometry.union_all() if hasattr(izt.geometry, "union_all") else izt.unary_union
ceda = gpd.read_file(ROOT / "data/boundaries/central_de_abasto/central_de_abasto.geojson").to_crs("EPSG:4326")
ceda_geom = ceda.geometry.iloc[0]

izt_w, izt_s, izt_e, izt_n = izt.total_bounds
izt_bounds = (izt_w - 0.004, izt_s - 0.004, izt_e + 0.004, izt_n + 0.004)
ceda_w, ceda_s, ceda_e, ceda_n = ceda.total_bounds
ceda_bounds = (ceda_w - 0.0025, ceda_s - 0.0025, ceda_e + 0.0025, ceda_n + 0.0025)

ceda_streets = fetch_streets(ceda_bounds, CACHE / "central_de_abasto_highways.geojson", tiles=1)

print("Building Landsat LST...", flush=True)
region = ee.Geometry.Rectangle(list(ceda_bounds), proj="EPSG:4326", geodesic=False)
lst = (
    heat.load_lst("LANDSAT/LC08/C02/T1_L2", region)
    .merge(heat.load_lst("LANDSAT/LC09/C02/T1_L2", region))
    .mean()
)
ceda_stats = lst.updateMask(lst.gt(THRESHOLD)).reduceRegion(
    reducer=ee.Reducer.minMax().combine(ee.Reducer.percentile([98]), sharedInputs=True),
    geometry=ee.Geometry(ceda_geom.__geo_interface__),
    scale=30,
    maxPixels=1e8,
    bestEffort=True,
).getInfo()
print("CEDA hot stats", ceda_stats, flush=True)
ceda_abs = float(ceda_stats.get("ST_C_max") or 50.0)
ceda_max = float(ceda_stats.get("ST_C_p98") or ceda_abs)
ceda_max = max(THRESHOLD + 2.0, min(ceda_max, ceda_abs))
ceda_vis = {"min": THRESHOLD, "max": ceda_max, "palette": PALETTE}

ceda_pt = ceda_geom.centroid
make_street_heat(
    ceda_geom,
    ceda_bounds,
    16,
    lst,
    ceda_vis,
    ceda_streets,
    "Temperatura de superficie en calles — Central de Abasto",
    OUT / "central_de_abasto_street_heat.png",
    ceda_max,
    ceda_abs,
    labels=[(ceda_pt.x, ceda_pt.y, "Central de Abasto")],
    scale_km=1,
    outline_w=3,
    width_scale=CEDA_STREET_WIDTH_SCALE,
)
print("done Central de Abasto street width scale", CEDA_STREET_WIDTH_SCALE, "(original = 1)", flush=True)
