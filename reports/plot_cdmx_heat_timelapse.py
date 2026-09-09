"""Annual April–May CDMX heat-island overlays, GIF, and year slider.

Repeat the 2026 Landsat 8/9 mean LST > THRESHOLD overlay for every year with
data. Change the cutoff here or on the command line:

    python reports/plot_cdmx_heat_timelapse.py --threshold 35
    python reports/plot_cdmx_heat_timelapse.py --threshold 38 --tag _38c
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import ee
import geemap
import geopandas as gpd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reports"))
import plot_cdmx_heat_over_streets as heat  # noqa: E402

# --- defaults (override with argparse) ---
THRESHOLD = 35.0
NAME_TAG = "_35c"
HEAT_SCALE_MAX = 48.0  # shared color stretch so years are comparable
START_YEAR = 2013  # Landsat 8 Collection 2
END_YEAR = 2026
MONTH_START, MONTH_END = 4, 6  # April 1 inclusive, June 1 exclusive
CLOUD_MAX = 80
WATERMARK_SIZE = 26
MIN_SCENES = 1


def parse_args():
    p = argparse.ArgumentParser(description="CDMX April–May heat-island timelapse")
    p.add_argument("--threshold", type=float, default=THRESHOLD, help="LST cutoff in °C (default 35)")
    p.add_argument("--tag", default="", help="Output suffix, default _<threshold>c")
    p.add_argument("--scale-max", type=float, default=HEAT_SCALE_MAX, help="Shared legend maximum °C")
    p.add_argument("--start-year", type=int, default=START_YEAR)
    p.add_argument("--end-year", type=int, default=END_YEAR)
    p.add_argument("--inventory-only", action="store_true", help="Count scenes and exit")
    return p.parse_args()


def year_window(year: int) -> tuple[str, str, str]:
    start = f"{year}-{MONTH_START:02d}-01"
    end = f"{year}-{MONTH_END:02d}-01"
    period = f"Apr–May {year}"
    return start, end, period


def collection_for(year: int, bounds_geom):
    start, end, _ = year_window(year)
    heat.START, heat.END = start, end

    def load(cid):
        return (
            ee.ImageCollection(cid)
            .filterBounds(bounds_geom)
            .filterDate(start, end)
            .filter(ee.Filter.lt("CLOUD_COVER", CLOUD_MAX))
            .map(heat.prep_lst)
        )

    return load("LANDSAT/LC08/C02/T1_L2").merge(load("LANDSAT/LC09/C02/T1_L2"))


def inventory_year(year: int, bounds_geom) -> dict:
    col = collection_for(year, bounds_geom)
    n = int(col.size().getInfo())
    props = col.toList(n).map(
        lambda im: ee.Dictionary({
            "date": ee.Image(im).date().format("YYYY-MM-dd"),
            "spacecraft": ee.Image(im).get("SPACECRAFT_ID"),
            "cloud": ee.Image(im).get("CLOUD_COVER"),
        })
    ).getInfo() if n else []
    dates = sorted({p["date"] for p in props})
    n8 = sum(1 for p in props if str(p.get("spacecraft", "")).endswith("8") or "08" in str(p.get("spacecraft", "")))
    n9 = n - n8
    return {
        "year": year,
        "n_scenes": n,
        "n_landsat8": n8,
        "n_landsat9": n9,
        "n_dates": len(dates),
        "dates": dates,
    }


def lst_stats(lst, aoi, threshold: float) -> dict:
    stats = lst.updateMask(lst.gt(threshold)).reduceRegion(
        reducer=ee.Reducer.minMax().combine(ee.Reducer.percentile([98]), sharedInputs=True),
        geometry=aoi,
        scale=100,
        maxPixels=1e8,
        bestEffort=True,
    ).getInfo()
    heat_abs_max = float(stats.get("ST_C_max") or threshold + 8.0)
    p98 = float(stats.get("ST_C_p98") or heat_abs_max)
    return {"abs_max": heat_abs_max, "p98": p98, "raw": stats}


def write_slider(out_dir: Path, frames: list[tuple[int, Path]], threshold: float, tag: str):
    years = [y for y, _ in frames]
    files = [p.name for _, p in frames]
    ticks = "".join(f'<span>{y}</span>' for y in years)
    html = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Islas de calor CDMX · abril–mayo · corte {threshold:.0f} °C</title>
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
    <div class="kicker">Anaplian.com · teledetección urbana</div>
    <h1>Islas de calor en la Ciudad de México</h1>
    <div class="year" id="yearLabel">{years[0]}</div>
    <p class="meta">Abril–mayo · Landsat 8/9 · temperatura de superficie &gt; {threshold:.0f} °C</p>
    <div class="stage">
      <img id="frame" src="frames/{files[0]}" alt="CDMX {years[0]}">
      <div class="watermark">Anaplian.com</div>
    </div>
    <div class="controls">
      <input id="slider" type="range" min="0" max="{len(years) - 1}" value="0" step="1">
      <div class="ticks">{ticks}</div>
      <button class="play" id="play" type="button">Reproducir</button>
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
      img.alt = "CDMX " + years[i];
      yearLabel.textContent = years[i];
      slider.value = i;
    }}
    slider.addEventListener("input", () => show(slider.value));
    playBtn.addEventListener("click", () => {{
      if (timer) {{ clearInterval(timer); timer = null; playBtn.textContent = "Reproducir"; return; }}
      playBtn.textContent = "Pausa";
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


def write_gif(frames: list[Path], outfile: Path, duration_ms: int = 1100, max_side: int = 1080):
    images = [Image.open(p).convert("RGB") for p in frames]
    w0, h0 = images[0].size
    scale = min(1.0, max_side / max(w0, h0))
    size = (max(1, int(w0 * scale)), max(1, int(h0 * scale)))
    images = [im.resize(size, Image.Resampling.LANCZOS) for im in images]
    hold = images + [images[-1]] * 2
    images[0].save(
        outfile,
        save_all=True,
        append_images=hold[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
    )


def try_mp4(frames: list[Path], outfile: Path) -> bool:
    list_path = outfile.with_suffix(".txt")
    lines = []
    for p in frames:
        lines.append(f"file '{p.resolve().as_posix()}'")
        lines.append("duration 1.1")
    lines.append(f"file '{frames[-1].resolve().as_posix()}'")
    list_path.write_text("\n".join(lines), encoding="utf-8")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(outfile),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        print("system ffmpeg skipped:", exc, flush=True)
    finally:
        list_path.unlink(missing_ok=True)
    try:
        import imageio.v2 as imageio
        import numpy as np
        writer = imageio.get_writer(
            str(outfile), fps=1, codec="libx264", quality=8,
            pixelformat="yuv420p", macro_block_size=1,
        )
        last = None
        for p in frames:
            im = Image.open(p).convert("RGB")
            im.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
            w, h = im.size
            if w % 2:
                im = im.crop((0, 0, w - 1, h))
                w, h = im.size
            if h % 2:
                im = im.crop((0, 0, w, h - 1))
            last = np.array(im)
            writer.append_data(last)
        if last is not None:
            writer.append_data(last)
            writer.append_data(last)
        writer.close()
        return True
    except Exception as exc:
        print("imageio ffmpeg skipped:", exc, flush=True)
        return False


def main():
    args = parse_args()
    threshold = float(args.threshold)
    tag = args.tag or f"_{int(threshold)}c"
    heat.THRESHOLD = threshold
    out = ROOT / "reports" / "cdmx_heat_islands" / f"timelapse{tag}"
    frames_dir = out / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

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

    print("Inventario Landsat 8/9 abril–mayo, CLOUD_COVER <", CLOUD_MAX, flush=True)
    inventory = []
    for year in range(args.start_year, args.end_year + 1):
        row = inventory_year(year, city_region)
        inventory.append(row)
        print(
            f"  {year}: {row['n_scenes']:2d} escenas  "
            f"(L8 {row['n_landsat8']}, L9 {row['n_landsat9']})  "
            f"{len(row['dates'])} fechas",
            flush=True,
        )

    (out / "inventory.json").write_text(
        json.dumps(
            {
                "window": "1 April – 31 May",
                "cloud_max": CLOUD_MAX,
                "threshold_C": threshold,
                "scale_max_C": args.scale_max,
                "years": inventory,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    usable = [r for r in inventory if r["n_scenes"] >= MIN_SCENES]
    print("años con datos", [r["year"] for r in usable], flush=True)
    if args.inventory_only:
        return

    vis = {"min": threshold, "max": args.scale_max, "palette": heat.HEAT_PALETTE}
    frame_paths: list[tuple[int, Path]] = []
    year_stats = []

    for row in usable:
        year = row["year"]
        start, end, period = year_window(year)
        heat.START, heat.END, heat.PERIOD = start, end, period
        print(f"\n=== {period}  n={row['n_scenes']} ===", flush=True)
        lst = collection_for(year, city_region).mean().clip(aoi)
        stats = lst_stats(lst, aoi, threshold)
        print("hot stats", stats["raw"], flush=True)
        year_stats.append({"year": year, **{k: stats[k] for k in ("abs_max", "p98")}})
        hot = lst.updateMask(lst.gt(threshold))
        outfile = frames_dir / f"cdmx_{year}{tag}.png"
        heat.make_map(
            city_geom,
            city_bounds,
            13,
            hot,
            vis,
            f"Urban Heat Islands in Ciudad de México — {year}",
            outfile,
            args.scale_max,
            stats["abs_max"],
            outline_w=3,
            year=year,
            watermark_size=WATERMARK_SIZE,
        )
        frame_paths.append((year, outfile))

    (out / "year_stats.json").write_text(json.dumps(year_stats, indent=2), encoding="utf-8")
    write_slider(out, frame_paths, threshold, tag)
    gif = out / f"cdmx_heat_timelapse{tag}.gif"
    write_gif([p for _, p in frame_paths], gif)
    print("GIF", gif, flush=True)
    mp4 = out / f"cdmx_heat_timelapse{tag}.mp4"
    if try_mp4([p for _, p in frame_paths], mp4):
        print("MP4", mp4, flush=True)
    print("slider", out / "slider.html", flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
