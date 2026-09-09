"""Compare three ways to stabilize the CDMX April–May heat-island timelapse.

1. Pixel-mean composite of all Landsat 8/9 scenes with CLOUD_COVER < 80,
   overlay LST > 35 °C.
2. Same window, but overlay the rural differential (SUHI = LST − T_rural).
3. Both: pixel-mean of all April–May scenes (pixel cloud mask only, no
   scene-level 80% cut) plus SUHI overlay.

    python reports/plot_cdmx_heat_methods.py
    python reports/plot_cdmx_heat_methods.py --inventory-only
    python reports/plot_cdmx_heat_methods.py --lst-cut 35 --suhi-cut 10
    python reports/plot_cdmx_heat_methods.py --skip-lst --suhi-cut 10
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import ee
import geemap
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reports"))
import plot_cdmx_heat_over_streets as heat  # noqa: E402
from plot_cdmx_heat_timelapse import try_mp4, write_gif, year_window  # noqa: E402

START_YEAR, END_YEAR = 2013, 2026

# --- cortes: cámbialos aquí o con --lst-cut / --suhi-cut ---
LST_CUT = 35.0    # °C  temperatura absoluta (amarillo–rojo)
SUHI_CUT = 10.0   # °C  diferencial urbano − rural (cian–ámbar)

LST_SCALE_MAX = 48.0
SUHI_SCALE_MAX = 18.0
# Cian → ámbar: se lee sobre el basemap oscuro y no se confunde con el LST amarillo–rojo.
SUHI_PALETTE = ["#22d3ee", "#38bdf8", "#fbbf24", "#f97316", "#c2410c"]
WATERMARK_SIZE = 26
CLOUD_COMPOSITE = 80
OUT = ROOT / "reports" / "cdmx_heat_islands" / "timelapse_methods"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--lst-cut", type=float, default=LST_CUT, help="Corte LST absoluta en °C")
    p.add_argument("--suhi-cut", type=float, default=SUHI_CUT, help="Corte SUHI (urbano−rural) en °C")
    p.add_argument("--skip-lst", action="store_true", help="Solo mapas SUHI (métodos 2 y 3)")
    p.add_argument("--reuse-inventory", action="store_true", help="Reusar inventory.json si existe")
    p.add_argument("--inventory-only", action="store_true")
    return p.parse_args()


def fnum(value, default=None):
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def rural_mask(aoi):
    smod = ee.Image("JRC/GHSL/P2023A/GHS_SMOD_V2-0/2020").select("smod_code").clip(aoi)
    return smod.eq(13).Or(smod.eq(12)).Or(smod.eq(11))


def collection_for(year: int, bounds_geom, cloud_max: float | None):
    start, end, _ = year_window(year)

    def load(cid):
        col = (
            ee.ImageCollection(cid)
            .filterBounds(bounds_geom)
            .filterDate(start, end)
            .map(heat.prep_lst)
        )
        if cloud_max is not None:
            col = col.filter(ee.Filter.lt("CLOUD_COVER", cloud_max))
        return col

    return load("LANDSAT/LC08/C02/T1_L2").merge(load("LANDSAT/LC09/C02/T1_L2"))


def scene_count(year: int, bounds_geom, cloud_max: float | None) -> int:
    return int(collection_for(year, bounds_geom, cloud_max).size().getInfo())


def summarize_lst(lst, aoi, rural):
    urban_mean = fnum(
        lst.reduceRegion(ee.Reducer.mean(), aoi, 100, maxPixels=1e8, bestEffort=True).getInfo().get("ST_C")
    )
    t_rural = fnum(
        lst.updateMask(rural)
        .reduceRegion(ee.Reducer.mean(), aoi, 100, maxPixels=1e8, bestEffort=True)
        .getInfo()
        .get("ST_C")
    )
    hot = lst.updateMask(lst.gt(LST_CUT))
    hot_stats = hot.reduceRegion(
        ee.Reducer.minMax().combine(ee.Reducer.percentile([98]), sharedInputs=True),
        aoi, 100, maxPixels=1e8, bestEffort=True,
    ).getInfo()
    suhi = None if urban_mean is None or t_rural is None else urban_mean - t_rural
    return {
        "lst_mean_C": urban_mean,
        "t_rural_C": t_rural,
        "suhi_mean_C": None if suhi is None else round(suhi, 2),
        "lst_max_C": fnum(hot_stats.get("ST_C_max")),
        "lst_p98_C": fnum(hot_stats.get("ST_C_p98")),
    }


def inventory_year(year: int, bounds_geom, aoi, rural) -> dict:
    n80 = scene_count(year, bounds_geom, CLOUD_COMPOSITE)
    n_all = scene_count(year, bounds_geom, None)
    col80 = collection_for(year, bounds_geom, CLOUD_COMPOSITE)
    col_all = collection_for(year, bounds_geom, None)
    lst80 = col80.mean().clip(aoi)
    lst_all = col_all.mean().clip(aoi)
    obs = fnum(
        col80.select("ST_C")
        .count()
        .reduceRegion(ee.Reducer.mean(), aoi, 200, maxPixels=1e8, bestEffort=True)
        .getInfo()
        .get("ST_C")
    )
    obs_all = fnum(
        col_all.select("ST_C")
        .count()
        .reduceRegion(ee.Reducer.mean(), aoi, 200, maxPixels=1e8, bestEffort=True)
        .getInfo()
        .get("ST_C")
    )
    s80 = summarize_lst(lst80, aoi, rural)
    sall = summarize_lst(lst_all, aoi, rural)
    return {
        "year": year,
        "n_scenes_cloud80": n80,
        "n_scenes_all": n_all,
        "mean_obs_per_pixel_cloud80": None if obs is None else round(obs, 2),
        "mean_obs_per_pixel_all": None if obs_all is None else round(obs_all, 2),
        "cloud80": s80,
        "all_scenes": sall,
    }


def write_compare_html(out: Path, years: list[int], lst_cut: float, suhi_cut: float):
    methods = [
        ("m1_composite", f"1. Composite LST > {lst_cut:.0f} °C", "Media por píxel, nubes de escena < 80 % · amarillo–rojo"),
        ("m2_suhi", f"2. Diferencial rural (SUHI ≥ {suhi_cut:.0f} °C)", f"Misma media, recorte SUHI ≥ {suhi_cut:.0f} °C · cian–ámbar"),
        ("m3_both", f"3. Composite amplio + SUHI ≥ {suhi_cut:.0f} °C", f"Todas las escenas abril–mayo + SUHI · cian–ámbar"),
    ]
    files = {}
    for key, _, _ in methods:
        urls = []
        for y in years:
            p = out / key / f"cdmx_{y}.png"
            ver = int(p.stat().st_mtime) if p.exists() else 0
            urls.append(f"{key}/cdmx_{y}.png?v={ver}")
        files[key] = urls
    first = files["m1_composite"][0]
    html = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CDMX · tres métodos · abril–mayo</title>
  <style>
    body {{ margin:0; background:#050505; color:#f2f2f2; font-family:"Segoe UI",Arial,sans-serif; }}
    .wrap {{ max-width:960px; margin:0 auto; padding:24px 16px 48px; }}
    h1 {{ font-size:1.35rem; margin:0 0 8px; }}
    .kicker {{ color:#f08c2b; letter-spacing:.12em; text-transform:uppercase; font-size:.72rem; }}
    .year {{ font-size:clamp(2.6rem,7vw,4rem); font-weight:800; margin:8px 0 4px; }}
    .meta {{ color:#9a9a9a; margin:0 0 12px; }}
    .tabs button {{
      background:#1a1a1a; color:#ddd; border:1px solid #333; padding:8px 12px;
      margin:0 6px 10px 0; cursor:pointer; font-weight:600;
    }}
    .tabs button.on {{ background:#f08c2b; color:#111; }}
    .stage {{ position:relative; }}
    .stage img {{ width:100%; display:block; }}
    .watermark {{
      position:absolute; right:12px; bottom:10px; font-size:1.5rem; font-weight:800;
      color:#d8d8d8; text-shadow:0 1px 8px #000; opacity:.92; pointer-events:none;
    }}
    input[type=range] {{ width:100%; accent-color:#f08c2b; margin-top:12px; }}
    .ticks {{ display:flex; justify-content:space-between; color:#888; font-size:.7rem; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="kicker">Anaplian.com · teledetección urbana</div>
    <h1>Islas de calor CDMX · tres métodos</h1>
    <div class="year" id="yearLabel">{years[0]}</div>
    <p class="meta" id="methodMeta">{methods[0][2]}</p>
    <div class="tabs" id="tabs"></div>
    <div class="stage">
      <img id="frame" src="{first}" alt="">
      <div class="watermark">Anaplian.com</div>
    </div>
    <input id="slider" type="range" min="0" max="{len(years)-1}" value="0" step="1">
    <div class="ticks">{''.join(f'<span>{y}</span>' for y in years)}</div>
  </div>
  <script>
    const years = {json.dumps(years)};
    const files = {json.dumps(files)};
    const methods = {json.dumps([(m[0], m[1], m[2]) for m in methods])};
    let method = methods[0][0];
    const tabs = document.getElementById("tabs");
    methods.forEach(([key, label, meta], i) => {{
      const b = document.createElement("button");
      b.textContent = label;
      if (i === 0) b.className = "on";
      b.onclick = () => {{
        method = key;
        document.getElementById("methodMeta").textContent = meta;
        [...tabs.children].forEach(x => x.classList.remove("on"));
        b.classList.add("on");
        show(document.getElementById("slider").value);
      }};
      tabs.appendChild(b);
    }});
    function show(i) {{
      i = Number(i);
      document.getElementById("yearLabel").textContent = years[i];
      document.getElementById("frame").src = files[method][i];
    }}
    document.getElementById("slider").oninput = e => show(e.target.value);
  </script>
</body>
</html>
"""
    (out / "compare.html").write_text(html, encoding="utf-8")


def render_year(year, lst, aoi, city_geom, city_bounds, vis, cutoff, scale_max, outfile,
                n_scenes, overlay_caption, cbar_label, footer, palette=None):
    start, end, period = year_window(year)
    heat.START, heat.END, heat.PERIOD = start, end, period
    heat.THRESHOLD = cutoff
    stats = lst.updateMask(lst.gt(cutoff)).reduceRegion(
        ee.Reducer.minMax().combine(ee.Reducer.percentile([98]), sharedInputs=True),
        aoi, 100, maxPixels=1e8, bestEffort=True,
    ).getInfo()
    abs_max = fnum(stats.get("ST_C_max"), cutoff + 4)
    hot = lst.updateMask(lst.gt(cutoff))
    heat.make_map(
        city_geom, city_bounds, 13, hot, vis,
        f"Urban Heat Islands in Ciudad de México — {year}",
        outfile, scale_max, abs_max, outline_w=3, year=year,
        watermark_size=WATERMARK_SIZE,
        overlay_caption=overlay_caption,
        cbar_label=cbar_label,
        footer=footer,
        palette=palette or vis.get("palette"),
    )


def main():
    args = parse_args()
    lst_cut = float(args.lst_cut)
    suhi_cut = float(args.suhi_cut)
    OUT.mkdir(parents=True, exist_ok=True)
    for sub in ("m1_composite", "m2_suhi", "m3_both"):
        (OUT / sub).mkdir(exist_ok=True)

    city_gdf = gpd.read_file(ROOT / "data/boundaries/ciudad_de_mexico/ciudad_de_mexico.shp").to_crs("EPSG:4326")
    city_geom = city_gdf.geometry.union_all() if hasattr(city_gdf.geometry, "union_all") else city_gdf.unary_union
    city_fc = geemap.geopandas_to_ee(city_gdf)
    aoi = city_fc.geometry()
    west, south, east, north = city_gdf.total_bounds
    city_bounds = (
        west - heat.CITY_PAD, south - heat.CITY_PAD,
        east + heat.CITY_PAD, north + heat.CITY_PAD,
    )
    city_region = ee.Geometry.Rectangle(list(city_bounds), proj="EPSG:4326", geodesic=False)
    rural = rural_mask(aoi)
    inv_path = OUT / "inventory.json"

    if args.reuse_inventory and inv_path.exists():
        inventory = json.loads(inv_path.read_text(encoding="utf-8"))
        print("Reusando", inv_path, flush=True)
        for row in inventory:
            c = row["cloud80"]
            print(
                f"{row['year']:6d} {row['n_scenes_cloud80']:6d} {row['n_scenes_all']:8d} "
                f"{(row.get('mean_obs_per_pixel_cloud80') or 0):8.2f} "
                f"{c['lst_mean_C'] or 0:9.1f} {c['t_rural_C'] or 0:8.1f} "
                f"{c['suhi_mean_C'] or 0:6.1f}",
                flush=True,
            )
    else:
        print("Inventario abril–mayo: escenas y temperaturas", flush=True)
        inventory = []
        print(
            f"{'año':>6} {'n<80':>6} {'n todas':>8} {'obs/px':>8} "
            f"{'T ciudad':>9} {'T rural':>8} {'SUHI':>6} {'máx LST':>8}",
            flush=True,
        )
        for year in range(START_YEAR, END_YEAR + 1):
            row = inventory_year(year, city_region, aoi, rural)
            inventory.append(row)
            c = row["cloud80"]
            print(
                f"{year:6d} {row['n_scenes_cloud80']:6d} {row['n_scenes_all']:8d} "
                f"{row['mean_obs_per_pixel_cloud80'] or 0:8.2f} "
                f"{c['lst_mean_C'] or 0:9.1f} {c['t_rural_C'] or 0:8.1f} "
                f"{c['suhi_mean_C'] or 0:6.1f} {c['lst_max_C'] or 0:8.1f}",
                flush=True,
            )

        (OUT / "inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
        with (OUT / "inventory.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow([
                "year", "n_scenes_cloud80", "n_scenes_all", "mean_obs_per_pixel_cloud80",
                "lst_mean_C", "t_rural_C", "suhi_mean_C", "lst_max_C",
            ])
            for row in inventory:
                c = row["cloud80"]
                w.writerow([
                    row["year"], row["n_scenes_cloud80"], row["n_scenes_all"],
                    row["mean_obs_per_pixel_cloud80"], c["lst_mean_C"], c["t_rural_C"],
                    c["suhi_mean_C"], c["lst_max_C"],
                ])
    if args.inventory_only:
        return

    vis_lst = {"min": lst_cut, "max": LST_SCALE_MAX, "palette": heat.HEAT_PALETTE}
    vis_suhi = {"min": suhi_cut, "max": SUHI_SCALE_MAX, "palette": SUHI_PALETTE}
    years = [r["year"] for r in inventory if r["n_scenes_all"] >= 1]
    do_lst = not args.skip_lst
    frames = {k: [] for k in ("m1_composite", "m2_suhi", "m3_both")}
    print(f"SUHI_CUT={suhi_cut:.0f} °C  LST_CUT={lst_cut:.0f} °C", flush=True)

    for row in inventory:
        year = row["year"]
        n80, n_all = row["n_scenes_cloud80"], row["n_scenes_all"]
        t_rural_80 = row["cloud80"]["t_rural_C"]
        t_rural_all = row["all_scenes"]["t_rural_C"]
        print(f"\n=== {year}  n80={n80}  n_all={n_all} ===", flush=True)

        lst80 = collection_for(year, city_region, CLOUD_COMPOSITE).mean().clip(aoi)
        lst_all = collection_for(year, city_region, None).mean().clip(aoi)

        if do_lst:
            render_year(
                year, lst80, aoi, city_geom, city_bounds, vis_lst, lst_cut, LST_SCALE_MAX,
                OUT / "m1_composite" / f"cdmx_{year}.png", n80,
                overlay_caption=(
                    f"{heat.LST_SOURCE}\nApr–May {year}  |  {heat.LST_HOURS}\n"
                    f"Pixel-mean composite  |  {n80} scenes  |  scene clouds < {CLOUD_COMPOSITE}%\n"
                    f"Overlay: LST > {lst_cut:.0f} °C"
                ),
                cbar_label="Land Surface Temperature (°C)",
                footer=f"{n80} escenas   ·   corte {lst_cut:.0f} °C   ·   máx {row['cloud80']['lst_max_C'] or 0:.1f} °C",
                palette=heat.HEAT_PALETTE,
            )
            frames["m1_composite"].append(OUT / "m1_composite" / f"cdmx_{year}.png")
        elif (OUT / "m1_composite" / f"cdmx_{year}.png").exists():
            frames["m1_composite"].append(OUT / "m1_composite" / f"cdmx_{year}.png")

        # 2. SUHI on the same 80% composite
        if t_rural_80 is None:
            print("skip m2, no T_rural", year, flush=True)
        else:
            suhi = lst80.subtract(t_rural_80).rename("ST_C")
            suhi_max = fnum(row["cloud80"]["lst_max_C"], suhi_cut + 8)
            if row["cloud80"]["lst_max_C"] and t_rural_80:
                suhi_max = row["cloud80"]["lst_max_C"] - t_rural_80
            render_year(
                year, suhi, aoi, city_geom, city_bounds, vis_suhi, suhi_cut, SUHI_SCALE_MAX,
                OUT / "m2_suhi" / f"cdmx_{year}.png", n80,
                overlay_caption=(
                    f"{heat.LST_SOURCE}\nApr–May {year}  |  {heat.LST_HOURS}\n"
                    f"SUHI = LST − T_rural ({t_rural_80:.1f} °C)  |  {n80} scenes  |  clouds < {CLOUD_COMPOSITE}%\n"
                    f"Overlay: urban−rural > {suhi_cut:.0f} °C"
                ),
                cbar_label="SUHI vs rural conservation land (°C)",
                footer=f"{n80} escenas   ·   T_rural {t_rural_80:.1f} °C   ·   corte SUHI {suhi_cut:.0f} °C",
                palette=SUHI_PALETTE,
            )
            frames["m2_suhi"].append(OUT / "m2_suhi" / f"cdmx_{year}.png")

        # 3. all scenes + SUHI
        if t_rural_all is None:
            print("skip m3, no T_rural", year, flush=True)
        else:
            suhi_all = lst_all.subtract(t_rural_all).rename("ST_C")
            render_year(
                year, suhi_all, aoi, city_geom, city_bounds, vis_suhi, suhi_cut, SUHI_SCALE_MAX,
                OUT / "m3_both" / f"cdmx_{year}.png", n_all,
                overlay_caption=(
                    f"{heat.LST_SOURCE}\nApr–May {year}  |  {heat.LST_HOURS}\n"
                    f"All April–May scenes, pixel cloud mask  |  {n_all} scenes\n"
                    f"SUHI = LST − T_rural ({t_rural_all:.1f} °C)  |  overlay > {suhi_cut:.0f} °C"
                ),
                cbar_label="SUHI vs rural conservation land (°C)",
                footer=f"{n_all} escenas   ·   T_rural {t_rural_all:.1f} °C   ·   corte SUHI {suhi_cut:.0f} °C",
                palette=SUHI_PALETTE,
            )
            frames["m3_both"].append(OUT / "m3_both" / f"cdmx_{year}.png")

    write_compare_html(OUT, years, lst_cut, suhi_cut)
    for key, paths in frames.items():
        if not paths:
            continue
        gif = OUT / f"{key}.gif"
        write_gif(paths, gif)
        print("GIF", gif, flush=True)
        mp4 = OUT / f"{key}.mp4"
        if try_mp4(paths, mp4):
            print("MP4", mp4, flush=True)
    print("compare", OUT / "compare.html", flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
