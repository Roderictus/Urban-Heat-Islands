"""Download Paris commune and 20 municipal arrondissements."""
from __future__ import annotations

import json
import re
from pathlib import Path

import geopandas as gpd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "boundaries" / "paris"
OUT.mkdir(parents=True, exist_ok=True)
ARR_URL = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson"
NOMINATIM = "https://nominatim.openstreetmap.org/lookup"
UA = {"User-Agent": "Anaplian-heat-islands/1.0 (research)"}


def ordinal(n: int) -> str:
    return "1er" if n == 1 else f"{n}e"


def normalize_arr(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf = gdf.to_crs("EPSG:4326").copy()
    cols = {c.lower(): c for c in gdf.columns}

    def pick(*names):
        for n in names:
            if n in cols:
                return cols[n]
        return None

    name_col = pick("l_ar", "nom", "nom_officiel", "name", "larr")
    num_col = pick("c_ar", "n_sq_ar", "arrondissement", "insee")
    numbers = []
    names = []
    for _, row in gdf.iterrows():
        num = None
        if num_col:
            raw = row[num_col]
            try:
                num = int(float(str(raw).lstrip("0") or "0"))
            except (TypeError, ValueError):
                m = re.search(r"(\d{1,2})", str(raw))
                num = int(m.group(1)) if m else None
        if num is None or num < 1 or num > 20:
            label = str(row[name_col] if name_col else "")
            m = re.search(r"(\d{1,2})", label)
            num = int(m.group(1)) if m else None
        if num is None:
            raise SystemExit(f"Cannot parse arrondissement number from {dict(row)}")
        numbers.append(num)
        names.append(f"{ordinal(num)} arrondissement")
    gdf["c_ar"] = numbers
    gdf["arrondissement"] = names
    gdf["slug"] = [ordinal(n).lower() for n in numbers]
    gdf = gdf.sort_values("c_ar").reset_index(drop=True)
    return gdf[["c_ar", "arrondissement", "slug", "geometry"]]


def from_opendata():
    print("opendata.paris.fr arrondissements…", flush=True)
    r = requests.get(ARR_URL, headers=UA, timeout=90)
    r.raise_for_status()
    path = OUT / "_arrondissements_raw.geojson"
    path.write_bytes(r.content)
    gdf = gpd.read_file(path)
    print("features", len(gdf), "cols", list(gdf.columns), flush=True)
    return normalize_arr(gdf)


def from_nominatim_city():
    print("nominatim Paris R7444…", flush=True)
    r = requests.get(
        NOMINATIM,
        params={"osm_ids": "R7444", "format": "geojson", "polygon_geojson": 1},
        headers=UA,
        timeout=60,
    )
    r.raise_for_status()
    fc = r.json()
    feats = fc.get("features") or []
    if not feats:
        return None
    return gpd.GeoDataFrame.from_features(feats, crs="EPSG:4326")


def main():
    arr = from_opendata()
    if len(arr) != 20:
        raise SystemExit(f"Expected 20 arrondissements, got {len(arr)}")
    geom = arr.geometry
    city_union = geom.union_all() if hasattr(geom, "union_all") else arr.unary_union()
    city = gpd.GeoDataFrame(
        [{"name": "Paris", "source": "opendata.paris.fr arrondissements (union)"}],
        geometry=[city_union],
        crs="EPSG:4326",
    )
    nom = from_nominatim_city()
    if nom is not None and not nom.empty:
        print("nominatim area_deg2", round(nom.geometry.iloc[0].area, 5), flush=True)
        city = gpd.GeoDataFrame(
            [{
                "name": "Paris",
                "display_name": (nom.iloc[0].get("display_name") if "display_name" in nom.columns else "Paris"),
                "osm_id": 7444,
                "source": "OpenStreetMap Nominatim relation 7444",
            }],
            geometry=[nom.geometry.iloc[0]],
            crs="EPSG:4326",
        )

    arr_path = OUT / "paris_arrondissements.geojson"
    city_path = OUT / "paris.geojson"
    arr.to_file(arr_path, driver="GeoJSON")
    city.to_file(city_path, driver="GeoJSON")
    (OUT / "CITATION.txt").write_text(
        "Ville de Paris et 20 arrondissements municipaux.\n"
        "Commune: OpenStreetMap relation 7444 (Nominatim).\n"
        "Arrondissements: Ville de Paris open data (opendata.paris.fr, dataset arrondissements).\n"
        "https://opendata.paris.fr/explore/dataset/arrondissements/\n"
        "https://www.openstreetmap.org/relation/7444\n"
        "License: ODbL 1.0 / Licence Ouverte.\n",
        encoding="utf-8",
    )
    print("arrondissements", ", ".join(arr["arrondissement"].tolist()), flush=True)
    print("city bounds", [round(x, 4) for x in city.total_bounds], "area_deg2", round(city.geometry.iloc[0].area, 5), flush=True)
    print("wrote", city_path, flush=True)
    print("wrote", arr_path, flush=True)
    raw = OUT / "_arrondissements_raw.geojson"
    if raw.exists():
        raw.unlink()


if __name__ == "__main__":
    main()
