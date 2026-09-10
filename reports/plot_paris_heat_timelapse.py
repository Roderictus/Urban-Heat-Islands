"""Annual April–May Paris heat-island overlays, GIF, and year slider.

Same amplio composite as CDMX: pixel-mean of every Landsat 8/9 scene (no
scene-level CLOUD_COVER cut). Pixel mask: QA_PIXEL fill, cloud, cloud-shadow,
and valid LST 0–80 °C. Overlay LST > THRESHOLD (25 °C for Paris spring).

    python reports/plot_paris_heat_timelapse.py
    python reports/plot_paris_heat_timelapse.py --threshold 30 --tag _30c
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import geemap
import geopandas as gpd
import ee

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reports"))
import plot_cdmx_heat_over_streets as heat  # noqa: E402
from plot_cdmx_heat_timelapse import (  # noqa: E402
    PIXEL_MASK,
    collection_for,
    inventory_year,
    lst_stats,
    try_mp4,
    write_gif,
    year_window,
)

THRESHOLD = 25.0
HEAT_SCALE_MAX = 35.0
START_YEAR = 2015
END_YEAR = 2026
CITY_PAD = 0.008
WATERMARK_SIZE = 26
MIN_SCENES = 1
TIMEZONE = "Europe/Paris"
LST_HOURS_FALLBACK = "~12 h 30 locale (10 h 30 UTC)"
BND = ROOT / "data" / "boundaries" / "paris" / "paris.geojson"
OUT_ROOT = ROOT / "reports" / "paris_heat_islands"


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


def parse_args():
    p = argparse.ArgumentParser(description="Paris April–May amplio heat-island timelapse")
    p.add_argument("--threshold", type=float, default=THRESHOLD, help="LST cutoff in °C (default 25)")
    p.add_argument("--tag", default="", help="Output suffix, default _<threshold>c")
    p.add_argument("--scale-max", type=float, default=HEAT_SCALE_MAX, help="Shared legend maximum °C")
    p.add_argument("--start-year", type=int, default=START_YEAR)
    p.add_argument("--end-year", type=int, default=END_YEAR)
    p.add_argument("--inventory-only", action="store_true")
    return p.parse_args()


def french_period(year: int) -> str:
    return f"Avr–mai {year}"


def write_slider(out_dir: Path, frames: list[tuple[int, Path]], threshold: float, lst_hours: str):
    years = [y for y, _ in frames]
    files = [p.name for _, p in frames]
    ticks = "".join(f"<span>{y}</span>" for y in years)
    html = f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Îlots de chaleur Paris · avril–mai · seuil {threshold:.0f} °C</title>
  <style>
    :root {{ --ink:#f4f4f4; --muted:#9a9a9a; --accent:#f08c2b; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; background: #050505; color: var(--ink);
      font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    }}
    .wrap {{ max-width: 920px; margin: 0 auto; padding: 28px 18px 48px; }}
    h1 {{ font-size: 1.45rem; margin: 0 0 6px; letter-spacing: -0.02em; }}
    .kicker {{ color: var(--accent); letter-spacing: 0.14em; text-transform: uppercase; font-size: 0.72rem; }}
    .year {{
      font-size: clamp(2.8rem, 8vw, 4.4rem); font-weight: 800;
      letter-spacing: -0.04em; margin: 12px 0 4px; line-height: 1;
    }}
    .meta {{ color: var(--muted); font-size: 0.92rem; margin-bottom: 14px; }}
    .stage {{ position: relative; background: #050505; }}
    .stage img {{ width: 100%; height: auto; display: block; }}
    .watermark {{
      position: absolute; right: 14px; bottom: 12px;
      font-size: 1.55rem; font-weight: 800; color: #d8d8d8;
      text-shadow: 0 1px 8px #000; pointer-events: none; opacity: 0.92;
    }}
    .controls {{ margin-top: 16px; }}
    input[type=range] {{
      width: 100%; accent-color: var(--accent); height: 8px;
    }}
    .ticks {{
      display: flex; justify-content: space-between; color: var(--muted);
      font-size: 0.72rem; margin-top: 4px;
    }}
    .play {{
      margin-top: 12px; background: var(--accent); color: #111; border: 0;
      padding: 8px 16px; font-weight: 700; cursor: pointer; border-radius: 4px;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="kicker">Anaplian.com · télédétection urbaine</div>
    <h1>Îlots de chaleur à Paris</h1>
    <div class="year" id="yearLabel">{years[0]}</div>
    <p class="meta">Avril–mai · {lst_hours} · composite large Landsat 8/9 · nuages/remplissage/plage valide par pixel · température de surface &gt; {threshold:.0f} °C</p>
    <div class="stage">
      <img id="frame" src="frames/{files[0]}" alt="Paris {years[0]}">
      <div class="watermark">Anaplian.com</div>
    </div>
    <div class="controls">
      <input id="slider" type="range" min="0" max="{len(years) - 1}" value="0" step="1">
      <div class="ticks">{ticks}</div>
      <button class="play" id="play" type="button">Lire</button>
    </div>
  </div>
  <script>
    const years = {json.dumps(years)};
    const files = {json.dumps(files)};
    const slider = document.getElementById("slider");
    const img = document.getElementById("frame");
    const yearLabel = document.getElementById("yearLabel");
    const playBtn = document.getElementById("play");
    let timer = null;
    function show(i) {{
      i = Number(i);
      img.src = "frames/" + files[i];
      img.alt = "Paris " + years[i];
      yearLabel.textContent = years[i];
      slider.value = i;
    }}
    slider.addEventListener("input", () => show(slider.value));
    playBtn.addEventListener("click", () => {{
      if (timer) {{ clearInterval(timer); timer = null; playBtn.textContent = "Lire"; return; }}
      playBtn.textContent = "Pause";
      timer = setInterval(() => {{
        const next = (Number(slider.value) + 1) % years.length;
        show(next);
      }}, 1100);
    }});
    years.forEach((_, i) => {{ const preload = new Image(); preload.src = "frames/" + files[i]; }});
  </script>
</body>
</html>
"""
    (out_dir / "slider.html").write_text(html, encoding="utf-8")


def main():
    args = parse_args()
    threshold = float(args.threshold)
    tag = args.tag or f"_{int(threshold)}c"
    heat.THRESHOLD = threshold
    heat.CITY_PAD = CITY_PAD
    heat.add_scale_north = add_scale_north

    out = OUT_ROOT / f"timelapse{tag}"
    frames_dir = out / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    city_gdf = gpd.read_file(BND).to_crs("EPSG:4326")
    city_geom = city_gdf.geometry.union_all() if hasattr(city_gdf.geometry, "union_all") else city_gdf.unary_union
    city_fc = geemap.geopandas_to_ee(city_gdf)
    aoi = city_fc.geometry()
    west, south, east, north = city_gdf.total_bounds
    city_bounds = (
        west - CITY_PAD, south - CITY_PAD,
        east + CITY_PAD, north + CITY_PAD,
    )
    city_region = ee.Geometry.Rectangle(list(city_bounds), proj="EPSG:4326", geodesic=False)
    zoom = heat.zoom_for(city_bounds)
    sample_start = f"{max(args.end_year - 2, args.start_year)}-04-01"
    sample_end = f"{args.end_year}-06-01"
    hours = heat.lst_overpass_hours(
        city_region, sample_start, sample_end, TIMEZONE, lang="fr",
        fallback={"label": LST_HOURS_FALLBACK, "local": "12 h 30", "utc": "10 h 30", "tz_name": TIMEZONE},
    )
    lst_hours = hours["label"]
    heat.LST_HOURS = lst_hours
    print(f"heure de survol {lst_hours}  tz {TIMEZONE}", flush=True)

    print("Inventaire Landsat 8/9 avril–mai, composite large (sans filtre CLOUD_COVER de scène)", flush=True)
    print("Masque par pixel:", PIXEL_MASK, flush=True)
    print(f"zoom {zoom}  pad {CITY_PAD}  seuil {threshold:.0f}–{args.scale_max:.0f} °C", flush=True)
    inventory = []
    for year in range(args.start_year, args.end_year + 1):
        row = inventory_year(year, city_region, aoi)
        inventory.append(row)
        obs = row["mean_obs_per_pixel"]
        print(
            f"  {year}: {row['n_scenes']:2d} scènes  "
            f"(L8 {row['n_landsat8']}, L9 {row['n_landsat9']})  "
            f"{len(row['dates'])} dates  "
            f"obs/px {obs if obs is not None else '-'}",
            flush=True,
        )

    (out / "inventory.json").write_text(
        json.dumps(
            {
                "city": "Paris",
                "window": "1 April – 31 May",
                "composite": "amplio",
                "scene_cloud_filter": None,
                "pixel_mask": PIXEL_MASK,
                "threshold_C": threshold,
                "scale_max_C": args.scale_max,
                "timezone": TIMEZONE,
                "lst_hours": lst_hours,
                "geometry": "OSM relation 7444",
                "years": inventory,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    usable = [r for r in inventory if r["n_scenes"] >= MIN_SCENES]
    print("années avec données", [r["year"] for r in usable], flush=True)
    if args.inventory_only:
        return

    vis = {"min": threshold, "max": args.scale_max, "palette": heat.HEAT_PALETTE}
    frame_paths: list[tuple[int, Path]] = []
    year_stats = []

    for row in usable:
        year = row["year"]
        start, end, _ = year_window(year)
        period = french_period(year)
        heat.START, heat.END, heat.PERIOD = start, end, period
        n_scenes = row["n_scenes"]
        print(f"\n=== {period}  n={n_scenes}  obs/px={row['mean_obs_per_pixel']} ===", flush=True)
        lst = collection_for(year, city_region).mean().clip(aoi)
        stats = lst_stats(lst, aoi, threshold)
        print("hot stats", stats["raw"], flush=True)
        year_stats.append({"year": year, "n_scenes": n_scenes, **{k: stats[k] for k in ("abs_max", "p98")}})
        hot = lst.updateMask(lst.gt(threshold))
        outfile = frames_dir / f"paris_{year}{tag}.png"
        overlay_caption = (
            f"{heat.LST_SOURCE}\n{period}  |  {lst_hours}\n"
            f"Composite large : moyenne par pixel de {n_scenes} scènes\n"
            f"Masque nuages/remplissage/plage valide par pixel\n"
            f"Overlay : température de surface > {threshold:.0f} °C"
        )
        footer = (
            f"{n_scenes} scènes   ·   seuil {threshold:.0f} °C   ·   "
            f"max {stats['abs_max']:.1f} °C"
        )
        heat.make_map(
            city_geom,
            city_bounds,
            zoom,
            hot,
            vis,
            f"Îlots de chaleur à Paris — {year}",
            outfile,
            args.scale_max,
            stats["abs_max"],
            outline_w=3,
            year=year,
            watermark_size=WATERMARK_SIZE,
            overlay_caption=overlay_caption,
            footer=footer,
            cbar_label="Température de surface (°C)",
        )
        frame_paths.append((year, outfile))

    (out / "year_stats.json").write_text(json.dumps(year_stats, indent=2), encoding="utf-8")
    write_slider(out, frame_paths, threshold, lst_hours)
    gif = out / f"paris_heat_timelapse{tag}.gif"
    write_gif([p for _, p in frame_paths], gif)
    print("GIF", gif, flush=True)
    mp4 = out / f"paris_heat_timelapse{tag}.mp4"
    tmp_mp4 = out / f"paris_heat_timelapse{tag}_new.mp4"
    if try_mp4([p for _, p in frame_paths], tmp_mp4):
        try:
            mp4.unlink(missing_ok=True)
            tmp_mp4.replace(mp4)
        except OSError:
            mp4 = tmp_mp4
        print("MP4", mp4, flush=True)
    print("slider", out / "slider.html", flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
