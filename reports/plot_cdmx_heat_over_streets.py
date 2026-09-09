"""LST > 38 C transparent overlay on satellite streets: CDMX and each alcaldia."""
from __future__ import annotations

import io
import math
import re
import unicodedata
from pathlib import Path

import ee
import geemap
import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import requests
from matplotlib.cm import ScalarMappable
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "cdmx_heat_islands" / "heat_over_streets_35c"
FIG.mkdir(parents=True, exist_ok=True)

ee.Initialize(project="ee-my-usenvdi")

START, END = "2026-04-01", "2026-06-01"
PERIOD = "Apr–May 2026"
LST_HOURS = "~10:30 local (16:30 UTC)"
LST_FORMULA = "LST = 0.00341802×DN + 149 − 273.15 (°C)"
LST_SOURCE = "USGS Landsat 8/9 Collection 2 Level-2 ST_B10"
THRESHOLD = 35.0
NAME_TAG = "_35c"
HEAT_ALPHA = 0.55
HEAT_PALETTE = ["#f6c445", "#f08c2b", "#e31a1c", "#9b0d0d"]
ESRI_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
CITY_PAD = 0.012
ALC_PAD = 0.004
MERC = 20037508.342789244
SESSION = requests.Session()
TILE_CACHE: dict[tuple[int, int, int], Image.Image] = {}


def slug(name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_name = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", ascii_name.lower()).strip("_")


def cloud_mask(image):
    qa = image.select("QA_PIXEL")
    fill = qa.bitwiseAnd(1)
    cloud = qa.bitwiseAnd(1 << 3).Or(qa.bitwiseAnd(1 << 4))
    return image.updateMask(fill.Or(cloud).Not())


def prep_lst(image):
    st = image.select("ST_B10").multiply(0.00341802).add(149.0).subtract(273.15).rename("ST_C")
    valid = st.gt(0.0).And(st.lt(80.0))
    return cloud_mask(image).addBands(st, None, True).select("ST_C").updateMask(valid)


def load_lst(cid, bounds_geom):
    return (
        ee.ImageCollection(cid)
        .filterBounds(bounds_geom)
        .filterDate(START, END)
        .filter(ee.Filter.lt("CLOUD_COVER", 80))
        .map(prep_lst)
    )


def lonlat_to_merc(lon, lat):
    x = lon * MERC / 180.0
    y = math.log(math.tan((90.0 + lat) * math.pi / 360.0)) * MERC / math.pi
    return x, y


def deg2num(lat, lon, zoom):
    lat_rad = math.radians(lat)
    n = 2.0**zoom
    xtile = (lon + 180.0) / 360.0 * n
    ytile = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    return xtile, ytile


def tile_merc_bounds(x, y, zoom):
    n = 2.0**zoom
    west = x / n * (2 * MERC) - MERC
    east = (x + 1) / n * (2 * MERC) - MERC
    north = MERC - y / n * (2 * MERC)
    south = MERC - (y + 1) / n * (2 * MERC)
    return west, south, east, north


def span_km(bounds):
    west, south, east, north = bounds
    lat = 0.5 * (south + north)
    width_km = abs(east - west) * 111.32 * math.cos(math.radians(lat))
    height_km = abs(north - south) * 110.57
    return width_km, height_km, max(width_km, height_km)


def zoom_for(bounds):
    span = span_km(bounds)[2]
    if span >= 25:
        return 13
    if span >= 14:
        return 14
    if span >= 8:
        return 15
    return 16


def scale_km_length(bounds):
    width_km = span_km(bounds)[0]
    if width_km >= 25:
        return 5
    if width_km >= 10:
        return 2
    return 1


def fetch_esri(bounds, zoom):
    west, south, east, north = bounds
    x0, y_north = deg2num(north, west, zoom)
    x1, y_south = deg2num(south, east, zoom)
    xmin, xmax = int(math.floor(min(x0, x1))), int(math.floor(max(x0, x1)))
    ymin, ymax = int(math.floor(min(y_north, y_south))), int(math.floor(max(y_north, y_south)))
    tile_w = tile_h = 256
    mosaic = Image.new("RGB", ((xmax - xmin + 1) * tile_w, (ymax - ymin + 1) * tile_h), (8, 8, 8))
    for ty in range(ymin, ymax + 1):
        for tx in range(xmin, xmax + 1):
            key = (zoom, tx, ty)
            tile = TILE_CACHE.get(key)
            if tile is None:
                url = ESRI_URL.format(z=zoom, y=ty, x=tx)
                try:
                    r = SESSION.get(url, timeout=40)
                    r.raise_for_status()
                    tile = Image.open(io.BytesIO(r.content)).convert("RGB")
                except Exception:
                    tile = Image.new("RGB", (tile_w, tile_h), (12, 12, 12))
                TILE_CACHE[key] = tile
            mosaic.paste(tile, ((tx - xmin) * tile_w, (ty - ymin) * tile_h))
    mw, _, _, mn = tile_merc_bounds(xmin, ymin, zoom)
    _, ms, me, _ = tile_merc_bounds(xmax, ymax, zoom)
    left_m, bottom_m = lonlat_to_merc(west, south)
    right_m, top_m = lonlat_to_merc(east, north)
    px0 = (left_m - mw) / (me - mw) * mosaic.width
    px1 = (right_m - mw) / (me - mw) * mosaic.width
    py0 = (mn - top_m) / (mn - ms) * mosaic.height
    py1 = (mn - bottom_m) / (mn - ms) * mosaic.height
    box = (
        int(max(0, min(px0, px1))),
        int(max(0, min(py0, py1))),
        int(min(mosaic.width, math.ceil(max(px0, px1)))),
        int(min(mosaic.height, math.ceil(max(py0, py1)))),
    )
    return mosaic.crop(box).convert("RGB")


def cap_size(width, height, max_side=1800, max_pixels=7_500_000):
    scale = min(1.0, max_side / max(width, height), math.sqrt(max_pixels / max(1, width * height)))
    return max(64, int(width * scale)), max(64, int(height * scale))


def fetch_gee_rgb(image, vis, region, width, height):
    url = image.visualize(**vis).getThumbURL(
        {
            "region": region,
            "crs": "EPSG:3857",
            "dimensions": f"{width}x{height}",
            "format": "png",
        }
    )
    return Image.open(io.BytesIO(SESSION.get(url, timeout=180).content)).convert("RGB")


def raster_mask(geom, bounds, size):
    width, height = size
    west, south, east, north = bounds
    left, bottom = lonlat_to_merc(west, south)
    right, top = lonlat_to_merc(east, north)
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    geoms = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)

    def to_px(coords):
        pts = []
        for lon, lat in coords:
            x, y = lonlat_to_merc(lon, lat)
            px = (x - left) / (right - left) * (width - 1)
            py = (top - y) / (top - bottom) * (height - 1)
            pts.append((px, py))
        return pts

    for poly in geoms:
        draw.polygon(to_px(poly.exterior.coords), fill=255)
        for hole in poly.interiors:
            draw.polygon(to_px(hole.coords), fill=0)
    return mask


def draw_outline(img, geom, bounds, width=3, fill=(255, 255, 255)):
    out = img.convert("RGBA")
    overlay = Image.new("RGBA", out.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    west, south, east, north = bounds
    left, bottom = lonlat_to_merc(west, south)
    right, top = lonlat_to_merc(east, north)
    geoms = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)

    def to_px(coords):
        pts = []
        for lon, lat in coords:
            x, y = lonlat_to_merc(lon, lat)
            px = (x - left) / (right - left) * (out.width - 1)
            py = (top - y) / (top - bottom) * (out.height - 1)
            pts.append((px, py))
        return pts

    for poly in geoms:
        draw.line(to_px(list(poly.exterior.coords)), fill=fill + (255,), width=width)
    return Image.alpha_composite(out, overlay).convert("RGB")


def add_scale_north(ax, bounds, km):
    width_km = span_km(bounds)[0]
    frac = km / width_km if width_km else 0.2
    x0, x1 = 0.72, 0.72 + min(frac, 0.22)
    y = 0.07
    ax.plot([x0, x1], [y, y], transform=ax.transAxes, color="white", lw=2.4, solid_capstyle="butt")
    ax.plot([x0, x0], [y - 0.008, y + 0.008], transform=ax.transAxes, color="white", lw=1.4)
    ax.plot([x1, x1], [y - 0.008, y + 0.008], transform=ax.transAxes, color="white", lw=1.4)
    ax.text((x0 + x1) / 2, y + 0.028, f"{km} km", transform=ax.transAxes, ha="center", color="white", fontsize=8)
    ax.annotate(
        "N",
        xy=(0.93, 0.11),
        xytext=(0.93, 0.20),
        xycoords="axes fraction",
        ha="center",
        va="bottom",
        fontsize=8,
        fontweight="bold",
        color="white",
        arrowprops=dict(arrowstyle="-|>", color="white", lw=1.1),
    )


def style_base(img):
    img = ImageEnhance.Color(img).enhance(0.45)
    img = ImageEnhance.Brightness(img).enhance(0.62)
    img = ImageEnhance.Contrast(img).enhance(1.18)
    return img


def compose_overlay(base_arr, heat_arr):
    heat_arr = np.array(Image.fromarray(heat_arr).resize((base_arr.shape[1], base_arr.shape[0]), Image.Resampling.BILINEAR))
    hot_mask = heat_arr.max(axis=2) > 18
    out = base_arr.copy()
    out[hot_mask] = ((1.0 - HEAT_ALPHA) * base_arr[hot_mask] + HEAT_ALPHA * heat_arr[hot_mask]).astype(np.uint8)
    return out


def save_poster(
    poster,
    bounds,
    title,
    outfile,
    heat_max,
    heat_abs_max,
    figsize=(11.2, 12.4),
    year=None,
    watermark_size=13,
    overlay_caption=None,
    cbar_label="Land Surface Temperature (°C)",
    footer=None,
    palette=None,
):
    pal = palette or HEAT_PALETTE
    cmap = mcolors.LinearSegmentedColormap.from_list("overlay", pal)
    fig = plt.figure(figsize=figsize, facecolor="#050505")
    ax = fig.add_axes([0.035, 0.145, 0.93, 0.78])
    ax.imshow(poster)
    ax.set_axis_off()
    for sp in ax.spines.values():
        sp.set_visible(False)
    add_scale_north(ax, bounds, scale_km_length(bounds))
    fig.text(
        0.5,
        0.965,
        title,
        ha="center",
        va="top",
        color="white",
        fontsize=16 if len(title) > 40 else 18,
        fontweight="bold",
        fontfamily="sans-serif",
    )
    if year is not None:
        ax.text(
            0.04,
            0.96,
            str(year),
            transform=ax.transAxes,
            ha="left",
            va="top",
            color="white",
            fontsize=36,
            fontweight="bold",
            fontfamily="sans-serif",
            alpha=0.95,
        )
    caption = overlay_caption or (
        f"{LST_SOURCE}\n{PERIOD}  |  {LST_HOURS}\n{LST_FORMULA}\n"
        f"Overlay: surface temperature > {THRESHOLD:.0f} °C"
    )
    fig.text(
        0.04,
        0.108,
        caption,
        ha="left",
        va="top",
        color="white",
        fontsize=7.5,
        linespacing=1.35,
        fontfamily="sans-serif",
    )
    sm = ScalarMappable(norm=mcolors.Normalize(THRESHOLD, heat_max), cmap=cmap)
    sm.set_array([])
    cax = fig.add_axes([0.33, 0.055, 0.34, 0.018])
    cbar = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cbar.set_ticks([THRESHOLD, heat_max])
    cbar.set_ticklabels([f"{THRESHOLD:.0f}", f"{heat_max:.0f}"])
    cbar.ax.tick_params(colors="white", labelsize=8)
    cbar.outline.set_edgecolor("white")
    cbar.set_label(cbar_label, color="white", fontsize=9, labelpad=6)
    fig.text(
        0.50,
        0.028,
        footer or f"min {THRESHOLD:.0f}   ·   observed max {heat_abs_max:.1f} °C",
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
        fontsize=watermark_size,
        fontweight="bold",
        color="#c4c4c4",
        alpha=0.95,
        fontfamily="sans-serif",
    )
    fig.savefig(outfile, dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("saved", outfile.name, flush=True)


def make_map(
    clip_geom,
    bounds,
    zoom,
    hot,
    vis,
    title,
    outfile,
    heat_max,
    heat_abs_max,
    outline_w=3,
    year=None,
    watermark_size=13,
    overlay_caption=None,
    cbar_label="Land Surface Temperature (°C)",
    footer=None,
    palette=None,
):
    print(f"basemap {title} z{zoom}", flush=True)
    base = style_base(fetch_esri(bounds, zoom))
    width, height = cap_size(*base.size)
    if (width, height) != base.size:
        base = base.resize((width, height), Image.Resampling.LANCZOS)
    region = ee.Geometry.Rectangle(list(bounds), proj="EPSG:4326", geodesic=False)
    heat_img = fetch_gee_rgb(hot.clip(ee.Geometry(clip_geom.__geo_interface__)), vis, region, width, height)
    composite = compose_overlay(np.array(base), np.array(heat_img))
    mask = np.array(raster_mask(clip_geom, bounds, (width, height)))
    composite[mask == 0] = (6, 6, 6)
    poster = draw_outline(Image.fromarray(composite), clip_geom, bounds, width=outline_w)
    poster = poster.filter(ImageFilter.SMOOTH)
    save_poster(
        poster,
        bounds,
        title,
        outfile,
        heat_max,
        heat_abs_max,
        year=year,
        watermark_size=watermark_size,
        overlay_caption=overlay_caption,
        cbar_label=cbar_label,
        footer=footer,
        palette=palette or vis.get("palette"),
    )


if __name__ == "__main__":
    city_gdf = gpd.read_file(ROOT / "data/boundaries/ciudad_de_mexico/ciudad_de_mexico.shp").to_crs("EPSG:4326")
    alc_gdf = gpd.read_file(ROOT / "data/boundaries/cdmx_alcaldias/cdmx_alcaldias.shp", encoding="utf-8").to_crs("EPSG:4326")
    if "alcaldia" not in alc_gdf.columns:
        alc_gdf["alcaldia"] = alc_gdf["shapeName"]
    city_geom = city_gdf.geometry.union_all() if hasattr(city_gdf.geometry, "union_all") else city_gdf.unary_union
    city_fc = geemap.geopandas_to_ee(city_gdf)
    aoi = city_fc.geometry()
    west, south, east, north = city_gdf.total_bounds
    city_bounds = (west - CITY_PAD, south - CITY_PAD, east + CITY_PAD, north + CITY_PAD)
    city_region = ee.Geometry.Rectangle(list(city_bounds), proj="EPSG:4326", geodesic=False)

    print("Building Landsat LST composite...", flush=True)
    lst = (
        load_lst("LANDSAT/LC08/C02/T1_L2", city_region)
        .merge(load_lst("LANDSAT/LC09/C02/T1_L2", city_region))
        .mean()
        .clip(aoi)
    )
    stats = lst.updateMask(lst.gt(THRESHOLD)).reduceRegion(
        reducer=ee.Reducer.minMax().combine(ee.Reducer.percentile([98]), sharedInputs=True),
        geometry=aoi,
        scale=100,
        maxPixels=1e8,
        bestEffort=True,
    ).getInfo()
    print("hot stats", stats, flush=True)
    heat_abs_max = float(stats.get("ST_C_max") or 50.0)
    heat_max = float(stats.get("ST_C_p98") or heat_abs_max)
    heat_max = max(THRESHOLD + 2.0, min(heat_max, heat_abs_max))
    hot = lst.updateMask(lst.gt(THRESHOLD))
    vis = {"min": THRESHOLD, "max": heat_max, "palette": HEAT_PALETTE}

    make_map(
        city_geom,
        city_bounds,
        13,
        hot,
        vis,
        "Urban Heat Islands in Ciudad de México",
        FIG / f"cdmx_heat_over_streets{NAME_TAG}.png",
        heat_max,
        heat_abs_max,
        outline_w=3,
    )

    for _, row in alc_gdf.sort_values("alcaldia").iterrows():
        name = row["alcaldia"]
        geom = row.geometry
        w, s, e, n = geom.bounds
        bounds = (w - ALC_PAD, s - ALC_PAD, e + ALC_PAD, n + ALC_PAD)
        make_map(
            geom,
            bounds,
            zoom_for(bounds),
            hot,
            vis,
            f"Urban Heat Islands in {name}",
            FIG / f"{slug(name)}_heat_over_streets{NAME_TAG}.png",
            heat_max,
            heat_abs_max,
            outline_w=2,
        )

    print("done", flush=True)
