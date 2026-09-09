"""Heat overlay for Central de Abasto (CEDA), Iztapalapa."""
from __future__ import annotations

import sys
from pathlib import Path

import ee
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import plot_cdmx_heat_over_streets as heat  # noqa: E402

CEDA = ROOT / "data/boundaries/central_de_abasto/central_de_abasto.geojson"
PAD = 0.0025


def run_one(threshold: float, outfile: Path, lst, geom, bounds, heat_abs_max_city=None):
    heat.THRESHOLD = threshold
    stats = lst.updateMask(lst.gt(threshold)).reduceRegion(
        reducer=ee.Reducer.minMax().combine(ee.Reducer.percentile([98]), sharedInputs=True),
        geometry=ee.Geometry(geom.__geo_interface__),
        scale=30,
        maxPixels=1e8,
        bestEffort=True,
    ).getInfo()
    print("CEDA stats", threshold, stats, flush=True)
    heat_abs_max = float(stats.get("ST_C_max") or heat_abs_max_city or 50.0)
    heat_max = float(stats.get("ST_C_p98") or heat_abs_max)
    heat_max = max(threshold + 2.0, min(heat_max, heat_abs_max))
    hot = lst.updateMask(lst.gt(threshold))
    vis = {"min": threshold, "max": heat_max, "palette": heat.HEAT_PALETTE}
    outfile.parent.mkdir(parents=True, exist_ok=True)
    heat.make_map(
        geom,
        bounds,
        heat.zoom_for(bounds),
        hot,
        vis,
        "Urban Heat Islands in Central de Abasto",
        outfile,
        heat_max,
        heat_abs_max,
        outline_w=3,
    )


gdf = gpd.read_file(CEDA).to_crs("EPSG:4326")
geom = gdf.geometry.iloc[0]
w, s, e, n = geom.bounds
bounds = (w - PAD, s - PAD, e + PAD, n + PAD)
region = ee.Geometry.Rectangle(list(bounds), proj="EPSG:4326", geodesic=False)

print("Building Landsat LST around Central de Abasto...", flush=True)
lst = (
    heat.load_lst("LANDSAT/LC08/C02/T1_L2", region)
    .merge(heat.load_lst("LANDSAT/LC09/C02/T1_L2", region))
    .mean()
    .clip(ee.Geometry(geom.__geo_interface__))
)

run_one(
    38.0,
    ROOT / "reports/cdmx_heat_islands/figures/central_de_abasto_heat_over_streets.png",
    lst,
    geom,
    bounds,
)
run_one(
    35.0,
    ROOT / "reports/cdmx_heat_islands/heat_over_streets_35c/central_de_abasto_heat_over_streets_35c.png",
    lst,
    geom,
    bounds,
)
print("done", flush=True)
