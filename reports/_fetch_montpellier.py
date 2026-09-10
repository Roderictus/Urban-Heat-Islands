"""Download Montpellier commune boundary from OSM Overpass."""
from __future__ import annotations

import json
from pathlib import Path

import requests
from shapely.geometry import LineString, MultiPolygon, Polygon, mapping, shape
from shapely.ops import linemerge, polygonize, unary_union

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "boundaries" / "montpellier"
OUT.mkdir(parents=True, exist_ok=True)
OVERPASS = "https://overpass-api.de/api/interpreter"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
QUERY = """
[out:json][timeout:90];
relation["name"="Montpellier"]["admin_level"="8"]["boundary"="administrative"];
out geom;
"""


def ring(pts):
    return [(p["lon"], p["lat"]) for p in pts]


def ways_to_polygon(members):
    lines = []
    for m in members:
        if m.get("type") != "way":
            continue
        geom = m.get("geometry") or []
        if len(geom) < 2:
            continue
        coords = ring(geom)
        if len(coords) >= 2:
            lines.append(LineString(coords))
    if not lines:
        return None
    merged = linemerge(lines)
    polys = list(polygonize(merged))
    if not polys:
        closed = []
        for ln in lines:
            coords = list(ln.coords)
            if coords[0] != coords[-1] and ln.length > 0:
                coords.append(coords[0])
            if len(coords) >= 4:
                try:
                    p = Polygon(coords)
                    if p.is_valid and p.area > 0:
                        closed.append(p)
                except Exception:
                    pass
        if not closed:
            return None
        polys = closed
    geom = unary_union(polys)
    if geom.is_empty:
        return None
    if not geom.is_valid:
        geom = geom.buffer(0)
    return geom


def from_nominatim():
    r = requests.get(
        NOMINATIM,
        params={
            "city": "Montpellier",
            "country": "France",
            "format": "geojson",
            "polygon_geojson": 1,
            "limit": 5,
            "featuretype": "settlement",
        },
        headers={"User-Agent": "Anaplian-heat-islands/1.0 (research)"},
        timeout=60,
    )
    r.raise_for_status()
    fc = r.json()
    feats = fc.get("features") or []
    print("nominatim features", len(feats), flush=True)
    best = None
    best_score = None
    for f in feats:
        props = f.get("properties") or {}
        geom = shape(f["geometry"])
        print(
            "nominatim", props.get("osm_id"), props.get("display_name", "")[:80],
            "type", f["geometry"]["type"], "area", round(geom.area, 5),
            flush=True,
        )
        # Commune ~57 km² ≈ 0.0064 deg²; skip arrondissement/métropole giants.
        if 0.003 < geom.area < 0.02:
            score = abs(geom.area - 0.0064)
            if best_score is None or score < best_score:
                best, best_score = f, score
    if best is None:
        for f in feats:
            geom = shape(f["geometry"])
            if best is None or geom.area < shape(best["geometry"]).area:
                best = f
    return best


def main():
    feat_in = from_nominatim()
    if feat_in is None:
        raise SystemExit("No Montpellier polygon")
    geom = shape(feat_in["geometry"])
    p = feat_in.get("properties") or {}
    osm_id = p.get("osm_id") or p.get("place_id")
    props = {
        "name": "Montpellier",
        "display_name": p.get("display_name"),
        "osm_type": p.get("osm_type"),
        "osm_id": osm_id,
        "source": "OpenStreetMap Nominatim",
    }

    if geom.geom_type == "Polygon":
        geom = MultiPolygon([geom])
    feat = {"type": "Feature", "properties": props, "geometry": mapping(geom)}
    fc = {"type": "FeatureCollection", "features": [feat]}
    (OUT / "montpellier.geojson").write_text(json.dumps(fc), encoding="utf-8")
    source = props.get("source", "OpenStreetMap")
    osm_ref = props.get("osm_id")
    (OUT / "CITATION.txt").write_text(
        "Commune de Montpellier (Hérault, France).\n"
        f"Geometry: {source}, osm_id={osm_ref}.\n"
        f"https://www.openstreetmap.org/relation/{osm_ref}\n"
        "License: ODbL 1.0. https://www.openstreetmap.org/copyright\n",
        encoding="utf-8",
    )
    g = shape(feat["geometry"])
    print("area_deg2", round(g.area, 5), "bounds", [round(x, 4) for x in g.bounds], flush=True)
    print("wrote", OUT / "montpellier.geojson", flush=True)


if __name__ == "__main__":
    main()
