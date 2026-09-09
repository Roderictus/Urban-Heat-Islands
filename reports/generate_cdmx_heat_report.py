"""Generate CDMX heat-island report for April-May 2026."""
from __future__ import annotations

import json
import re
import unicodedata
from io import BytesIO
from pathlib import Path

import ee
import geemap
import geopandas as gpd
import pandas as pd
import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "cdmx_heat_islands"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

ee.Initialize(project="ee-my-usenvdi")

START, END = "2026-04-01", "2026-06-01"
LST_VIS = {"min": 24, "max": 48, "palette": ["#2166ac", "#67a9cf", "#d1e5f0", "#ffffbf", "#fdae61", "#d7191c"]}
AIR_VIS = {"min": 12, "max": 32, "palette": ["#313695", "#74add1", "#ffffbf", "#f46d43", "#a50026"]}
NIGHT_VIS = {"min": 8, "max": 28, "palette": ["#313695", "#74add1", "#ffffbf", "#f46d43", "#a50026"]}


def slug(name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_name = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", ascii_name.lower()).strip("_")


def gdf_union(gdf):
    geom = gdf.geometry
    return geom.union_all() if hasattr(geom, "union_all") else geom.unary_union


def cloud_mask(image):
    qa = image.select("QA_PIXEL")
    mask = qa.bitwiseAnd(1 << 3).Or(qa.bitwiseAnd(1 << 4))
    return image.updateMask(mask.Not())


def apply_st(image):
    thermal = image.select("ST_B10").multiply(0.00341802).add(149.0).subtract(273.15).rename("ST_C")
    return image.addBands(thermal, None, True)


def save_thumb(image, vis, region, path, dimensions=900, extra=None):
    vis_img = image.visualize(**vis)
    if extra is not None:
        vis_img = vis_img.blend(extra)
    url = vis_img.getThumbURL({"region": region, "dimensions": dimensions, "format": "png"})
    img = Image.open(BytesIO(requests.get(url, timeout=180).content)).convert("RGBA")
    img.save(path)
    print("saved", path.name, img.size)
    return img


def load_roads(city_gdf, aoi_bounds):
    try:
        url = "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_roads.zip"
        print("Downloading Natural Earth roads...", flush=True)
        gdf = gpd.read_file(url).to_crs("EPSG:4326")
        clipped = gdf.clip(city_gdf)
        print("NE roads in CDMX", len(clipped), flush=True)
        if len(clipped):
            return geemap.geopandas_to_ee(clipped[["geometry"]])
    except Exception as exc:
        print("Natural Earth roads failed:", exc, flush=True)
    return ee.FeatureCollection([])


def lst_to_celsius(image):
    """Handle Kelvin, already-Celsius, or 0.02-scaled Kelvin."""
    p50 = image.reduceRegion(
        ee.Reducer.percentile([50]), image.geometry(), 200, maxPixels=1e8, bestEffort=True
    )
    # p50 keys depend on band name; compute on a known sample instead in caller
    return image, p50


# --- geometries ---
city_gdf = gpd.read_file(ROOT / "data/boundaries/ciudad_de_mexico/ciudad_de_mexico.shp").to_crs("EPSG:4326")
alc_gdf = gpd.read_file(ROOT / "data/boundaries/cdmx_alcaldias/cdmx_alcaldias.shp", encoding="utf-8").to_crs("EPSG:4326")
if "alcaldia" not in alc_gdf.columns:
    alc_gdf["alcaldia"] = alc_gdf["shapeName"]
city_fc = geemap.geopandas_to_ee(city_gdf)
alc_fc = geemap.geopandas_to_ee(alc_gdf[["alcaldia", "geometry"]])
aoi = city_fc.geometry()
aoi_bounds = aoi.bounds()

roads_fc = load_roads(city_gdf, aoi_bounds)
roads_layer = ee.Image().paint(roads_fc, 1, 1).visualize(palette=["ffffff"], min=0, max=1)
outline = ee.Image().paint(alc_fc, 1, 1).visualize(palette=["000000"], min=0, max=1)

# --- Landsat surface ---
def load_l(cid):
    return (
        ee.ImageCollection(cid)
        .select(["ST_B10", "QA_PIXEL"])
        .filterBounds(aoi_bounds)
        .filterDate(START, END)
        .filter(ee.Filter.lt("CLOUD_COVER", 80))
        .map(cloud_mask)
        .map(apply_st)
        .select("ST_C")
    )


landsat = load_l("LANDSAT/LC08/C02/T1_L2").merge(load_l("LANDSAT/LC09/C02/T1_L2"))
n_landsat = landsat.size().getInfo()
print("Landsat scenes", n_landsat, flush=True)
lst_mean = landsat.mean().clip(aoi)
lst_max = landsat.max().clip(aoi)

smod = ee.Image("JRC/GHSL/P2023A/GHS_SMOD_V2-0/2020").select("smod_code").clip(aoi)
rural_mask = smod.eq(13).Or(smod.eq(12)).Or(smod.eq(11))
t_rural = lst_mean.updateMask(smod.neq(10)).updateMask(rural_mask).reduceRegion(
    ee.Reducer.mean(), aoi, 30, maxPixels=1e9, bestEffort=True
).getInfo()["ST_C"]
print("T_rural", t_rural)

# --- ERA5 air ---
era5 = (
    ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
    .filterBounds(aoi_bounds)
    .filterDate(START, END)
    .select(["temperature_2m_max", "temperature_2m"])
)
air_max = era5.select("temperature_2m_max").mean().subtract(273.15).rename("Tair").clip(aoi)
air_mean = era5.select("temperature_2m").mean().subtract(273.15).rename("Tair").clip(aoi)

# --- ECOSTRESS (night-dominated over CDMX; used as 70 m atmospheric-adjacent surface) ---
def prep_eco(image):
    lst = image.select("LST")
    qa_mask = image.select("QC").bitwiseAnd(3).lt(2)
    cloud_ok = image.select("cloud").eq(0)
    return lst.updateMask(qa_mask).updateMask(cloud_ok).rename("ECO").copyProperties(image, ["system:time_start"])


eco_raw = (
    ee.ImageCollection("NASA/ECOSTRESS/L2T_LSTE/V2")
    .filterBounds(aoi.centroid())
    .filterDate(START, END)
    .map(prep_eco)
)
n_eco = eco_raw.size().getInfo()
print("ECOSTRESS scenes", n_eco)
eco_mean = None
if n_eco:
    eco_mean = eco_raw.mean().clip(aoi)
    sample = eco_mean.reduceRegion(
        ee.Reducer.percentile([50]), aoi, 200, maxPixels=1e8, bestEffort=True
    ).getInfo()
    p50 = sample.get("ECO")
    print("ECOSTRESS p50", p50)
    if p50 is not None and p50 > 200:
        eco_mean = eco_mean.subtract(273.15)
    elif p50 is not None and p50 < 50:
        # already C or double-scaled; if < 8 treat as 0.02 * Kelvin
        if p50 < 10:
            eco_mean = eco_mean.multiply(50)  # 0.02 applied twice -> undo one: wait
            # 308*0.02=6.16; if p50~6, values are Kelvin*0.02, so /0.02 then -273
            eco_mean = eco_mean.divide(0.02).subtract(273.15)

# --- zonal stats ---
lst_stats = lst_mean.addBands(lst_max.rename("ST_max")).reduceRegions(
    collection=alc_fc,
    reducer=ee.Reducer.mean().combine(ee.Reducer.max(), sharedInputs=False).combine(ee.Reducer.count(), sharedInputs=True),
    scale=30,
)
# mean reducer on 2 bands -> ST_C_mean, ST_max_mean which is wrong for max band.
# Do two reduceRegions instead.
mean_fc = lst_mean.reduceRegions(alc_fc, ee.Reducer.mean().combine(ee.Reducer.count(), sharedInputs=True).combine(ee.Reducer.minMax(), sharedInputs=True), 30)
max_fc = lst_max.reduceRegions(alc_fc, ee.Reducer.max(), 30)
air_fc = air_mean.addBands(air_max.rename("Tair_max")).reduceRegions(
    alc_fc,
    ee.Reducer.mean(),
    9000,
)
mean_df = geemap.ee_to_df(mean_fc)
max_df = geemap.ee_to_df(max_fc)
air_df = geemap.ee_to_df(air_fc)

print("mean cols", list(mean_df.columns), flush=True)
print("max cols", list(max_df.columns), flush=True)
print("air cols", list(air_df.columns), flush=True)
max_col = "lst_peak_C" if "lst_peak_C" in max_df.columns else [c for c in max_df.columns if c != "alcaldia"][0]
if max_col != "lst_peak_C":
    max_df = max_df.rename(columns={max_col: "lst_peak_C"})
if "Tair" in air_df.columns:
    air_df = air_df.rename(columns={"Tair": "tair_mean_C"})
if "Tair_max" in air_df.columns:
    air_df = air_df.rename(columns={"Tair_max": "tair_max_C"})
mean_rename = {}
if "mean" in mean_df.columns:
    mean_rename["mean"] = "lst_mean_C"
if "ST_C" in mean_df.columns:
    mean_rename["ST_C"] = "lst_mean_C"
if "min" in mean_df.columns:
    mean_rename["min"] = "lst_min_C"
if "max" in mean_df.columns:
    mean_rename["max"] = "lst_max_in_mean"
if "count" in mean_df.columns:
    mean_rename["count"] = "n_pixels"
df = mean_df.rename(columns=mean_rename)
if "lst_mean_C" not in df.columns and "ST_C_mean" in df.columns:
    df = df.rename(columns={"ST_C_mean": "lst_mean_C", "ST_C_min": "lst_min_C", "ST_C_count": "n_pixels"})
df = df.merge(max_df[["alcaldia", "lst_peak_C"]], on="alcaldia")
air_keep = [c for c in ["alcaldia", "tair_mean_C", "tair_max_C"] if c in air_df.columns]
df = df.merge(air_df[air_keep], on="alcaldia")
df["suhi_C"] = df["lst_mean_C"] - t_rural
df["internal_range_C"] = df["lst_peak_C"] - df["lst_min_C"]
df = df.sort_values("suhi_C", ascending=False).reset_index(drop=True)
df["slug"] = df["alcaldia"].map(slug)
print(df[["alcaldia", "lst_peak_C", "lst_mean_C", "suhi_C", "tair_max_C"]].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# --- city images ---
city_surface = save_thumb(
    lst_mean, LST_VIS, aoi, FIG / "city_surface_roads.png", 1000, extra=roads_layer.blend(outline)
)
if eco_mean is not None:
    city_atm = save_thumb(eco_mean, NIGHT_VIS, aoi, FIG / "city_atmospheric.png", 1000, extra=outline)
    atm_img = eco_mean
    atm_vis = NIGHT_VIS
    atm_label = "ECOSTRESS night-dominated LST (C)"
else:
    city_atm = save_thumb(air_max, AIR_VIS, aoi, FIG / "city_atmospheric.png", 1000, extra=outline)
    atm_img = air_max
    atm_vis = AIR_VIS
    atm_label = "ERA5-Land 2 m air temperature, mean of daily maxima (C)"

# --- per alcaldia ---
profiles = []
for _, row in df.iterrows():
    name = row["alcaldia"]
    feat = alc_fc.filter(ee.Filter.eq("alcaldia", name)).first()
    geom = ee.Feature(feat).geometry()
    s_path = FIG / f"{row['slug']}_surface_roads.png"
    a_path = FIG / f"{row['slug']}_atmospheric.png"
    save_thumb(lst_mean.clip(geom), LST_VIS, geom, s_path, 640, extra=roads_layer)
    save_thumb(atm_img.clip(geom), atm_vis, geom, a_path, 640)
    profiles.append(
        {
            "alcaldia": name,
            "slug": row["slug"],
            "lst_peak_C": round(float(row["lst_peak_C"]), 2),
            "lst_mean_C": round(float(row["lst_mean_C"]), 2),
            "lst_min_C": round(float(row["lst_min_C"]), 2),
            "suhi_C": round(float(row["suhi_C"]), 2),
            "internal_range_C": round(float(row["internal_range_C"]), 2),
            "tair_mean_C": round(float(row["tair_max_C"] and row["tair_mean_C"]), 2),
            "tair_max_C": round(float(row["tair_max_C"]), 2),
            "n_pixels": int(row["n_pixels"]),
            "surface_img": f"figures/{s_path.name}",
            "atm_img": f"figures/{a_path.name}",
        }
    )

meta = {
    "title": "Mexico City heat islands",
    "window": "1 April – 31 May 2026",
    "n_landsat": n_landsat,
    "n_ecostress": n_eco,
    "t_rural": round(float(t_rural), 2),
    "city_suhi": round(float(df["lst_mean_C"].mean() - t_rural), 2),
    "hottest": profiles[0]["alcaldia"],
    "coolest": profiles[-1]["alcaldia"],
    "atm_label": atm_label,
    "surface_label": "Landsat 8/9 Collection 2 surface temperature, mean of clear-sky scenes (C)",
    "profiles": profiles,
}
(OUT / "profiles.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
pd.DataFrame(profiles).to_csv(OUT / "profiles.csv", index=False)

cards = []
for p in profiles:
    cards.append(
        f"""
        <section class="card">
          <h2>{p['alcaldia']}</h2>
          <ul class="stats">
            <li><b>Greatest surface temperature</b> {p['lst_peak_C']:.1f} C</li>
            <li><b>Average surface temperature</b> {p['lst_mean_C']:.1f} C</li>
            <li><b>Highest difference vs rural CDMX</b> {p['suhi_C']:+.1f} C</li>
            <li><b>Air temperature (ERA5 2 m max)</b> {p['tair_max_C']:.1f} C</li>
          </ul>
          <div class="pair">
            <figure>
              <img src="{p['surface_img']}" alt="Surface heat with roads, {p['alcaldia']}">
              <figcaption>Surface heat (Landsat LST) with major roads</figcaption>
            </figure>
            <figure>
              <img src="{p['atm_img']}" alt="Atmospheric heat, {p['alcaldia']}">
              <figcaption>{meta['atm_label']}</figcaption>
            </figure>
          </div>
        </section>
        """
    )

html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Mexico City heat islands — April–May 2026</title>
  <style>
    body {{ font-family: Georgia, serif; max-width: 1100px; margin: 32px auto; color: #1a1a1a; }}
    h1, h2 {{ font-family: Helvetica, Arial, sans-serif; }}
    .hero img {{ width: 100%; }}
    .pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    img {{ width: 100%; background: #111; }}
    .stats {{ padding-left: 18px; }}
    .card {{ border-top: 1px solid #ddd; padding-top: 24px; margin-top: 24px; }}
    figcaption {{ font-size: 0.85rem; color: #555; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 0.92rem; }}
    th, td {{ border: 1px solid #ddd; padding: 6px 8px; text-align: right; }}
    th:first-child, td:first-child {{ text-align: left; }}
  </style>
</head>
<body>
  <h1>Mexico City heat islands</h1>
  <p>Comparable window: <b>1 April – 31 May 2026</b> (late dry season). July 2026 was tested and rejected for a citywide map because of monsoon cloud gaps.</p>
  <p>Surface heat is Landsat 8/9 Collection 2 land-surface temperature ({n_landsat} scenes, pixel cloud mask). Difference is alcaldía mean LST minus GHSL rural mean in CDMX ({t_rural:.1f} C), mostly the southern conservation land. Atmospheric heat uses ERA5-Land 2 m air temperature; where ECOSTRESS is available it is shown as a 70 m night-dominated surface that tracks air temperature more closely than daytime LST.</p>
  <section class="hero">
    <h2>All Mexico City — surface heat</h2>
    <img src="figures/city_surface_roads.png" alt="CDMX Landsat surface temperature with roads">
    <h2>All Mexico City — atmospheric heat</h2>
    <img src="figures/city_atmospheric.png" alt="CDMX atmospheric heat">
  </section>
  {''.join(cards)}
</body>
</html>
"""
(OUT / "report.html").write_text(html, encoding="utf-8")
print("wrote", OUT / "report.html", flush=True)
print("done", flush=True)
