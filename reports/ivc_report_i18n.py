"""Spanish / English / French copy for IVC HTML+PDF sites.

Maps stay shared (Spanish titles on the raster). Charts, HTML and PDF are
language-specific so a later site can switch with index.html / en.html / fr.html.
"""
from __future__ import annotations

import re
import unicodedata
import json
import shutil
from datetime import datetime
from pathlib import Path

import numpy as np
from fpdf import FPDF
from PIL import Image

from ivc_priority1 import METRIC_VERSION
from city_local_copy import local_note, local_zones, tropical_rank

YEAR = 2026
LANGS = ("es", "en", "fr")
RICH_SLUGS = ("cdmx", "ahmedabad", "phoenix")
HTML_NAME = {"es": "index.html", "en": "en.html", "fr": "fr.html"}
PDF_STEM = {
    "es": "Vulnerabilidad_climatica",
    "en": "Climate_vulnerability",
    "fr": "Vulnerabilite_climatique",
}
LST_MAX_CUT = 43.0
LST_MEAN_MAP_CUT = 35.0
LST_MEAN_INDEX_CUT = 43.0
NDVI_VEG = 0.30
SMOD_URBAN = 21
NDVI_LO, NDVI_HI = 0.05, 0.55
SUHI_MAP_CUT = 8.0
SUHI_INDEX_CAP = 15.0
MIN_RURAL_KM2 = 80.0
BRANDING = Path(__file__).resolve().parent / "branding"


def apply_cdmx_chapter_numbers(ui: dict, lang: str, slug: str, name: str, ulabel: str, ulabels: str, prio: int) -> None:
    if slug not in RICH_SLUGS:
        return
    methods_h, maps, four_h, table_h, hot_h, units_h, why_h = {
        "en": (
            "4. Four methods",
            (
                "5. Per-pixel maximum surface temperature (> 43 °C)",
                "6. Mean surface temperature of observations (> 35 °C)",
                "7. Vegetation (NDVI)",
                "8. Heat island (pixel − rural)",
            ),
            "9. Four sub-index elements",
            f"10. Table of {ulabels}",
            "11. Heat-exposure sites",
            f"12. {ulabels[:1].upper() + ulabels[1:]}",
            f"13. Why {name} is in Priority {prio}",
        ),
        "fr": (
            "4. Quatre méthodes",
            (
                "5. Température de surface maximale par pixel (> 43 °C)",
                "6. Température de surface, moyenne des observations (> 35 °C)",
                "7. Végétation (NDVI)",
                "8. Îlot de chaleur (pixel − rural)",
            ),
            "9. Quatre éléments du sous-indice",
            f"10. Tableau des {ulabels}",
            "11. Sites d’exposition à la chaleur",
            f"12. {ulabels[:1].upper() + ulabels[1:]}",
            f"13. Pourquoi {name} est en Priorité {prio}",
        ),
    }.get(lang, (
        "4. Cuatro metodologías",
        (
            "5. Temperatura de superficie máxima por píxel (> 43 °C)",
            "6. Temperatura de superficie, promedio de observaciones (> 35 °C)",
            "7. Vegetación (NDVI)",
            "8. Isla de calor (píxel − rural)",
        ),
        "9. Cuatro elementos del subíndice",
        f"10. Tabla de {ulabels}",
        "11. Zonas de exposición al calor",
        f"12. {ulabels[:1].upper() + ulabels[1:]}",
        f"13. Por qué {name} está en Prioridad {prio}",
    ))
    pdf_maps = {
        "en": (
            "4. Per-pixel maximum LST > 43 °C",
            "5. Mean LST of observations > 35 °C",
            "6. Vegetation (NDVI)",
            "7. Heat island (pixel − rural)",
        ),
        "fr": (
            "4. LST maximale par pixel > 43 °C",
            "5. LST moyenne des observations > 35 °C",
            "6. Végétation (NDVI)",
            "7. Îlot de chaleur (pixel − rural)",
        ),
    }.get(lang, (
        "4. LST máxima por píxel > 43 °C",
        "5. LST media de observaciones > 35 °C",
        "6. Vegetación (NDVI)",
        "7. Isla de calor (píxel − rural)",
    ))
    pdf_four = {
        "en": "8. Four sub-index elements",
        "fr": "8. Quatre éléments du sous-indice",
    }.get(lang, "8. Cuatro elementos del subíndice")
    pdf_table = {
        "en": f"9. Table of {ulabels}",
        "fr": f"9. Tableau des {ulabels}",
    }.get(lang, f"9. Tabla de {ulabels}")
    pdf_hot = {
        "en": "10. Heat-exposure sites",
        "fr": "10. Sites d’exposition à la chaleur",
    }.get(lang, "10. Zonas de exposición al calor")
    pdf_units = {
        "en": f"11. {ulabels[:1].upper() + ulabels[1:]}",
        "fr": f"11. {ulabels[:1].upper() + ulabels[1:]}",
    }.get(lang, f"11. {ulabels[:1].upper() + ulabels[1:]}")
    pdf_why = {
        "en": f"12. Why {name} is in Priority {prio}",
        "fr": f"12. Pourquoi {name} est en Priorité {prio}",
    }.get(lang, f"12. Por qué {name} está en Prioridad {prio}")
    # HTML keeps methods as chapter 4; PDF folds methods into map pages 4–7.
    ui["four"] = methods_h
    ui["map1"], ui["map2"], ui["map3"], ui["map4"] = maps
    ui["order"] = four_h
    ui["table_h"] = table_h
    ui["units_h"] = units_h
    ui["why_prio"] = why_h
    ui["hotspot_h"] = hot_h
    ui["pdf_m1"], ui["pdf_m2"], ui["pdf_m3"], ui["pdf_m4"] = pdf_maps
    ui["pdf_four"] = pdf_four
    ui["pdf_index"] = pdf_four
    ui["pdf_table"] = pdf_table
    ui["pdf_hotspot"] = pdf_hot
    ui["pdf_units"] = pdf_units
    ui["pdf_why"] = pdf_why
    ui["toc_html"] = [
        ("intro", ui["why_index"]),
        ("rank", ui["rank_h"]),
        ("subdiv", ui["subdiv_h"]),
        ("methods", ui["four"]),
        ("map1", ui["map1"]),
        ("map2", ui["map2"]),
        ("map3", ui["map3"]),
        ("map4", ui["map4"]),
        ("order", ui["order"]),
        ("table", table_h),
        ("hotspots", ui["hotspot_h"]),
        ("units", ui["units_h"]),
        ("why", ui["why_prio"]),
    ]
    ui["toc_pdf"] = [
        ui["why_index"],
        ui["rank_h"],
        ui["subdiv_h"],
        ui["pdf_m1"], ui["pdf_m2"], ui["pdf_m3"], ui["pdf_m4"],
        ui["pdf_four"],
        ui["pdf_table"],
        ui["pdf_hotspot"],
        ui["pdf_units"],
        ui["pdf_why"],
    ]
    if slug != "cdmx":
        units_label = ulabels[:1].upper() + ulabels[1:]
        html_units, html_why, pdf_u, pdf_w = {
            "en": (
                f"11. {units_label}",
                f"12. Why {name} is in Priority {prio}",
                f"10. {units_label}",
                f"11. Why {name} is in Priority {prio}",
            ),
            "fr": (
                f"11. {units_label}",
                f"12. Pourquoi {name} est en Priorité {prio}",
                f"10. {units_label}",
                f"11. Pourquoi {name} est en Priorité {prio}",
            ),
        }.get(lang, (
            f"11. {units_label}",
            f"12. Por qué {name} está en Prioridad {prio}",
            f"10. {units_label}",
            f"11. Por qué {name} está en Prioridad {prio}",
        ))
        ui["units_h"] = html_units
        ui["why_prio"] = html_why
        ui["pdf_units"] = pdf_u
        ui["pdf_why"] = pdf_w
        ui["toc_html"] = [item for item in ui["toc_html"] if item[0] != "hotspots"]
        ui["toc_html"] = [
            (k, html_units if k == "units" else html_why if k == "why" else v)
            for k, v in ui["toc_html"]
        ]
        ui["toc_pdf"] = [
            ui["why_index"],
            ui["rank_h"],
            ui["subdiv_h"],
            ui["pdf_m1"], ui["pdf_m2"], ui["pdf_m3"], ui["pdf_m4"],
            ui["pdf_four"],
            ui["pdf_table"],
            ui["pdf_units"],
            ui["pdf_why"],
        ]


def comparable_units(lang: str, slug: str, ulabels: str) -> str:
    if lang == "en":
        if slug == "cdmx":
            return (
                f"{ulabels} of Mexico City and the equivalent political divisions "
                "of other cities worldwide"
            )
        return f"{ulabels} and the equivalent political divisions of other cities worldwide"
    if lang == "fr":
        if slug == "cdmx":
            return (
                f"{ulabels} de Mexico et l’équivalent en divisions politiques "
                "d’autres villes du monde"
            )
        return f"{ulabels} et l’équivalent en divisions politiques d’autres villes du monde"
    if slug == "cdmx":
        return (
            f"{ulabels} de la CDMX y el equivalente en divisiones políticas "
            "para otras ciudades del mundo"
        )
    return f"{ulabels} y el equivalente en divisiones políticas para otras ciudades del mundo"


RANKING_JSON = Path(__file__).resolve().parent / "ranking_ivc_l4_v1.json"


def load_official_ranking() -> dict:
    if RANKING_JSON.exists():
        return json.loads(RANKING_JSON.read_text(encoding="utf-8"))
    return {}


def load_city_ranking() -> list[dict]:
    data = load_official_ranking()
    cities = data.get("cities") or []
    if cities:
        rows = []
        for rec in cities:
            rows.append({
                "slug": rec["slug"],
                "ivc": float(rec["ivc"]),
                "suhi": float(rec.get("suhi") or 0),
                "t_rural": float(rec.get("t_rural") or 0),
                "rank": int(rec["rank"]),
            })
        rows.sort(key=lambda r: r["rank"])
        return rows
    rows = []
    base = Path(__file__).resolve().parent
    for folder in base.glob("*_heat_islands"):
        idx = folder / "vulnerability_2026" / "index.json"
        if not idx.exists():
            continue
        meta = json.loads(idx.read_text(encoding="utf-8"))
        ivc = meta.get("city_ivc")
        if ivc is None:
            continue
        slug = folder.name[: -len("_heat_islands")]
        rows.append({
            "slug": slug,
            "ivc": float(ivc),
            "suhi": float(meta.get("city_suhi") or 0),
            "t_rural": float(meta.get("t_rural") or 0),
        })
    rows.sort(key=lambda r: (-r["ivc"], r["slug"]))
    for i, row in enumerate(rows, 1):
        row["rank"] = i
    return rows


def city_top25_units(slug: str) -> tuple[int, list[dict]]:
    data = load_official_ranking()
    units = data.get("units") or []
    n_units = int(data.get("n_units") or len(units) or 296)
    top = [u for u in units[:25] if u.get("slug") == slug]
    return n_units, top


def city_short(slug: str, lang: str) -> str:
    info = CITY_I18N.get(slug) or {}
    return (info.get("name") or {}).get(lang) or slug.replace("_", " ").title()


def intro_and_rank(lang: str, slug: str, name: str, country: str, ulabel: str, ulabels: str, df, meta: dict) -> dict:
    ranking = load_city_ranking()
    n_cities = len(ranking) or 1
    mine = next((r for r in ranking if r["slug"] == slug), None)
    rank = int(mine["rank"]) if mine else 0
    ivc = float(meta.get("city_ivc") or (mine or {}).get("ivc") or 0)
    suhi = float(meta.get("city_suhi") or 0)
    t_rural = float(meta.get("t_rural") or 0)
    leaders = [r for r in ranking if r["slug"] != slug][:2]
    nxt = next((r for r in ranking if r["rank"] == rank + 1), None)
    names = [f"{city_short(r['slug'], lang)} ({r['ivc']:.1f})" for r in leaders]
    if lang == "en":
        conj = " and "
    elif lang == "fr":
        conj = " et "
    else:
        conj = " y "
    lead_txt = conj.join(names) if len(names) == 2 else ", ".join(names)
    nxt_name = city_short(nxt["slug"], lang) if nxt else ""
    nxt_ivc = nxt["ivc"] if nxt else 0
    hottest, coolest = df.iloc[0], df.iloc[-1]
    top_n = min(5, len(df))
    top_rows = list(df.itertuples())[:top_n]
    n_units_all, city_top25 = city_top25_units(slug)

    def _ord(n: int) -> str:
        if lang == "en":
            if 10 <= n % 100 <= 20:
                suf = "th"
            else:
                suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
            return f"{n}{suf}"
        if lang == "fr":
            return "1re" if n == 1 else f"{n}e"
        return f"{n}.°"

    top25_txt = ", ".join(
        f"{u['unit']} ({_ord(int(u['rank']))}, IVC {u['ivc']:.0f})" for u in city_top25
    )
    n_cdmx_top = len(city_top25)
    if lang == "en":
        intro_p1 = (
            "The sustained rise in mean temperature and in its variability — more extreme days, longer "
            "heatwaves — falls on human settlements. The body sheds heat by radiation, convection and, "
            "above all, evaporation of sweat. When air and radiating surfaces block that loss, core "
            "temperature rises, the heart works harder to send blood to the skin, and water and electrolytes "
            "are lost. The outcome can be heat exhaustion, heat stroke or cardiovascular and renal strain. "
            "Night-time heat, typical of urban islands, cuts recovery during sleep. The risk is higher for "
            "older people, those with chronic illness, outdoor workers and residents of poorly ventilated "
            "or unshaded housing."
        )
        intro_p2 = (
            f"The purpose of this index is to quantify that surface heat load and make it comparable, "
            f"so as to see where vulnerability concentrates and which urban traits foster it: pavement, "
            f"sheds, vegetation deficit and heat islands relative to the surroundings. It does not replace "
            f"demography or epidemiological surveillance; it ranks territory by surface exposure, with a "
            f"fixed metric across cities."
        )
        intro_p3 = (
            f"The comparison works at two scales. Across cities, the same number sizes the problem against "
            f"places that already apply good practice or illustrate solutions to heat concentration. Inside "
            f"each city, the political units — in {name}, the {ulabels} — locate the most problematic zones "
            f"in more detail and point to authorities and residents with a direct stake in addressing them."
        )
        intro_p4 = (
            "For data availability and comparability we use four Landsat layers. Three are surface "
            "temperature: the period maximum, the mean of the observations and the heat island, the "
            "differential between a nearby rural or less-urbanised reference zone and the temperature "
            "in the area. The fourth is a vegetation index (NDVI) that enters inverted: lower greenness "
            "is penalised, because vegetation has a clear cooling effect."
        )
        rank_h = "2. Position in the index"
        rank_city = (
            f"{name} ranks {rank} of {n_cities} cities measured in April and May 2026, with a "
            f"Climate Vulnerability Index (IVC) of {ivc:.1f} out of 100. {lead_txt} lead. "
            f"{f'{nxt_name} ({nxt_ivc:.1f}) comes next. ' if nxt else ''}"
            f"What sets {name} apart is not being the hottest desert, but the strongest heat island "
            f"in the sample: the urban surface sits about {abs(suhi):.0f} °C above a nearby, cooler "
            f"reference zone."
        )
        if slug == "cdmx":
            rank_alc = (
                f"Inside the city the index concentrates in the fully urban east and north. "
                f"{hottest.unit} leads (IVC {hottest.ivc:.0f}): here are Mexico City International Airport "
                f"(AICM), the Eastern Passenger Bus Terminal (TAPO) and the sports city. "
                f"{top_rows[1].unit} ({top_rows[1].ivc:.0f}), the smallest and entirely urban borough, "
                f"follows with the Pantitlán Modal Transfer Centre (CETRAM). "
                f"{top_rows[2].unit} ({top_rows[2].ivc:.0f}) supplies the largest urban mass and Central "
                f"de Abasto. {top_rows[3].unit} ({top_rows[3].ivc:.0f}) adds sheds and yards in Vallejo "
                f"and El Rosario. {top_rows[4].unit} ({top_rows[4].ivc:.0f}) adds the historic centre and "
                f"La Merced."
            )
            rank_why = (
                f"That concentration at the top of the ranking follows urban form, not latitude: "
                f"paved slabs, terminals, sheds and little vegetation. These are heat islands that "
                f"shade, cool roofs, trees and a reduction of pavement can still treat.\n\n"
                f"{df.iloc[5].unit} ({df.iloc[5].ivc:.0f}) ranks high because of the town, even if "
                f"the chinampas lower the borough mean. {df.iloc[6].unit} ({df.iloc[6].ivc:.0f}) "
                f"ranks high because of Indios Verdes and Central del Norte, even if the northern "
                f"hillside lowers the mean.\n\n"
                f"In Ahmedabad or Riyadh climate weighs more: rural surroundings already reach very "
                f"high surface temperatures, and background heat affects the city as a whole. In "
                f"Mexico City the additional heat is an urban differential, so it admits city-design "
                f"solutions. {coolest.unit} ranks last ({coolest.ivc:.0f})."
            )
            rank_units = (
                "The ranking of political subdivisions — boroughs, districts and their equivalents "
                "across the 18 cities in the index — places Mexico City’s eastern boroughs at the top."
            )
            rank_soil = (
                "Land cover in the city’s top five boroughs is concrete, asphalt and roofs, with little "
                "green. Venustiano Carranza is dominated by AICM runways, aprons and terminals, plus TAPO "
                "platforms and the sports-city slab; airport coverage replaces vegetation. Iztacalco is "
                "entirely urban: CETRAM Pantitlán sits on a transfer slab, the rest is roofs and the "
                "viaduct. Iztapalapa’s Central de Abasto is warehouses for perishables on asphalt yards "
                "with almost no trees. Azcapotzalco adds Vallejo and El Rosario sheds and loading yards. "
                "Cuauhtémoc adds the historic centre’s stone and terraces, La Merced’s metal roofs and "
                "the Reforma–Juárez asphalt corridor; parks are fragments that do not offset the slab."
            )
            subdiv_h = "3. Highest-IVC subdivisions"
            subdiv_p = (
                f"Among {n_units_all} political subdivisions of the 18 cities in the comparable index, "
                f"{n_cdmx_top} Mexico City boroughs enter the top 25: {top25_txt}. "
                "Maryvale (Phoenix) sits 5th, between Azcapotzalco and Cuauhtémoc. "
                "The components chart shows why the city’s east saturates z_SUHI and z_LST max: "
                "slab and a greenness deficit, not a hot desert background. Coyoacán (29th) falls "
                "just outside the top 25."
            )
        else:
            rank_alc = (
                f"Among the {len(df)} {ulabels}, {hottest.unit} leads (IVC {hottest.ivc:.0f}) and "
                f"{coolest.unit} ranks last ({coolest.ivc:.0f})."
            )
            rank_why = (
                "Where the heat island is strong, pavement and a vegetation deficit usually explain the "
                "top of the list, and urban design can still cool. Where the surroundings are themselves "
                "hot, geography and climate weigh more."
            )
            rank_units = (
                f"The ranking of political subdivisions places the {ulabels} of {name} next to districts "
                "and boroughs of the other cities in the index."
            )
            rank_soil = ""
            subdiv_h = ""
            subdiv_p = ""
    elif lang == "fr":
        intro_p1 = (
            "La hausse soutenue de la température moyenne et de sa variabilité — plus de jours extrêmes, "
            "des vagues plus longues — pèse sur les peuplements humains. Le corps dissipe la chaleur par "
            "rayonnement, convection et surtout évaporation de la sueur. Quand l’air et les surfaces qui "
            "rayonnent empêchent cette perte, la température corporelle monte, le cœur travaille plus pour "
            "envoyer le sang vers la peau, eau et électrolytes se perdent. L’issue peut être l’épuisement, "
            "le coup de chaleur ou une décompensation cardiovasculaire et rénale. La chaleur nocturne, "
            "typique des îlots urbains, réduit la récupération du sommeil. Le risque est plus élevé chez "
            "les personnes âgées, malades chroniques, travailleurs en extérieur et habitants de logements "
            "mal ventilés ou sans ombre."
        )
        intro_p2 = (
            "Le but de cet indice est de quantifier cette charge de chaleur de surface et de la rendre "
            "comparable, pour voir où se concentre la vulnérabilité et quels traits urbains la favorisent : "
            "revêtement, hangars, déficit de verdure et îlots de chaleur par rapport à l’environnement. "
            "Il ne remplace ni la démographie ni la surveillance épidémiologique ; il ordonne le territoire "
            "selon l’exposition de surface, avec une métrique fixe d’une ville à l’autre."
        )
        intro_p3 = (
            f"La comparaison opère à deux échelles. Entre villes, un même nombre dimensionne le problème "
            f"face à d’autres qui appliquent déjà de bonnes pratiques ou illustrent des solutions à la "
            f"concentration de chaleur. Dans chaque ville, les divisions politico-administratives — à "
            f"{name}, les {ulabels} — localisent plus finement les zones problématiques et désignent "
            f"autorités et population directement concernées."
        )
        intro_p4 = (
            "Par disponibilité des données et comparabilité, nous retenons quatre couches Landsat. Trois "
            "sont de température de surface : le maximum de la période, la moyenne des observations et "
            "l’îlot de chaleur, le différentiel entre une zone de référence proche, rurale ou moins "
            "urbanisée, et la température de la zone. La quatrième est un indice de végétation (NDVI) "
            "qui entre inversé : on pénalise un verdissement plus faible, parce que la végétation a un "
            "effet de refroidissement net."
        )
        rank_h = "2. Position dans l’indice"
        rank_city = (
            f"{name} occupe la {rank}e place sur {n_cities} villes mesurées en avril et mai 2026, avec un "
            f"indice de vulnérabilité climatique (IVC) de {ivc:.1f} sur 100. {lead_txt} arrivent en tête. "
            f"{f'{nxt_name} ({nxt_ivc:.1f}) suit. ' if nxt else ''}"
            f"Ce qui distingue {name}, ce n’est pas d’être le désert le plus chaud, mais l’îlot de chaleur "
            f"le plus marqué de l’échantillon : la surface urbaine est d’environ {abs(suhi):.0f} °C au-dessus "
            f"d’une zone de référence proche, plus fraîche."
        )
        if slug == "cdmx":
            rank_alc = (
                f"Dans la ville, l’indice se concentre à l’est et au nord entièrement urbains. "
                f"{hottest.unit} arrive en tête (IVC {hottest.ivc:.0f}) : s’y trouvent l’aéroport "
                f"international de Mexico (AICM), la gare routière de l’est (TAPO) et la cité sportive. "
                f"{top_rows[1].unit} ({top_rows[1].ivc:.0f}), la plus petite et entièrement urbaine, "
                f"suit avec le centre de correspondance (CETRAM) Pantitlán. "
                f"{top_rows[2].unit} ({top_rows[2].ivc:.0f}) apporte la plus grande masse urbaine et la "
                f"Central de Abasto. {top_rows[3].unit} ({top_rows[3].ivc:.0f}) ajoute hangars et cours "
                f"à Vallejo et El Rosario. {top_rows[4].unit} ({top_rows[4].ivc:.0f}) ajoute le centre "
                f"historique et La Merced."
            )
            rank_why = (
                f"Cette concentration en tête du classement s’explique par la forme urbaine, non par la "
                f"latitude : dalles, terminaux, hangars et peu de végétation. Ce sont des îlots de chaleur "
                f"que l’ombre, les toits froids, les arbres et moins de revêtement peuvent encore traiter.\n\n"
                f"{df.iloc[5].unit} ({df.iloc[5].ivc:.0f}) se classe haut grâce au bourg, même si les "
                f"chinampas abaissent la moyenne de la délégation. {df.iloc[6].unit} ({df.iloc[6].ivc:.0f}) "
                f"se classe haut grâce à Indios Verdes et à la Central del Norte, même si le versant nord "
                f"abaisse la moyenne.\n\n"
                f"À Ahmedabad ou Riyad, le climat pèse davantage : l’environnement rural atteint déjà des "
                f"températures de surface très élevées, et la chaleur de fond concerne la ville dans son "
                f"ensemble. À Mexico, la chaleur supplémentaire est un différentiel urbain, d’où des "
                f"solutions de dessin de ville. {coolest.unit} arrive dernière ({coolest.ivc:.0f})."
            )
            rank_units = (
                "Le classement des subdivisions politiques — délégations, districts et équivalents "
                "des 18 villes de l’indice — place les délégations de l’est de Mexico en tête."
            )
            rank_soil = (
                "La couverture du sol dans les cinq délégations en tête de l’indice de la ville est "
                "béton, asphalte et toits, avec peu de verdure. Venustiano Carranza est dominée par "
                "les pistes, aires et terminaux de l’AICM, plus la TAPO et la dalle de la cité "
                "sportive ; la couverture aéroportuaire remplace la végétation. Iztacalco est "
                "entièrement urbaine : le CETRAM Pantitlán est une dalle de correspondance, le reste "
                "des toits et le viaduc. La Central de Abasto à Iztapalapa, ce sont des hangars de "
                "denrées périssables sur des cours d’asphalte, presque sans arbres. Azcapotzalco "
                "ajoute hangars et cours à Vallejo et El Rosario. Cuauhtémoc ajoute pierre et "
                "terrasses du centre historique, toits de tôle de La Merced et le couloir asphalté "
                "Reforma–Juárez ; les parcs sont des fragments qui ne compensent pas la dalle."
            )
            subdiv_h = "3. Subdivisions à l’IVC le plus élevé"
            subdiv_p = (
                f"Parmi les {n_units_all} subdivisions politiques des 18 villes de l’indice comparable, "
                f"{n_cdmx_top} délégations de Mexico entrent dans le top 25 : {top25_txt}. "
                "Maryvale (Phoenix) est 5e, entre Azcapotzalco et Cuauhtémoc. "
                "Le graphique des composantes montre pourquoi l’est de la ville sature z_SUHI et "
                "z_LST max. : dalle et déficit de verdure, pas un désert de fond. Coyoacán (29e) "
                "reste juste hors du top 25."
            )
        else:
            rank_alc = (
                f"Parmi les {len(df)} {ulabels}, {hottest.unit} arrive en tête (IVC {hottest.ivc:.0f}) "
                f"et {coolest.unit} en dernier ({coolest.ivc:.0f})."
            )
            rank_why = (
                "Là où l’îlot de chaleur est fort, le revêtement et le déficit de verdure expliquent en "
                "général le haut du classement, et le dessin urbain peut encore refroidir. Là où "
                "l’environnement est lui-même chaud, la géographie et le climat pèsent plus."
            )
            rank_units = (
                f"Le classement des subdivisions politiques place les {ulabels} de {name} à côté des "
                "districts et délégations des autres villes de l’indice."
            )
            rank_soil = ""
            subdiv_h = ""
            subdiv_p = ""
    else:
        intro_p1 = (
            "El incremento sostenido de la temperatura media y de su variabilidad —más días extremos, olas "
            "más largas— recae sobre los asentamientos humanos. El cuerpo disipa calor por radiación, "
            "convección y, sobre todo, evaporación del sudor. Cuando el aire y las superficies que irradian "
            "impiden esa disipación, sube la temperatura corporal, el corazón se esfuerza más para llevar "
            "sangre a la piel y se pierden agua y electrolitos. El desenlace puede ser agotamiento, golpe "
            "de calor o descompensación cardiovascular y renal. El calor nocturno, típico de las islas "
            "urbanas, reduce la recuperación del sueño. El riesgo es mayor en personas mayores, con "
            "enfermedad crónica, quienes trabajan al aire libre y quienes habitan viviendas mal ventiladas "
            "o sin sombra."
        )
        intro_p2 = (
            "El propósito de este índice es cuantificar esa carga de calor en la superficie urbana y "
            "hacerla comparable, para entender dónde se concentra la vulnerabilidad y qué rasgos de la "
            "ciudad la propician: pavimento, naves, déficit de verdor e islas de calor respecto al entorno. "
            "No sustituye demografía ni vigilancia epidemiológica; ordena el territorio por exposición de "
            "superficie, con una métrica fija entre ciudades."
        )
        intro_p3 = (
            f"La lectura comparada opera en dos escalas. Entre ciudades, un mismo número permite "
            f"dimensionar el problema frente a otras que ya aplican buenas prácticas o ilustran soluciones "
            f"a la concentración de calor. Dentro de cada ciudad, las divisiones político-administrativas "
            f"—en {name}, las {ulabels}— localizan las zonas más problemáticas con más detalle y señalan "
            f"autoridades y población con interés directo en atenderlas."
        )
        intro_p4 = (
            "Por disponibilidad de datos y por comparabilidad nos concentramos en cuatro capas Landsat. "
            "Tres son de temperatura de superficie: el máximo del periodo, el promedio de las observaciones "
            "y la isla de calor, el diferencial entre una zona de referencia cercana, rural o menos "
            "urbanizada, y la temperatura en la zona. La cuarta es un índice de vegetación (NDVI) que entra "
            "invertido: se castiga menor verdor, porque la vegetación tiene un efecto claro de enfriamiento."
        )
        who = name[:1].upper() + name[1:] if name else name
        rank_h = "2. Posición en el índice"
        rank_city = (
            f"{who} ocupa el lugar {rank} de {n_cities} ciudades medidas en abril y mayo de 2026, "
            f"con un Índice de Vulnerabilidad Climática (IVC) de {ivc:.1f} sobre 100. Encabezan {lead_txt}. "
            f"{f'{nxt_name} ({nxt_ivc:.1f}) queda a continuación. ' if nxt else ''}"
            f"Lo que distingue a {name} no es ser el desierto más caliente, sino la isla de calor más "
            f"marcada de la muestra: la superficie urbana está unos {abs(suhi):.0f} °C por encima de una "
            f"zona de referencia cercana, más fresca."
        )
        if slug == "cdmx":
            rank_alc = (
                f"Dentro de la ciudad el índice se concentra en el oriente y el norte, donde casi todo el "
                f"suelo es urbano. {hottest.unit} encabeza (IVC {hottest.ivc:.0f}): aquí están el Aeropuerto "
                f"Internacional de la Ciudad de México (AICM), la Terminal de Autobuses de Pasajeros de "
                f"Oriente (TAPO) y la Ciudad Deportiva. {top_rows[1].unit} ({top_rows[1].ivc:.0f}), la "
                f"alcaldía más pequeña y enteramente urbana, sigue con el Centro de Transferencia Modal "
                f"(CETRAM) Pantitlán. {top_rows[2].unit} ({top_rows[2].ivc:.0f}) aporta la mayor masa urbana "
                f"y la Central de Abasto. {top_rows[3].unit} ({top_rows[3].ivc:.0f}) suma naves y patios en "
                f"Vallejo y El Rosario. {top_rows[4].unit} ({top_rows[4].ivc:.0f}) aporta el centro histórico "
                f"y La Merced."
            )
            rank_why = (
                f"Esa concentración en los primeros lugares se explica por la forma urbana, no por la "
                f"latitud: losa, terminales, naves y poca vegetación. Son islas de calor que pueden "
                f"atenderse con sombra, techos fríos, arbolado y menos pavimento.\n\n"
                f"{df.iloc[5].unit} ({df.iloc[5].ivc:.0f}) figura entre las alcaldías de mayor índice por "
                f"el poblado, aunque las chinampas reduzcan la media de la alcaldía. {df.iloc[6].unit} "
                f"({df.iloc[6].ivc:.0f}) aparece por Indios Verdes y la Central del Norte, aunque la ladera "
                f"norte reduzca la media.\n\n"
                f"En Ahmedabad o Riad el clima pesa más: el entorno rural ya registra temperaturas de "
                f"superficie muy altas y el calor de fondo afecta a la ciudad en su conjunto. En la "
                f"Ciudad de México el calor adicional es un diferencial urbano, y por ello admite "
                f"soluciones de diseño de ciudad. {coolest.unit} queda al final ({coolest.ivc:.0f})."
            )
            rank_units = (
                "En el ranking de subdivisiones políticas —alcaldías, distritos y equivalentes de las "
                "18 ciudades del índice— las alcaldías del oriente de la Ciudad de México ocupan los "
                "primeros lugares."
            )
            rank_soil = (
                "El tipo de suelo en las cinco alcaldías con mayor IVC de la ciudad es concreto, "
                "asfalto y azoteas, con poca vegetación. Venustiano Carranza está dominada por las "
                "pistas, plataformas y terminales del AICM, más la TAPO y la losa de la Ciudad "
                "Deportiva; la cobertura del aeropuerto sustituye áreas verdes. Iztacalco es "
                "enteramente urbana: el CETRAM Pantitlán es losa de transbordo y el resto, techos y "
                "viaducto. En Iztapalapa, la Central de Abasto son bodegas de perecederos sobre "
                "patios de asfalto, casi sin árboles. Azcapotzalco suma naves y patios de carga en "
                "Vallejo y El Rosario. Cuauhtémoc aporta piedra y terrazas del centro histórico, "
                "techos de lámina de La Merced y el corredor asfaltado Reforma–Juárez; los parques "
                "son fragmentos que no compensan la losa."
            )
            subdiv_h = "3. Subdivisiones con mayor IVC"
            subdiv_p = (
                f"Entre las {n_units_all} subdivisiones políticas de las 18 ciudades del índice "
                f"comparable, {n_cdmx_top} alcaldías de la Ciudad de México entran al top 25: "
                f"{top25_txt}. Maryvale (Phoenix) se intercala en el 5.° lugar, entre Azcapotzalco y "
                "Cuauhtémoc. La gráfica de componentes muestra por qué el oriente de la ciudad "
                "satura z_SUHI y z_LST máx.: losa y déficit de verdor, no un desierto de fondo. "
                "Coyoacán (29.°) queda justo fuera del top 25."
            )
        else:
            rank_alc = (
                f"Entre los {len(df)} {ulabels}, {hottest.unit} encabeza (IVC {hottest.ivc:.0f}) y "
                f"{coolest.unit} queda al final ({coolest.ivc:.0f})."
            )
            rank_why = (
                "Donde la isla de calor es alta, el pavimento y el déficit de vegetación suelen explicar el "
                "tope de la lista, y el diseño urbano aún puede enfriar. Donde el entorno ya es caliente, "
                "pesan más la geografía y el clima."
            )
            rank_units = (
                f"El ranking de subdivisiones políticas sitúa a los {ulabels} de {name} junto a distritos y "
                "alcaldías de las otras ciudades del índice."
            )
            rank_soil = ""
            subdiv_h = ""
            subdiv_p = ""
    packed = tropical_rank(lang, slug, dict(
        name=name, ulabel=ulabel, ulabels=ulabels,
        hottest=hottest, coolest=coolest, top_rows=top_rows, df=df,
        ivc=ivc, suhi=suhi, t_rural=t_rural, rank=rank, n_cities=n_cities,
        nxt_name=nxt_name, nxt_ivc=nxt_ivc,
        n_units_all=n_units_all, top25_txt=top25_txt, n_top=n_cdmx_top,
        n_units=len(df),
        frac_max=float(meta.get("city_frac_lst_max_43") or 0),
        frac_mean=float(meta.get("city_frac_lst_mean_43") or 0),
    ))
    if packed:
        rank_city = packed.get("rank_city") or rank_city
        rank_alc = packed["rank_alc"]
        rank_why = packed["rank_why"]
        rank_soil = packed["rank_soil"]
        subdiv_h = packed["subdiv_h"]
        subdiv_p = packed["subdiv_p"]
    if lang == "en":
        cover_cap = "Surface heat island and borough boundaries."
        cap_city_comp = "Index components by city."
        cap_unit_top = "Highest-scoring political subdivisions in the index."
        cap_unit_comp = "Index components of the highest-scoring subdivisions."
    elif lang == "fr":
        cover_cap = "Îlot de chaleur de surface et limites des délégations."
        cap_city_comp = "Composantes de l’indice par ville."
        cap_unit_top = "Subdivisions politiques les mieux classées dans l’indice."
        cap_unit_comp = "Composantes de l’indice des subdivisions les mieux classées."
    else:
        cover_cap = "Isla de calor de superficie y división por alcaldías."
        cap_city_comp = "Componentes del índice por ciudad."
        cap_unit_top = "Subdivisiones políticas con el índice más alto."
        cap_unit_comp = "Componentes del índice de las subdivisiones mejor clasificadas."
    if slug == "ahmedabad":
        cover_cap = {
            "en": "Surface heat island and taluka boundaries.",
            "fr": "Îlot de chaleur de surface et limites des talukas.",
        }.get(lang, "Isla de calor de superficie y división por talukas.")
    elif slug == "phoenix":
        cover_cap = {
            "en": "Surface heat island and urban-village boundaries.",
            "fr": "Îlot de chaleur de surface et limites des villages urbains.",
        }.get(lang, "Isla de calor de superficie y división por urban villages.")
    return dict(
        intro_p1=intro_p1, intro_p2=intro_p2, intro_p3=intro_p3, intro_p4=intro_p4,
        rank_h=rank_h, rank_city=rank_city, rank_alc=rank_alc, rank_why=rank_why,
        rank_units=rank_units, rank_soil=rank_soil,
        subdiv_h=subdiv_h, subdiv_p=subdiv_p,
        cap_city_comp=cap_city_comp, cap_unit_top=cap_unit_top, cap_unit_comp=cap_unit_comp,
        n_cities=n_cities, city_rank=rank, cover_cap=cover_cap,
    )

WHY = {
    1: {
        "es": (
            "Estas ciudades son la Prioridad 1 de un recorte explícito: más de dos millones de habitantes "
            "en la franja 18–42 °N, el mismo cinturón latitudinal en el que el proyecto ya mide islas de calor. "
            "No se eligieron por ser las más calientes del planeta, sino por el producto peligro × exposición × "
            "vulnerabilidad. IPCC, OMS/OMM, el índice GUHVI (2025) y el ranking Oxford 2026 (205 ciudades de más "
            "de un millón) coinciden en ese marco: Riad o Dubai tienen picos brutales y mucha refrigeración; "
            "Karachi o Delhi tienen menos capacidad de afrontamiento y más mortalidad esperada. Oxford concentra "
            "más del 95 % de las peor rankeadas en Sur/Sureste de Asia y África; Basora, vecina de Bagdad, es la "
            "ciudad de mayor riesgo de esa lista.",
            "Dentro de esa franja, Prioridad 1 cubre cuatro climas que el índice Landsat debe distinguir con la "
            "misma métrica ivc-l4-v1: el pre-monzón seco de Delhi (la mayor población expuesta a olas de calor), "
            "el árido de El Cairo y Bagdad (picos de LST entre los más altos; El Cairo entra en el top 50 Oxford), "
            "el húmedo costero de Karachi (ola mortal de 2015; Mora et al.: condiciones equivalentes podrían "
            "volverse anuales a +2 °C) y dos anclas del proyecto —Ciudad de México en el borde sur, aire fresco "
            "por altitud pero LST urbana por encima de 60 °C, y Madrid en el borde norte, mediterráneo interior "
            "con olas e incremento relativo rápido, ya en la franja Fra-Spa-Por. Abril–mayo de 2026 es la ventana "
            "común a propósito: en Delhi y Karachi es el pico pre-monzón; en El Cairo y Bagdad ya hay calor "
            "intenso; en Madrid y CDMX es primavera, no el máximo anual. Se mantiene para que un IVC 60 en un "
            "distrito sea comparable entre ciudades.",
        ),
        "en": (
            "These cities are Priority 1 of an explicit cut: more than two million inhabitants in the 18–42 °N "
            "band, the same latitudinal belt where the project already maps heat islands. They were not chosen "
            "for being the hottest places on Earth, but for the product hazard × exposure × vulnerability. "
            "IPCC, WHO/WMO, the GUHVI index (2025) and the Oxford 2026 ranking (205 cities of more than one "
            "million) share that frame: Riyadh or Dubai have brutal peaks and abundant cooling; Karachi or Delhi "
            "have less coping capacity and higher expected mortality. Oxford concentrates more than 95% of the "
            "worst-ranked cities in South/Southeast Asia and Africa; Basra, next to Baghdad, is the highest-risk "
            "city on that list.",
            "Within that band, Priority 1 covers four climates that the Landsat index must distinguish with the "
            "same ivc-l4-v1 metric: Delhi’s dry pre-monsoon (the largest population exposed to heatwaves), the "
            "arid climates of Cairo and Baghdad (among the highest LST peaks; Cairo is in the Oxford top 50), "
            "Karachi’s humid coast (the deadly 2015 heatwave; Mora et al.: equivalent conditions could become "
            "annual at +2 °C) and two project anchors — Mexico City on the southern edge, cooler air from "
            "altitude but urban LST above 60 °C, and Madrid on the northern edge, inland Mediterranean with "
            "heatwaves and a fast relative rise, already in the Fra-Spa-Por strip. April–May 2026 is the common "
            "window on purpose: in Delhi and Karachi it is the pre-monsoon peak; in Cairo and Baghdad heat is "
            "already intense; in Madrid and Mexico City it is spring, not the annual maximum. It is kept so that "
            "an IVC of 60 in one district is comparable across cities.",
        ),
        "fr": (
            "Ces villes sont la Priorité 1 d’un découpage explicite : plus de deux millions d’habitants dans la "
            "bande 18–42 °N, le même fuseau latitudinal où le projet cartographie déjà les îlots de chaleur. "
            "Elles n’ont pas été choisies pour être les plus chaudes de la planète, mais pour le produit "
            "danger × exposition × vulnérabilité. Le GIEC, l’OMS/OMM, l’indice GUHVI (2025) et le classement "
            "Oxford 2026 (205 villes de plus d’un million) partagent ce cadre : Riyad ou Dubaï ont des pics "
            "brutaux et beaucoup de climatisation ; Karachi ou Delhi ont moins de capacité d’adaptation et une "
            "mortalité attendue plus élevée. Oxford concentre plus de 95 % des villes les plus mal classées en "
            "Asie du Sud/Sud-Est et en Afrique ; Bassora, voisine de Bagdad, est la ville au risque le plus "
            "élevé de cette liste.",
            "Dans cette bande, la Priorité 1 couvre quatre climats que l’indice Landsat doit distinguer avec la "
            "même métrique ivc-l4-v1 : le pré-mousson sec de Delhi (la plus grande population exposée aux "
            "vagues de chaleur), l’aride du Caire et de Bagdad (pics de LST parmi les plus hauts ; Le Caire "
            "entre dans le top 50 Oxford), le littoral humide de Karachi (canicule meurtrière de 2015 ; Mora "
            "et al. : des conditions équivalentes pourraient devenir annuelles à +2 °C) et deux ancres du "
            "projet — Mexico au bord sud, air plus frais par l’altitude mais LST urbaine au-dessus de 60 °C, "
            "et Madrid au bord nord, méditerranéen intérieur avec vagues de chaleur et hausse relative rapide, "
            "déjà dans la frange Fra-Spa-Por. Avril–mai 2026 est la fenêtre commune à dessein : à Delhi et "
            "Karachi c’est le pic de pré-mousson ; au Caire et à Bagdad la chaleur est déjà intense ; à Madrid "
            "et Mexico c’est le printemps, pas le maximum annuel. On la conserve pour qu’un IVC 60 dans un "
            "district soit comparable d’une ville à l’autre.",
        ),
    },
    2: {
        "es": (
            "Prioridad 2 sigue el mismo recorte —más de dos millones de habitantes en 18–42 °N— y el mismo "
            "marco peligro × exposición × vulnerabilidad, un peldaño por debajo de las seis de cabecera. "
            "No sustituye a Delhi o Karachi: las complementa. Lahore, Dhaka y Ahmedabad concentran el "
            "crecimiento de persona-días de calor extremo en Sur de Asia (Tuholske 2021); Phoenix es el "
            "referente ECOSTRESS de quemaduras por pavimento (49–60 °C) ya usado en el estilo cartográfico "
            "del proyecto; Teherán aporta una megaciudad semiárida de cuenca cerrada; Monterrey es el par "
            "seco-industrial de la Ciudad de México.",
            "La métrica es la misma ivc-l4-v1 y la ventana sigue siendo abril–mayo de 2026, para que un IVC 60 "
            "en un town de Lahore sea comparable a Iztapalapa o a un urban village de Phoenix. En Lahore, "
            "Ahmedabad y Dhaka esa ventana es pre-monzón o temporada caliente. En Phoenix y Monterrey el "
            "máximo anual es junio–agosto; entran a propósito en primavera para no romper la escala fija. "
            "Ahmedabad, además, tiene un plan de acción térmica pionero en India: el índice mide exposición "
            "de superficie, no el éxito del plan.",
        ),
        "en": (
            "Priority 2 follows the same cut — more than two million inhabitants in 18–42 °N — and the same "
            "hazard × exposure × vulnerability frame, one step below the six headline cities. It does not "
            "replace Delhi or Karachi: it complements them. Lahore, Dhaka and Ahmedabad concentrate the growth "
            "of extreme-heat person-days in South Asia (Tuholske 2021); Phoenix is the ECOSTRESS reference for "
            "pavement burns (49–60 °C) already used in the project’s map style; Tehran adds a semi-arid "
            "megacity in a closed basin; Monterrey is Mexico City’s dry-industrial counterpart.",
            "The metric is the same ivc-l4-v1 and the window remains April–May 2026, so that an IVC of 60 in a "
            "Lahore town is comparable to Iztapalapa or to a Phoenix urban village. In Lahore, Ahmedabad and "
            "Dhaka that window is pre-monsoon or hot season. In Phoenix and Monterrey the annual peak is "
            "June–August; they enter in spring on purpose so as not to break the fixed scale. Ahmedabad also "
            "has a pioneering heat-action plan in India: the index measures surface exposure, not the plan’s "
            "success.",
        ),
        "fr": (
            "La Priorité 2 suit le même découpage — plus de deux millions d’habitants en 18–42 °N — et le même "
            "cadre danger × exposition × vulnérabilité, un cran sous les six villes de tête. Elle ne remplace "
            "pas Delhi ou Karachi : elle les complète. Lahore, Dhaka et Ahmedabad concentrent la croissance "
            "des personne-jours de chaleur extrême en Asie du Sud (Tuholske 2021) ; Phoenix est la référence "
            "ECOSTRESS des brûlures sur chaussée (49–60 °C) déjà utilisée dans le style cartographique du "
            "projet ; Téhéran apporte une mégapole semi-aride en bassin fermé ; Monterrey est le pendant "
            "sec-industriel de Mexico.",
            "La métrique est la même ivc-l4-v1 et la fenêtre reste avril–mai 2026, pour qu’un IVC 60 dans un "
            "town de Lahore soit comparable à Iztapalapa ou à un urban village de Phoenix. À Lahore, Ahmedabad "
            "et Dhaka cette fenêtre est pré-mousson ou saison chaude. À Phoenix et Monterrey le maximum annuel "
            "est juin–août ; elles entrent au printemps à dessein pour ne pas casser l’échelle fixe. Ahmedabad "
            "a en outre un plan d’action chaleur pionnier en Inde : l’indice mesure l’exposition de surface, "
            "pas le succès du plan.",
        ),
    },
    3: {
        "es": (
            "Prioridad 3 cierra el recorte de más de dos millones en 18–42 °N con contrastes de capacidad "
            "de afrontamiento, no con las ciudades más calientes que queden. Riad tiene picos de desierto "
            "y mucha refrigeración: sirve de contraste frente a Bagdad o El Cairo. Houston aporta calor "
            "húmedo estadounidense; Wuhan, una ciudad-horno de cuenca en China; Barcelona y Roma anclan "
            "el Mediterráneo costero e interior frente a Madrid; Casablanca pone el Magreb en la misma "
            "latitud que Phoenix, con menos capacidad de adaptación que Europa.",
            "La métrica sigue siendo ivc-l4-v1 y la ventana abril–mayo de 2026. En Riad y Casablanca esa "
            "ventana ya es temporada caliente. En Houston y Wuhan el pico suele ser julio–agosto; en "
            "Barcelona y Roma es primavera, como en Madrid. Entran a propósito en la misma escala fija, "
            "para que un IVC 60 en un distrito de Houston o un municipio de Roma sea comparable a "
            "Iztapalapa o a un urban village de Phoenix.",
        ),
        "en": (
            "Priority 3 closes the cut of more than two million people in 18–42 °N with contrasts of coping "
            "capacity, not with whatever hottest cities remain. Riyadh has desert peaks and abundant cooling: "
            "it is the contrast to Baghdad or Cairo. Houston adds humid U.S. heat; Wuhan, a furnace city in "
            "a Chinese river basin; Barcelona and Rome anchor the coastal and inland Mediterranean against "
            "Madrid; Casablanca puts the Maghreb on the same latitude as Phoenix, with less adaptive capacity "
            "than Europe.",
            "The metric remains ivc-l4-v1 and the window April–May 2026. In Riyadh and Casablanca that window "
            "is already hot season. In Houston and Wuhan the peak is usually July–August; in Barcelona and "
            "Rome it is spring, as in Madrid. They enter on purpose on the same fixed scale, so that an IVC "
            "of 60 in a Houston district or a Rome municipio is comparable to Iztapalapa or a Phoenix urban "
            "village.",
        ),
        "fr": (
            "La Priorité 3 referme le découpage de plus de deux millions d’habitants en 18–42 °N par des "
            "contrastes de capacité d’adaptation, non par les villes les plus chaudes qui restent. Riyad a "
            "des pics désertiques et beaucoup de climatisation : c’est le contraste de Bagdad ou du Caire. "
            "Houston apporte la chaleur humide américaine ; Wuhan, une ville-fournaise en bassin chinois ; "
            "Barcelone et Rome ancrent la Méditerranée côtière et intérieure face à Madrid ; Casablanca "
            "place le Maghreb à la même latitude que Phoenix, avec moins de capacité d’adaptation que l’Europe.",
            "La métrique reste ivc-l4-v1 et la fenêtre avril–mai 2026. À Riyad et Casablanca cette fenêtre "
            "est déjà la saison chaude. À Houston et Wuhan le pic est plutôt juillet–août ; à Barcelone et "
            "Rome c’est le printemps, comme à Madrid. Elles entrent à dessein sur la même échelle fixe, pour "
            "qu’un IVC 60 dans un district de Houston ou un municipio de Rome soit comparable à Iztapalapa "
            "ou à un urban village de Phoenix.",
        ),
    },
    4: {
        "es": (
            "Prioridad 4 abre el índice más allá de la franja 18–42 °N: megaciudades tropicales, "
            "australes, ecuatoriales y de latitud alta, más las capitales europeas y Tokio que "
            "faltaban como reporte de subdivisiones. La métrica sigue siendo ivc-l4-v1 y la ventana "
            "abril–mayo de 2026, a propósito: en Mumbai o Singapur esa ventana es caliente; en Lagos, "
            "São Paulo, Santiago y Johannesburgo no es el pico anual. Sirve para leer un IVC 60 junto "
            "a Iztapalapa o un distrito de Madrid, no para coronar la ciudad más caliente del año.",
            "Dentro de cada ciudad el recorte son subdivisiones políticas oficiales —LGAs, "
            "subprefecturas, comunas, Bezirke, arrondissements, ku— para que sombra, pavimento y "
            "respuesta al calor se discutan en el grano en el que se deciden.",
        ),
        "en": (
            "Priority 4 opens the index beyond the 18–42 °N band: tropical, southern-hemisphere, "
            "equatorial and high-latitude megacities, plus the European capitals and Tokyo that still "
            "lacked a subdivision report. The metric remains ivc-l4-v1 and the window April–May 2026 "
            "on purpose: in Mumbai or Singapore that window is hot; in Lagos, São Paulo, Santiago and "
            "Johannesburg it is not the annual peak. It is there to read an IVC of 60 next to "
            "Iztapalapa or a Madrid district, not to crown the hottest city of the year.",
            "Inside each city the cut is official political subdivisions — LGAs, subprefectures, "
            "comunas, Bezirke, arrondissements, ku — so that shade, paving and heat response are "
            "discussed at the grain at which they are decided.",
        ),
        "fr": (
            "La Priorité 4 ouvre l’indice au-delà de la bande 18–42 °N : mégapoles tropicales, "
            "australes, équatoriales et de haute latitude, plus les capitales européennes et Tokyo "
            "qui n’avaient pas encore de rapport par subdivision. La métrique reste ivc-l4-v1 et la "
            "fenêtre avril–mai 2026 à dessein : à Mumbai ou Singapour cette fenêtre est chaude ; à "
            "Lagos, São Paulo, Santiago et Johannesburg ce n’est pas le pic annuel. Il s’agit de lire "
            "un IVC 60 à côté d’Iztapalapa ou d’un district de Madrid, non de couronner la ville la "
            "plus chaude de l’année.",
            "Dans chaque ville le découpage est celui des subdivisions politiques officielles — LGA, "
            "sous-préfectures, comunas, Bezirke, arrondissements, ku — pour que l’ombre, le revêtement "
            "et la réponse à la chaleur se discutent au grain où elles se décident.",
        ),
    },
}

CITY_I18N = {
    "cdmx": {
        "name": {"es": "la Ciudad de México", "en": "Mexico City", "fr": "Mexico"},
        "country": {"es": "México", "en": "Mexico", "fr": "Mexique"},
        "unit": {"es": ("alcaldía", "alcaldías"), "en": ("borough", "boroughs"), "fr": ("délégation", "délégations")},
        "pdf": {"es": "CDMX", "en": "Mexico_City", "fr": "Mexico"},
        "why": {
            "es": (
                "Ciudad de México ancla el borde sur de la franja: aire más fresco por altitud, pero LST urbana "
                "que llega a superar 60 °C en alcaldías centrales. Ya estaba en el proyecto; Prioridad 1 la "
                "mantiene como referencia para comparar alcaldías con distritos de Delhi, El Cairo, Karachi, "
                "Bagdad y Madrid bajo la misma métrica."
            ),
            "en": (
                "Mexico City anchors the southern edge of the band: cooler air from altitude, but urban LST that "
                "can exceed 60 °C in central boroughs. It was already in the project; Priority 1 keeps it as the "
                "reference for comparing boroughs with districts of Delhi, Cairo, Karachi, Baghdad and Madrid "
                "under the same metric."
            ),
            "fr": (
                "Mexico ancre le bord sud de la bande : air plus frais grâce à l’altitude, mais une LST urbaine "
                "qui dépasse 60 °C dans les délégations centrales. Elle était déjà dans le projet ; la Priorité 1 "
                "la conserve comme référence pour comparer les délégations aux districts de Delhi, du Caire, de "
                "Karachi, de Bagdad et de Madrid sous la même métrique."
            ),
        },
    },
    "delhi": {
        "name": {"es": "Delhi", "en": "Delhi", "fr": "Delhi"},
        "country": {"es": "India", "en": "India", "fr": "Inde"},
        "unit": {"es": ("distrito", "distritos"), "en": ("district", "districts"), "fr": ("district", "districts")},
        "why": {
            "es": (
                "Delhi es la mayor ciudad de la franja por población expuesta: megaciudad del pre-monzón "
                "seco, trabajo al aire libre y enfriamiento desigual. Abril–mayo coincide aquí con el "
                "pico de calor previo al monzón, así que el IVC no está mirando un hombro de la temporada, "
                "sino el momento en que la superficie urbana más aprieta."
            ),
            "en": (
                "Delhi is the largest city in the band by exposed population: a dry pre-monsoon megacity, outdoor "
                "work and uneven cooling. April–May coincides here with the heat peak before the monsoon, so the "
                "IVC is not looking at a shoulder of the season but at the moment when the urban surface is "
                "tightest."
            ),
            "fr": (
                "Delhi est la plus grande ville de la bande par population exposée : mégapole de pré-mousson "
                "sèche, travail en extérieur et rafraîchissement inégal. Avril–mai coïncide ici avec le pic de "
                "chaleur avant la mousson, donc l’IVC ne regarde pas un flanc de saison mais le moment où la "
                "surface urbaine serre le plus."
            ),
        },
    },
    "cairo": {
        "name": {"es": "El Cairo", "en": "Cairo", "fr": "Le Caire"},
        "country": {"es": "Egipto", "en": "Egypt", "fr": "Égypte"},
        "unit": {"es": ("distrito", "distritos"), "en": ("district", "districts"), "fr": ("district", "districts")},
        "pdf": {"es": "El_Cairo", "en": "Cairo", "fr": "Le_Caire"},
        "why": {
            "es": (
                "El Cairo es la megaciudad árida de referencia en África del Norte: Oxford 2026 la coloca "
                "en el top 50 de riesgo térmico. El gobernorado incluye el núcleo denso (Abdin, Bulaq) y "
                "ciudades nuevas al este (New Cairo, Badr, El Shorouk); el índice sirve precisamente para "
                "ver si ese crecimiento desértico replica la isla de calor del centro."
            ),
            "en": (
                "Cairo is the arid megacity of record in North Africa: Oxford 2026 places it in the thermal-risk "
                "top 50. The governorate includes the dense core (Abdin, Bulaq) and new towns to the east "
                "(New Cairo, Badr, El Shorouk); the index is there to see whether that desert growth copies the "
                "heat island of the centre."
            ),
            "fr": (
                "Le Caire est la mégapole aride de référence en Afrique du Nord : Oxford 2026 la place dans le "
                "top 50 du risque thermique. Le gouvernorat inclut le noyau dense (Abdin, Bulaq) et des villes "
                "nouvelles à l’est (New Cairo, Badr, El Shorouk) ; l’indice sert précisément à voir si cette "
                "croissance désertique reproduit l’îlot de chaleur du centre."
            ),
        },
    },
    "karachi": {
        "name": {"es": "Karachi", "en": "Karachi", "fr": "Karachi"},
        "country": {"es": "Pakistán", "en": "Pakistan", "fr": "Pakistan"},
        "unit": {"es": ("town", "towns"), "en": ("town", "towns"), "fr": ("town", "towns")},
        "why": {
            "es": (
                "Karachi combina calor húmedo costero con muy baja capacidad de afrontamiento: la ola de "
                "2015 mató a más de mil personas, y Mora et al. advierten que condiciones equivalentes "
                "podrían volverse anuales a +2 °C. Los towns y cantonments permiten separar el puerto, "
                "los asentamientos densos y la periferia de Gadap."
            ),
            "en": (
                "Karachi combines humid coastal heat with very low coping capacity: the 2015 heatwave killed "
                "more than a thousand people, and Mora et al. warn that equivalent conditions could become "
                "annual at +2 °C. Towns and cantonments make it possible to separate the port, the dense "
                "settlements and the Gadap periphery."
            ),
            "fr": (
                "Karachi combine une chaleur côtière humide et une très faible capacité d’adaptation : la "
                "canicule de 2015 a tué plus de mille personnes, et Mora et al. avertissent que des conditions "
                "équivalentes pourraient devenir annuelles à +2 °C. Les towns et cantonments permettent de "
                "séparer le port, les peuplements denses et la périphérie de Gadap."
            ),
        },
    },
    "baghdad": {
        "name": {"es": "Bagdad", "en": "Baghdad", "fr": "Bagdad"},
        "country": {"es": "Irak", "en": "Iraq", "fr": "Irak"},
        "unit": {"es": ("distrito", "distritos"), "en": ("district", "districts"), "fr": ("district", "districts")},
        "pdf": {"es": "Bagdad", "en": "Baghdad", "fr": "Bagdad"},
        "why": {
            "es": (
                "Bagdad aporta los picos de LST entre los más altos del planeta en la franja. La gobernación "
                "se analiza en los cuatro distritos ADM2 de geoBoundaries (Karkh, Risafa, Adhamiya, Thawra). "
                "Basora, cercana, es la ciudad de mayor riesgo Oxford 2026: Bagdad es el ancla urbana de ese "
                "corredor mesopotámico."
            ),
            "en": (
                "Baghdad contributes some of the highest LST peaks on the planet in this band. The governorate "
                "is analysed in the four geoBoundaries ADM2 districts (Karkh, Risafa, Adhamiya, Thawra). Nearby "
                "Basra is the highest-risk Oxford 2026 city: Baghdad is the urban anchor of that Mesopotamian "
                "corridor."
            ),
            "fr": (
                "Bagdad apporte des pics de LST parmi les plus élevés de la planète dans cette bande. Le "
                "gouvernorat est analysé en quatre districts ADM2 de geoBoundaries (Karkh, Risafa, Adhamiya, "
                "Thawra). Bassora, toute proche, est la ville au plus fort risque Oxford 2026 : Bagdad est "
                "l’ancre urbaine de ce corridor mésopotamien."
            ),
        },
    },
    "madrid": {
        "name": {"es": "Madrid", "en": "Madrid", "fr": "Madrid"},
        "country": {"es": "España", "en": "Spain", "fr": "Espagne"},
        "unit": {"es": ("distrito", "distritos"), "en": ("district", "districts"), "fr": ("district", "districts")},
        "why": {
            "es": (
                "Madrid cierra la franja por el norte: mediterráneo interior, ya en el recorte Fra-Spa-Por "
                "del proyecto, con olas de calor e incremento relativo rápido. Abril–mayo no es su máximo "
                "anual (eso es julio–agosto); entra para anclar la métrica en una capital europea con 21 "
                "distritos municipales comparables a las alcaldías de CDMX."
            ),
            "en": (
                "Madrid closes the band to the north: inland Mediterranean, already in the project’s Fra-Spa-Por "
                "cut, with heatwaves and a fast relative rise. April–May is not its annual peak (that is "
                "July–August); it enters to anchor the metric in a European capital with 21 municipal districts "
                "comparable to Mexico City boroughs."
            ),
            "fr": (
                "Madrid ferme la bande au nord : méditerranéen intérieur, déjà dans le découpage Fra-Spa-Por du "
                "projet, avec vagues de chaleur et hausse relative rapide. Avril–mai n’est pas son maximum "
                "annuel (c’est juillet–août) ; elle entre pour ancrer la métrique dans une capitale européenne "
                "à 21 districts municipaux comparables aux délégations de Mexico."
            ),
        },
    },
    "lahore": {
        "name": {"es": "Lahore", "en": "Lahore", "fr": "Lahore"},
        "country": {"es": "Pakistán", "en": "Pakistan", "fr": "Pakistan"},
        "unit": {"es": ("tehsil", "tehsiles"), "en": ("tehsil", "tehsils"), "fr": ("tehsil", "tehsils")},
        "why": {
            "es": (
                "Lahore es la segunda megaciudad de Pakistán: crecimiento urbano rápido, olas pre-monzón "
                "y poca capacidad de afrontamiento. El distrito se parte en dos tehsiles ADM3 (Lahore City "
                "y Lahore Cantt). Abril–mayo coincide con el pico previo al monzón, como en Delhi y Karachi."
            ),
            "en": (
                "Lahore is Pakistan’s second megacity: rapid urban growth, pre-monsoon heatwaves and little "
                "coping capacity. The district splits into two ADM3 tehsils (Lahore City and Lahore Cantt). "
                "April–May coincides with the pre-monsoon peak, as in Delhi and Karachi."
            ),
            "fr": (
                "Lahore est la deuxième mégapole du Pakistan : croissance urbaine rapide, vagues de pré-mousson "
                "et faible capacité d’adaptation. Le district se partage en deux tehsils ADM3 (Lahore City et "
                "Lahore Cantt). Avril–mai coïncide avec le pic avant la mousson, comme à Delhi et Karachi."
            ),
        },
    },
    "ahmedabad": {
        "name": {"es": "Ahmedabad", "en": "Ahmedabad", "fr": "Ahmedabad"},
        "country": {"es": "India", "en": "India", "fr": "Inde"},
        "unit": {"es": ("taluka", "talukas"), "en": ("taluka", "talukas"), "fr": ("taluka", "talukas")},
        "why": {
            "es": (
                "Ahmedabad es el referente indio de adaptación: tuvo el primer plan de acción térmica del "
                "país, pero la exposición de superficie sigue siendo muy alta. El recorte usa las talukas "
                "del distrito a menos de 55 km del centro (Sabarmati, Daskroi, Sanand y periurbano), no el "
                "SIR de Dholera. El IVC mide calor de superficie, no el éxito del plan."
            ),
            "en": (
                "Ahmedabad is India’s adaptation benchmark: it had the country’s first heat-action plan, but "
                "surface exposure remains very high. The cut uses district talukas within 55 km of the centre "
                "(Sabarmati, Daskroi, Sanand and peri-urban land), not the Dholera SIR. The IVC measures "
                "surface heat, not the plan’s success."
            ),
            "fr": (
                "Ahmedabad est le référent indien de l’adaptation : elle a eu le premier plan d’action chaleur "
                "du pays, mais l’exposition de surface reste très élevée. Le découpage utilise les talukas du "
                "district à moins de 55 km du centre (Sabarmati, Daskroi, Sanand et périurbain), pas le SIR de "
                "Dholera. L’IVC mesure la chaleur de surface, pas le succès du plan."
            ),
        },
    },
    "dhaka": {
        "name": {"es": "Dhaka", "en": "Dhaka", "fr": "Dhaka"},
        "country": {"es": "Bangladés", "en": "Bangladesh", "fr": "Bangladesh"},
        "unit": {"es": ("thana", "thanas"), "en": ("thana", "thanas"), "fr": ("thana", "thanas")},
        "why": {
            "es": (
                "Dhaka es, en Tuholske 2021, la ciudad con mayor aumento de persona-días de calor extremo, "
                "sobre todo por crecimiento demográfico. Se analizan las thanas del distrito urbano "
                "(sin upazilas rurales de Savar, Keraniganj, Dhamrai, Dohar y Nawabganj). El clima es "
                "húmedo subtropical: el NDVI y el SUHI pesan distinto que en el desierto de Phoenix."
            ),
            "en": (
                "In Tuholske 2021, Dhaka is the city with the largest rise in extreme-heat person-days, mainly "
                "from demographic growth. The analysis uses thanas of the urban district (without the rural "
                "upazilas of Savar, Keraniganj, Dhamrai, Dohar and Nawabganj). The climate is humid subtropical: "
                "NDVI and SUHI weigh differently than in the Phoenix desert."
            ),
            "fr": (
                "Chez Tuholske 2021, Dhaka est la ville au plus fort accroissement de personne-jours de chaleur "
                "extrême, surtout par croissance démographique. On analyse les thanas du district urbain (sans "
                "les upazilas rurales de Savar, Keraniganj, Dhamrai, Dohar et Nawabganj). Le climat est "
                "subtropical humide : le NDVI et le SUHI pèsent autrement que dans le désert de Phoenix."
            ),
        },
    },
    "phoenix": {
        "name": {"es": "Phoenix", "en": "Phoenix", "fr": "Phoenix"},
        "country": {"es": "Estados Unidos", "en": "United States", "fr": "États-Unis"},
        "unit": {"es": ("urban village", "urban villages"), "en": ("urban village", "urban villages"), "fr": ("village urbain", "villages urbains")},
        "why": {
            "es": (
                "Phoenix es el referente de calor de pavimento en desierto: LST urbana de 49–60 °C en el "
                "núcleo, con poco dosel. Los 15 urban villages del ayuntamiento permiten ver si el núcleo "
                "(Central City, Maryvale) se calienta más que el desierto planeado del norte "
                "(Desert View, North Gateway). Abril–mayo no es el pico de julio; entra para anclar la escala."
            ),
            "en": (
                "Phoenix is the desert-pavement heat benchmark: urban LST of 49–60 °C in the core, with little "
                "canopy. The city’s 15 urban villages show whether the core (Central City, Maryvale) "
                "runs hotter than the planned desert of the north (Desert View, North Gateway). April–May is not "
                "the July peak; it enters to anchor the scale."
            ),
            "fr": (
                "Phoenix est le référent de chaleur de chaussée en désert : LST urbaine de 49–60 °C dans le "
                "noyau, avec peu de canopée. Les 15 villages urbains de la ville permettent de voir si le "
                "noyau (Central City, Maryvale) chauffe plus que le désert planifié du nord (Desert View, North "
                "Gateway). Avril–mai n’est pas le pic de juillet ; la ville entre pour ancrer l’échelle."
            ),
        },
    },
    "tehran": {
        "name": {"es": "Teherán", "en": "Tehran", "fr": "Téhéran"},
        "country": {"es": "Irán", "en": "Iran", "fr": "Iran"},
        "unit": {"es": ("distrito", "distritos"), "en": ("district", "districts"), "fr": ("district", "districts")},
        "pdf": {"es": "Teheran", "en": "Tehran", "fr": "Teheran"},
        "why": {
            "es": (
                "Teherán aporta una megaciudad semiárida de altitud, contaminación y cuenca cerrada: el "
                "calor no se ventila. Los 22 distritos municipales (manāteq) van del centro denso al "
                "oeste industrial (21–22) y al piedemonte del Alborz (1 y 3)."
            ),
            "en": (
                "Tehran adds a high-altitude semi-arid megacity, polluted and in a closed basin: the heat does "
                "not ventilate. The 22 municipal districts (manāteq) run from the dense centre to the industrial "
                "west (21–22) and the Alborz piedmont (1 and 3)."
            ),
            "fr": (
                "Téhéran apporte une mégapole semi-aride d’altitude, polluée et en bassin fermé : la chaleur ne "
                "s’évacue pas. Les 22 districts municipaux (manāteq) vont du centre dense à l’ouest industriel "
                "(21–22) et au piémont de l’Alborz (1 et 3)."
            ),
        },
    },
    "monterrey": {
        "name": {"es": "Monterrey", "en": "Monterrey", "fr": "Monterrey"},
        "country": {"es": "México", "en": "Mexico", "fr": "Mexique"},
        "unit": {"es": ("municipio", "municipios"), "en": ("municipality", "municipalities"), "fr": ("municipalité", "municipalités")},
        "why": {
            "es": (
                "Monterrey es el par de CDMX en México: calor seco, industria y expansión sobre el desierto "
                "del noreste. El recorte es el AMM de 13 municipios (de San Pedro Garza García a Pesquería). "
                "El contraste con las alcaldías de CDMX, a la misma métrica y ventana, es el motivo de incluirla."
            ),
            "en": (
                "Monterrey is Mexico City’s counterpart in Mexico: dry heat, industry and expansion over the "
                "northeastern desert. The cut is the 13-municipality AMM (from San Pedro Garza García to "
                "Pesquería). The contrast with Mexico City boroughs, at the same metric and window, is why it "
                "is included."
            ),
            "fr": (
                "Monterrey est le pendant de Mexico au Mexique : chaleur sèche, industrie et expansion sur le "
                "désert du nord-est. Le découpage est l’AMM de 13 municipalités (de San Pedro Garza García à "
                "Pesquería). Le contraste avec les délégations de Mexico, à la même métrique et la même fenêtre, "
                "justifie de l’inclure."
            ),
        },
    },
    "riyadh": {
        "name": {"es": "Riad", "en": "Riyadh", "fr": "Riyad"},
        "country": {"es": "Arabia Saudita", "en": "Saudi Arabia", "fr": "Arabie saoudite"},
        "unit": {"es": ("baladiya", "baladiyat"), "en": ("baladiya", "baladiyat"), "fr": ("baladiya", "baladiyat")},
        "pdf": {"es": "Riad", "en": "Riyadh", "fr": "Riyad"},
        "why": {
            "es": (
                "Riad es el contraste de adaptación del Golfo: picos de LST brutales y mucha "
                "refrigeración. El recorte usa las 14 baladiyat del núcleo (no toda la región). "
                "El IVC mide exposición de superficie, no el aire acondicionado."
            ),
            "en": (
                "Riyadh is the Gulf’s adaptation contrast: brutal LST peaks and abundant cooling. "
                "The cut uses the 14 core baladiyat, not the whole region. The IVC measures "
                "surface exposure, not air conditioning."
            ),
            "fr": (
                "Riyad est le contraste d’adaptation du Golfe : pics de LST brutaux et beaucoup de "
                "climatisation. Le découpage utilise les 14 baladiyat du noyau, pas toute la région. "
                "L’IVC mesure l’exposition de surface, pas la climatisation."
            ),
        },
    },
    "houston": {
        "name": {"es": "Houston", "en": "Houston", "fr": "Houston"},
        "country": {"es": "Estados Unidos", "en": "United States", "fr": "États-Unis"},
        "unit": {"es": ("district", "districts"), "en": ("district", "districts"), "fr": ("district", "districts")},
        "why": {
            "es": (
                "Houston aporta el calor húmedo del Golfo de México: noches cálidas y trabajo al "
                "aire libre. Los 11 distritos del ayuntamiento permiten ver si el este industrial "
                "se calienta más que el oeste arbolado. Abril–mayo no es el pico de agosto."
            ),
            "en": (
                "Houston adds humid heat from the Gulf of Mexico: warm nights and outdoor work. "
                "The city’s 11 council districts show whether the industrial east runs hotter than "
                "the wooded west. April–May is not the August peak."
            ),
            "fr": (
                "Houston apporte la chaleur humide du golfe du Mexique : nuits chaudes et travail "
                "en extérieur. Les 11 districts municipaux permettent de voir si l’est industriel "
                "chauffe plus que l’ouest boisé. Avril–mai n’est pas le pic d’août."
            ),
        },
    },
    "wuhan": {
        "name": {"es": "Wuhan", "en": "Wuhan", "fr": "Wuhan"},
        "country": {"es": "China", "en": "China", "fr": "Chine"},
        "unit": {"es": ("distrito", "distritos"), "en": ("district", "districts"), "fr": ("district", "districts")},
        "why": {
            "es": (
                "Wuhan es una de las ciudades-horno de China: humedad y estancamiento en la cuenca "
                "del Yangtsé. Los distritos ADM3 van de Wuchang y Hankou al periurbano de Huangpi "
                "y Jiangxia. La ventana de primavera no es el pico de julio; entra para anclar Asia oriental."
            ),
            "en": (
                "Wuhan is one of China’s furnace cities: humidity and stagnation in the Yangtze basin. "
                "ADM3 districts run from Wuchang and Hankou to peri-urban Huangpi and Jiangxia. "
                "The spring window is not the July peak; it enters to anchor East Asia."
            ),
            "fr": (
                "Wuhan est une des villes-fournaises de Chine : humidité et stagnation dans le bassin "
                "du Yangtsé. Les districts ADM3 vont de Wuchang et Hankou au périurbain de Huangpi "
                "et Jiangxia. La fenêtre de printemps n’est pas le pic de juillet ; elle entre pour "
                "ancrer l’Asie orientale."
            ),
        },
    },
    "barcelona": {
        "name": {"es": "Barcelona", "en": "Barcelona", "fr": "Barcelone"},
        "country": {"es": "España", "en": "Spain", "fr": "Espagne"},
        "unit": {"es": ("distrito", "distritos"), "en": ("district", "districts"), "fr": ("district", "districts")},
        "why": {
            "es": (
                "Barcelona es el complemento costero de Madrid: noches cálidas, turismo y tejido "
                "denso. Los 10 distritos municipales (de Ciutat Vella a Sant Martí) son comparables "
                "a los 21 de Madrid. Abril–mayo es primavera; entra para no romper la escala."
            ),
            "en": (
                "Barcelona is Madrid’s coastal counterpart: warm nights, tourism and a dense fabric. "
                "The 10 municipal districts (from Ciutat Vella to Sant Martí) are comparable to "
                "Madrid’s 21. April–May is spring; it enters so as not to break the scale."
            ),
            "fr": (
                "Barcelone est le pendant côtier de Madrid : nuits chaudes, tourisme et tissu dense. "
                "Les 10 districts municipaux (de Ciutat Vella à Sant Martí) sont comparables aux "
                "21 de Madrid. Avril–mai est le printemps ; elle entre pour ne pas casser l’échelle."
            ),
        },
    },
    "rome": {
        "name": {"es": "Roma", "en": "Rome", "fr": "Rome"},
        "country": {"es": "Italia", "en": "Italy", "fr": "Italie"},
        "unit": {"es": ("municipio", "municipios"), "en": ("municipio", "municipi"), "fr": ("municipio", "municipi")},
        "pdf": {"es": "Roma", "en": "Rome", "fr": "Rome"},
        "why": {
            "es": (
                "Roma aporta población envejecida, turismo y olas de calor documentadas por EuroHEAT. "
                "Los 15 municipi de Roma Capitale van del centro histórico a la periferia del GRA. "
                "Como Madrid y Barcelona, abril–mayo no es su máximo anual."
            ),
            "en": (
                "Rome adds an ageing population, tourism and heatwaves documented by EuroHEAT. "
                "The 15 municipi of Roma Capitale run from the historic centre to the GRA periphery. "
                "Like Madrid and Barcelona, April–May is not its annual peak."
            ),
            "fr": (
                "Rome apporte une population vieillissante, le tourisme et des vagues de chaleur "
                "documentées par EuroHEAT. Les 15 municipi de Roma Capitale vont du centre historique "
                "à la périphérie du GRA. Comme Madrid et Barcelone, avril–mai n’est pas son maximum annuel."
            ),
        },
    },
    "casablanca": {
        "name": {"es": "Casablanca", "en": "Casablanca", "fr": "Casablanca"},
        "country": {"es": "Marruecos", "en": "Morocco", "fr": "Maroc"},
        "unit": {"es": ("arrondissement", "arrondissements"), "en": ("arrondissement", "arrondissements"), "fr": ("arrondissement", "arrondissements")},
        "why": {
            "es": (
                "Casablanca pone el Magreb en la misma latitud que Phoenix, con menos capacidad de "
                "adaptación que Europa. El recorte son los arrondissements de la prefectura urbana. "
                "El Atlántico suaviza el pico; el IVC sirve para ver si el centro denso se despega del litoral."
            ),
            "en": (
                "Casablanca puts the Maghreb on the same latitude as Phoenix, with less adaptive "
                "capacity than Europe. The cut is the arrondissements of the urban prefecture. "
                "The Atlantic softens the peak; the IVC shows whether the dense centre pulls away from the shore."
            ),
            "fr": (
                "Casablanca place le Maghreb à la même latitude que Phoenix, avec moins de capacité "
                "d’adaptation que l’Europe. Le découpage est celui des arrondissements de la préfecture "
                "urbaine. L’Atlantique adoucit le pic ; l’IVC sert à voir si le centre dense se détache du littoral."
            ),
        },
    },
    "lagos": {
        "name": {"es": "Lagos", "en": "Lagos", "fr": "Lagos"},
        "country": {"es": "Nigeria", "en": "Nigeria", "fr": "Nigeria"},
        "unit": {"es": ("LGA", "LGAs"), "en": ("LGA", "LGAs"), "fr": ("LGA", "LGA")},
        "why": {
            "es": (
                "Lagos es la megaciudad tropical húmeda de África Occidental: calor + humedad y baja "
                "capacidad de adaptación. El recorte es el estado (LGAs). Abril–mayo no es su pico "
                "(estación seca); entra en la ventana fija del IVC."
            ),
            "en": (
                "Lagos is West Africa’s humid tropical megacity: heat plus humidity and low coping "
                "capacity. The cut is the state (LGAs). April–May is not its peak (dry season); it "
                "enters on the IVC’s fixed window."
            ),
            "fr": (
                "Lagos est la mégapole tropicale humide d’Afrique de l’Ouest : chaleur et humidité, "
                "faible capacité d’adaptation. Le découpage est l’État (LGA). Avril–mai n’est pas son "
                "pic (saison sèche) ; elle entre dans la fenêtre fixe de l’IVC."
            ),
        },
    },
    "sao_paulo": {
        "name": {"es": "São Paulo", "en": "São Paulo", "fr": "São Paulo"},
        "country": {"es": "Brasil", "en": "Brazil", "fr": "Brésil"},
        "unit": {"es": ("distrito", "distritos"), "en": ("district", "districts"), "fr": ("district", "districts")},
        "pdf": {"es": "Sao_Paulo", "en": "Sao_Paulo", "fr": "Sao_Paulo"},
        "why": {
            "es": (
                "São Paulo es la mayor aglomeración de Sudamérica: verano austral y meseta. Las "
                "subprefecturas separan el centro de la periferia. Abril–mayo es otoño austral."
            ),
            "en": (
                "São Paulo is South America’s largest agglomeration: southern-hemisphere summer and a "
                "plateau. Subprefectures separate the core from the fringe. April–May is southern autumn."
            ),
            "fr": (
                "São Paulo est la plus grande agglomération d’Amérique du Sud : été austral et plateau. "
                "Les sous-préfectures séparent le centre de la périphérie. Avril–mai est l’automne austral."
            ),
        },
    },
    "singapore": {
        "name": {"es": "Singapur", "en": "Singapore", "fr": "Singapour"},
        "country": {"es": "Singapur", "en": "Singapore", "fr": "Singapour"},
        "unit": {"es": ("planning area", "planning areas"), "en": ("planning area", "planning areas"), "fr": ("planning area", "planning areas")},
        "pdf": {"es": "Singapur", "en": "Singapore", "fr": "Singapour"},
        "why": {
            "es": (
                "Singapur es la isla ecuatorial de referencia: calor casi permanente y UHI tropical "
                "costera. Las regiones de planificación separan el centro denso del oeste industrial."
            ),
            "en": (
                "Singapore is the equatorial-island benchmark: near-permanent heat and a coastal tropical "
                "UHI. Planning regions separate the dense centre from the industrial west."
            ),
            "fr": (
                "Singapour est l’île équatoriale de référence : chaleur quasi permanente et UHI tropical "
                "côtier. Les régions de planification séparent le centre dense de l’ouest industriel."
            ),
        },
    },
    "dubai": {
        "name": {"es": "Dubái", "en": "Dubai", "fr": "Dubaï"},
        "country": {"es": "Emiratos Árabes Unidos", "en": "United Arab Emirates", "fr": "Émirats arabes unis"},
        "unit": {"es": ("sector", "sectores"), "en": ("sector", "sectors"), "fr": ("secteur", "secteurs")},
        "pdf": {"es": "Dubai", "en": "Dubai", "fr": "Dubai"},
        "why": {
            "es": (
                "Dubái es el contraste de adaptación del Golfo: picos de LST brutales y mucha "
                "refrigeración. El polígono es el emirato; las subdivisiones separan el tejido urbano del desierto."
            ),
            "en": (
                "Dubai is the Gulf adaptation contrast: brutal LST peaks and abundant cooling. The polygon "
                "is the emirate; subdivisions separate urban fabric from desert."
            ),
            "fr": (
                "Dubaï est le contraste d’adaptation du Golfe : pics de LST brutaux et beaucoup de "
                "climatisation. Le polygone est l’émirat ; les subdivisions séparent le tissu urbain du désert."
            ),
        },
    },
    "santiago": {
        "name": {"es": "Santiago de Chile", "en": "Santiago de Chile", "fr": "Santiago du Chili"},
        "country": {"es": "Chile", "en": "Chile", "fr": "Chili"},
        "unit": {"es": ("comuna", "comunas"), "en": ("comuna", "comunas"), "fr": ("comuna", "comunas")},
        "why": {
            "es": (
                "Santiago aporta el mediterráneo andino de cuenca cerrada. Las comunas van del centro "
                "al piedemonte. Abril–mayo es otoño austral, no el pico de enero."
            ),
            "en": (
                "Santiago adds an Andean Mediterranean closed basin. Comunas run from the centre to the "
                "foothills. April–May is southern autumn, not the January peak."
            ),
            "fr": (
                "Santiago apporte le méditerranéen andin en bassin fermé. Les comunas vont du centre "
                "au piémont. Avril–mai est l’automne austral, pas le pic de janvier."
            ),
        },
    },
    "johannesburg": {
        "name": {"es": "Johannesburgo", "en": "Johannesburg", "fr": "Johannesburg"},
        "country": {"es": "Sudáfrica", "en": "South Africa", "fr": "Afrique du Sud"},
        "unit": {"es": ("ward", "wards"), "en": ("ward", "wards"), "fr": ("ward", "wards")},
        "pdf": {"es": "Johannesburgo", "en": "Johannesburg", "fr": "Johannesburg"},
        "why": {
            "es": (
                "Johannesburgo es la meseta africana (~1 750 m). Las regiones de la City of Johannesburg "
                "separan el CBD, Soweto y el norte suburbano."
            ),
            "en": (
                "Johannesburg is the African highveld (~1,750 m). City of Johannesburg regions separate "
                "the CBD, Soweto and the northern suburbs."
            ),
            "fr": (
                "Johannesburg est le haut plateau africain (~1 750 m). Les régions de la City of "
                "Johannesburg séparent le CBD, Soweto et le nord suburbain."
            ),
        },
    },
    "mumbai": {
        "name": {"es": "Mumbai", "en": "Mumbai", "fr": "Mumbai"},
        "country": {"es": "India", "en": "India", "fr": "Inde"},
        "unit": {"es": ("taluka", "talukas"), "en": ("taluka", "talukas"), "fr": ("taluka", "talukas")},
        "why": {
            "es": (
                "Mumbai es el par costero de Delhi: pre-monzón húmedo. El recorte es la MMR; las "
                "talukas separan la island city, los suburbios y Thane. Abril–mayo sí es su pico."
            ),
            "en": (
                "Mumbai is Delhi’s coastal counterpart: humid pre-monsoon. The cut is the MMR; talukas "
                "separate the island city, the suburbs and Thane. April–May is its peak."
            ),
            "fr": (
                "Mumbai est le pendant côtier de Delhi : pré-mousson humide. Le découpage est la MMR ; "
                "les talukas séparent l’island city, les banlieues et Thane. Avril–mai est bien son pic."
            ),
        },
    },
    "los_angeles": {
        "name": {"es": "Los Ángeles", "en": "Los Angeles", "fr": "Los Angeles"},
        "country": {"es": "Estados Unidos", "en": "United States", "fr": "États-Unis"},
        "unit": {"es": ("distrito", "distritos"), "en": ("district", "districts"), "fr": ("district", "districts")},
        "pdf": {"es": "Los_Angeles", "en": "Los_Angeles", "fr": "Los_Angeles"},
        "why": {
            "es": (
                "Los Ángeles es el referente ECOSTRESS/JPL de LST urbana. Los 15 distritos del "
                "ayuntamiento van de San Pedro al Valle. Abril–mayo no es el pico de agosto."
            ),
            "en": (
                "Los Angeles is the ECOSTRESS/JPL urban-LST benchmark. The 15 council districts run "
                "from San Pedro to the Valley. April–May is not the August peak."
            ),
            "fr": (
                "Los Angeles est le référent ECOSTRESS/JPL de la LST urbaine. Les 15 districts du "
                "conseil vont de San Pedro à la Valley. Avril–mai n’est pas le pic d’août."
            ),
        },
    },
    "montpellier": {
        "name": {"es": "Montpellier", "en": "Montpellier", "fr": "Montpellier"},
        "country": {"es": "Francia", "en": "France", "fr": "France"},
        "unit": {"es": ("quartier", "quartiers"), "en": ("district", "districts"), "fr": ("quartier", "quartiers")},
        "why": {
            "es": (
                "Montpellier ya tenía un reporte a escala de comuna. Aquí entra con quartiers y la "
                "misma métrica ivc-l4-v1 que París y Barcelona. Abril–mayo es primavera mediterránea."
            ),
            "en": (
                "Montpellier already had a commune-scale report. Here it enters with quartiers and the "
                "same ivc-l4-v1 metric as Paris and Barcelona. April–May is Mediterranean spring."
            ),
            "fr": (
                "Montpellier avait déjà un rapport à l’échelle de la commune. Elle entre ici avec les "
                "quartiers et la même métrique ivc-l4-v1 que Paris et Barcelone. Avril–mai est le "
                "printemps méditerranéen."
            ),
        },
    },
    "paris": {
        "name": {"es": "París", "en": "Paris", "fr": "Paris"},
        "country": {"es": "Francia", "en": "France", "fr": "France"},
        "unit": {"es": ("arrondissement", "arrondissements"), "en": ("arrondissement", "arrondissements"), "fr": ("arrondissement", "arrondissements")},
        "pdf": {"es": "Paris", "en": "Paris", "fr": "Paris"},
        "why": {
            "es": (
                "París es la capital europea de olas de calor (2003, 2019, 2022). Los 20 arrondissements "
                "van del centro denso al Bois. Abril–mayo no es su máximo anual."
            ),
            "en": (
                "Paris is Europe’s heatwave capital (2003, 2019, 2022). The 20 arrondissements run from "
                "the dense centre to the Bois. April–May is not its annual maximum."
            ),
            "fr": (
                "Paris est la capitale européenne des canicules (2003, 2019, 2022). Les 20 arrondissements "
                "vont du centre dense aux Bois. Avril–mai n’est pas son maximum annuel."
            ),
        },
    },
    "berlin": {
        "name": {"es": "Berlín", "en": "Berlin", "fr": "Berlin"},
        "country": {"es": "Alemania", "en": "Germany", "fr": "Allemagne"},
        "unit": {"es": ("Bezirk", "Bezirke"), "en": ("borough", "boroughs"), "fr": ("arrondissement", "arrondissements")},
        "pdf": {"es": "Berlin", "en": "Berlin", "fr": "Berlin"},
        "why": {
            "es": (
                "Berlín aporta una capital continental de latitud alta (~52 °N). Los 12 Bezirke van de "
                "Mitte a Spandau. Abril–mayo es primavera; el pico es julio."
            ),
            "en": (
                "Berlin adds a high-latitude continental capital (~52 °N). The 12 Bezirke run from Mitte "
                "to Spandau. April–May is spring; the peak is July."
            ),
            "fr": (
                "Berlin apporte une capitale continentale de haute latitude (~52 °N). Les 12 Bezirke "
                "vont de Mitte à Spandau. Avril–mai est le printemps ; le pic est juillet."
            ),
        },
    },
    "tokyo": {
        "name": {"es": "Tokio", "en": "Tokyo", "fr": "Tokyo"},
        "country": {"es": "Japón", "en": "Japan", "fr": "Japon"},
        "unit": {"es": ("barrio", "barrios"), "en": ("ward", "wards"), "fr": ("arrondissement", "arrondissements")},
        "pdf": {"es": "Tokio", "en": "Tokyo", "fr": "Tokyo"},
        "why": {
            "es": (
                "Tokio es la mayor aglomeración del mundo. El recorte son los 23 ku, no la prefectura. "
                "Abril–mayo es anterior al pico de julio–agosto y al monzón."
            ),
            "en": (
                "Tokyo is the world’s largest agglomeration. The cut is the 23 special wards, not the "
                "prefecture. April–May precedes the July–August peak and the monsoon."
            ),
            "fr": (
                "Tokyo est la plus grande agglomération du monde. Le découpage est celui des 23 ku, pas "
                "la préfecture. Avril–mai précède le pic de juillet–août et la mousson."
            ),
        },
    },
}


def ascii_token(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch)).replace(" ", "_")


def city_pack(slug: str, lang: str, cfg: dict | None = None) -> dict:
    info = CITY_I18N.get(slug, {})
    name = (info.get("name") or {}).get(lang) or (cfg or {}).get("name_es") or slug.title()
    country = (info.get("country") or {}).get(lang) or (cfg or {}).get("country_es") or ""
    unit, units = (info.get("unit") or {}).get(lang) or (
        (cfg or {}).get("unit_label", "unit"),
        (cfg or {}).get("unit_label_plural", "units"),
    )
    why = (info.get("why") or {}).get(lang) or (cfg or {}).get("why_city", "")
    pdf = (info.get("pdf") or {}).get(lang) or ascii_token(name)
    return {"name": name, "country": country, "unit": unit, "units": units, "why": why, "pdf": pdf}


def hours_label(meta: dict, lang: str) -> str:
    local = meta.get("overpass_local") or ""
    utc = meta.get("overpass_utc") or ""
    raw = meta.get("overpass_label") or ""
    if not local and raw:
        m = re.search(r"~?\s*(\d{1,2}[:h]\s*\d{2})", raw)
        local = m.group(1).replace("h", ":").replace(" ", "") if m else raw
    if not utc and raw:
        m = re.search(r"\(([^)]*UTC)\)", raw)
        if m:
            utc = m.group(1).replace(" UTC", "").strip()
    local = str(local).lstrip("~").strip()
    utc = str(utc).replace("UTC", "").strip()
    if lang == "fr":
        loc = local.replace(":", " h ")
        ut = utc.replace(":", " h ") if utc else utc
        return f"~{loc} heure locale ({ut} UTC)" if ut else f"~{loc} heure locale"
    if lang == "en":
        return f"~{local} local time ({utc} UTC)" if utc else f"~{local} local time"
    return f"~{local} local ({utc} UTC)" if utc else f"~{local} local"


def rural_text(meta: dict, lang: str) -> str:
    raw = meta.get("rural_definition") or ""
    km = re.search(r"(\d+(?:[.,]\d+)?)\s*km", raw, re.I)
    area = km.group(1) if km else None
    belt = any(k in raw.lower() for k in ("cinturón", "cinturon", "belt", "ceinture"))
    if belt:
        inner = area or "?"
        return {
            "es": f"cinturón rural GHSL 20 km (solo {inner} km² rurales internos, umbral {MIN_RURAL_KM2:.0f} km²)",
            "en": f"20 km GHSL rural belt (only {inner} km² rural inside, threshold {MIN_RURAL_KM2:.0f} km²)",
            "fr": f"ceinture rurale GHSL de 20 km (seulement {inner} km² ruraux internes, seuil {MIN_RURAL_KM2:.0f} km²)",
        }[lang]
    if area:
        return {
            "es": f"GHSL 2020 SMOD 11–13 dentro del polígono ({area} km² rurales)",
            "en": f"GHSL 2020 SMOD 11–13 inside the polygon ({area} km² rural)",
            "fr": f"GHSL 2020 SMOD 11–13 à l’intérieur du polygone ({area} km² ruraux)",
        }[lang]
    return {
        "es": "GHSL 2020 SMOD 11–13 dentro del polígono, sin agua",
        "en": "GHSL 2020 SMOD 11–13 inside the city polygon, excluding water",
        "fr": "GHSL 2020 SMOD 11–13 à l’intérieur du polygone, hors eau",
    }[lang]


def chart_name(lang: str, stem: str) -> str:
    return f"{stem}.png" if lang == "es" else f"{stem}.{lang}.png"


def copy_ranking_charts(assets: Path) -> None:
    base = Path(__file__).resolve().parent
    cities = base / "sitio_ranking_ciudades_ivc" / "assets"
    units = base / "sitio_ranking_subdivisiones_ivc" / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    pairs = [
        (cities, "02_componentes", "ranking_ciudades_componentes"),
        (units, "01_top25", "ranking_unidades_top"),
        (units, "02_componentes", "ranking_unidades_componentes"),
    ]
    for src_dir, src_stem, dest_stem in pairs:
        for lang in LANGS:
            src = src_dir / chart_name(lang, src_stem)
            if src.exists():
                shutil.copy2(src, assets / chart_name(lang, dest_stem))


def _html_paras(*texts: str) -> str:
    bits = []
    for text in texts:
        for para in str(text).split("\n\n"):
            para = para.strip()
            if para:
                bits.append(f"<p>{para}</p>")
    return "\n".join(bits)


def ranking_city_html(lang: str, ui: dict, paths: dict, slug: str) -> str:
    if slug not in RICH_SLUGS:
        return _html_paras(ui["rank_alc"], ui["rank_why"])
    assets = paths["assets"]
    city_c = chart_name(lang, "ranking_ciudades_componentes")
    bits = []
    if (assets / city_c).exists():
        bits.append(
            f'<figure class="rank-fig compact"><img src="assets/{city_c}" alt="{ui["cap_city_comp"]}">'
            f'<figcaption>{ui["cap_city_comp"]}</figcaption></figure>'
        )
    bits.append(_html_paras(ui["rank_alc"], ui["rank_why"], ui.get("rank_soil") or ""))
    return "\n".join(bits)


def ranking_units_html(lang: str, ui: dict, paths: dict, slug: str) -> str:
    if slug not in RICH_SLUGS or not ui.get("subdiv_h"):
        return ""
    assets = paths["assets"]
    unit_top = chart_name(lang, "ranking_unidades_top")
    unit_c = chart_name(lang, "ranking_unidades_componentes")
    bits = [f'<h2 id="subdiv">{ui["subdiv_h"]}</h2>', _html_paras(ui["subdiv_p"])]
    if (assets / unit_top).exists():
        bits.append(
            f'<figure class="rank-fig"><img src="assets/{unit_top}" alt="{ui["cap_unit_top"]}">'
            f'<figcaption>{ui["cap_unit_top"]}</figcaption></figure>'
        )
    if (assets / unit_c).exists():
        bits.append(
            f'<figure class="rank-fig compact"><img src="assets/{unit_c}" alt="{ui["cap_unit_comp"]}">'
            f'<figcaption>{ui["cap_unit_comp"]}</figcaption></figure>'
        )
    return "\n".join(bits)


def ranking_html_block(lang: str, ui: dict, paths: dict, slug: str) -> str:
    return ranking_city_html(lang, ui, paths, slug)


def lang_nav(lang: str) -> str:
    bits = []
    for code, label in (("es", "ES"), ("en", "EN"), ("fr", "FR")):
        cur = ' aria-current="true"' if code == lang else ""
        bits.append(f'<a href="{HTML_NAME[code]}"{cur}>{label}</a>')
    return f'<nav class="langs">{"".join(bits)}</nav>'


def copy_pack(lang: str, cfg: dict, df, meta: dict) -> dict:
    slug = meta.get("slug") or cfg.get("slug") or ""
    prio = int(cfg.get("priority") or meta.get("priority") or 1)
    city = city_pack(slug, lang, cfg)
    why1, why2 = WHY[prio][lang]
    n = meta["n_landsat"]
    n_obs = meta["n_obs_mean"]
    hours = hours_label(meta, lang)
    t_rural = meta["t_rural"]
    urban_km2, area_km2 = meta["city_urban_km2"], meta["city_area_km2"]
    hottest, coolest = df.iloc[0], df.iloc[-1]
    unit_name = hottest.unit
    cool_name = coolest.unit
    rural = rural_text(meta, lang)
    name, country, ulabel, ulabels = city["name"], city["country"], city["unit"], city["units"]
    if lang == "en":
        intro1 = (
            f"This report turns four Landsat layers into a surface climate-vulnerability index for {name} "
            f"({country}), comparable across {comparable_units(lang, slug, ulabels)}. "
            f"The index has three temperature measures: a maximum, a period average, and a heat island, "
            f"a differential between a nearby temperate reference zone and the temperature in the area. "
            f"The index is an aggregate of these three measures and a vegetation index (NDVI) that "
            f"penalizes lower vegetation."
        )
        intro2 = (
            f"The urban mask is GHSL 2020 (SMOD ≥ {SMOD_URBAN}) and covers {urban_km2:.0f} km² of "
            f"{area_km2:.0f} km² of the polygon ({100 * urban_km2 / max(area_km2, 1e-6):.0f}%). The 43 °C "
            f"threshold is ISO 13732-1 prolonged contact. The mean map colours from {LST_MEAN_MAP_CUT:.0f} °C."
        )
        intro3 = (
            f"Metric {METRIC_VERSION} is not renormalised across the {len(df)} {ulabels}: each component uses a "
            f"fixed cap, so an IVC of 60 here is comparable to an IVC of 60 in Iztapalapa or a Madrid district. "
            f"z_LST max and z_LST mean are the urban fraction above 43 °C. z_NDVI inverts greenness between "
            f"{NDVI_LO:.2f} and {NDVI_HI:.2f}. z_SUHI clips the differential at {SUHI_INDEX_CAP:.0f} °C. "
            f"IVC = 100 × the mean of the four z scores."
        )
        lead = (
            f"{unit_name} leads the index ({hottest.ivc:.0f}/100): "
            f"{100 * hottest.frac_lst_max_43:.0f}% of its urban area exceeds 43 °C at the per-pixel maximum, "
            f"urban SUHI {hottest.suhi_urban:.1f} °C and NDVI {hottest.ndvi_urban:.2f}. "
            f"{cool_name} ranks last ({coolest.ivc:.0f}/100)."
        )
        method1 = (
            f"Maximum surface temperature. Landsat 8 and 9 Collection 2 Level 2, band 10 (ST_B10), "
            f"1 April–31 May {YEAR}. {n} scenes; overpass {hours}. Per-pixel mask of fill, cloud, shadow and "
            f"LST outside 0–80 °C. LST = 0.00341802×DN + 149 − 273.15. Maximum of valid observations "
            f"({n_obs:.1f} obs./pixel). Overlay and index: urban fraction > {LST_MAX_CUT:.0f} °C."
        )
        method2 = (
            f"Mean surface temperature of observations. Same collection and mask. Mean of valid scenes. "
            f"The map colours from {LST_MEAN_MAP_CUT:.0f} °C; the index uses the urban fraction > {LST_MEAN_INDEX_CUT:.0f} °C."
        )
        method3 = (
            f"Vegetation. NDVI = (NIR − red)/(NIR + red), SR_B5 and SR_B4. Period mean ({n} scenes, {hours}). "
            f"Urban greenness: NDVI ≥ {NDVI_VEG:.2f} inside GHSL SMOD ≥ {SMOD_URBAN}. It enters the index inverted "
            f"on a fixed {NDVI_LO:.2f}–{NDVI_HI:.2f} scale."
        )
        method4 = (
            f"Surface urban heat island. SUHI = pixel mean LST − rural T. T rural = {t_rural:.1f} °C, {rural}. "
            f"Overlay: SUHI > {SUHI_MAP_CUT:.0f} °C. z_SUHI = min(max(urban SUHI, 0) / {SUHI_INDEX_CAP:.0f}, 1)."
        )
        ui = dict(
            remote="urban remote sensing",
            priority=f"Priority {prio}",
            h1=f"Climate Vulnerability Index for {name}",
            subtitle=(
                f"April and May 2026 · peak LST, mean LST, vegetation and heat island · "
                f"{len(df)} {ulabels} · {METRIC_VERSION}"
            ),
            why_index="1. Introduction",
            why_prio=f"11. Why {name} is in Priority {prio}",
            metric_b=f"Comparable metric {METRIC_VERSION}.",
            metric_p=(
                f"IVC = 100 × mean of z<sub>max</sub>, z<sub>mean</sub>, z<sub>NDVI inv</sub> and z<sub>SUHI</sub>. "
                f"City: IVC {meta['city_ivc']:.1f} · SUHI {meta['city_suhi']:.1f} °C · T rural {t_rural:.1f} °C "
                f"· {n} scenes · {n_obs:.1f} obs./pixel · {hours}."
            ),
            four="3. Four methods",
            mh1="1. Per-pixel maximum LST", mh2="2. Mean LST of observations",
            mh3="3. Vegetation (NDVI)", mh4="4. Heat island (SUHI)",
            map1="4. Per-pixel maximum surface temperature (&gt; 43 °C)",
            map2="5. Mean surface temperature of observations (&gt; 35 °C)",
            map3="6. Vegetation (NDVI)",
            map4="7. Heat island (pixel − rural)",
            cap1=f"Maximum of valid observations. ISO 13732-1 overlay: {LST_MAX_CUT:.0f} °C. {n} scenes · {hours} · {n_obs:.1f} obs./pixel.",
            cap2=f"Per-pixel mean. The map colours from {LST_MEAN_MAP_CUT:.0f} °C; the index uses &gt; {LST_MEAN_INDEX_CUT:.0f} °C.",
            cap3=f"Mean NDVI of the same composite. Urban greenness: NDVI ≥ {NDVI_VEG:.2f}.",
            cap4=f"SUHI = mean LST − {t_rural:.1f} °C. {rural}. Overlay &gt; {SUHI_MAP_CUT:.0f} °C. Urban SUHI: {meta['city_suhi']:.1f} °C.",
            order=f"9. Ranking of the {ulabels}",
            units_h=f"10. {ulabels[:1].upper() + ulabels[1:]}",
            summary=(
                f"Area {area_km2:.0f} km² · GHSL urban {urban_km2:.0f} km² "
                f"({100 * urban_km2 / max(area_km2, 1e-6):.0f}%) · peak LST &gt; 43 °C: "
                f"{100 * meta['city_frac_lst_max_43']:.0f}% · mean LST &gt; 43 °C: "
                f"{100 * meta['city_frac_lst_mean_43']:.0f}% · urban SUHI {meta['city_suhi']:.1f} °C "
                f"· greenness {100 * meta['city_frac_veg']:.0f}% · city IVC {meta['city_ivc']:.1f}."
            ),
            th_unit=ulabel[:1].upper() + ulabel[1:],
            th_max="Peak LST &gt; 43 °C", th_mean="Mean LST &gt; 43 °C",
            th_suhi="SUHI °C", th_ndvi="Urban NDVI", th_veg="Greenness", th_obs="Obs./pixel",
            stat_max=f"Peak LST &gt; 43 °C", stat_mean=f"Mean LST &gt; 43 °C",
            stat_suhi="Urban SUHI", stat_ndvi="Urban NDVI",
            fig_max="Peak LST &gt; 43 °C", fig_mean="Mean LST &gt; 35 °C",
            fig_ndvi="NDVI", fig_suhi="Heat island",
            urban="urban", vs="vs T rural",
            footer=(
                f"metric {METRIC_VERSION} · Priority {prio} · {n} scenes · {hours} · April–May {YEAR}"
            ),
            title=f"Climate Vulnerability Index for {name} — April and May 2026",
            chart_ivc=f"Climate-vulnerability index by {ulabel}",
            chart_ivc_x="IVC (0–100) · four layers, inverted NDVI, equal weights",
            chart_frac="Urban area with peak LST > 43 °C",
            chart_frac_x=f"% of GHSL urban area · per-pixel maximum, April–May {YEAR}",
            chart_ndvi="Mean NDVI in urban area",
            chart_ndvi_x=f"Landsat 8/9 NDVI · April–May {YEAR}",
            chart_suhi="Urban heat island (SUHI)",
            chart_suhi_x=f"Urban mean LST − rural T ({t_rural:.1f} °C)",
            stack_title="Vulnerability-index components",
            stack_x="Contribution to the index (0–100, equal weights)",
            stack_labs=["Peak LST pixel > 43 °C", "Mean LST > 43 °C", "Greenness deficit", "Heat island (SUHI)"],
            pdf_why="Why this index",
            pdf_cover=f"Anaplian.com  ·  Priority {prio}  ·  April–May {YEAR}  ·  {METRIC_VERSION}  ·  {n} scenes",
            pdf_city=f"City IVC {meta['city_ivc']:.1f}/100. Urban SUHI {meta['city_suhi']:.1f} °C. {n_obs:.1f} valid observations per pixel.",
            pdf_m1="3. Per-pixel maximum LST > 43 °C",
            pdf_m2="4. Mean LST of observations > 35 °C",
            pdf_m3="5. Vegetation (NDVI)",
            pdf_m4="6. Heat island (pixel − rural)",
            pdf_c1=f"{n} scenes · {hours} · ISO overlay {LST_MAX_CUT:.0f} °C.",
            pdf_c2=f"Mean of valid observations. Index: urban fraction > {LST_MEAN_INDEX_CUT:.0f} °C.",
            pdf_c3=f"Mean NDVI. Urban greenness ≥ {NDVI_VEG:.2f}.",
            pdf_c4=f"SUHI = mean LST − {t_rural:.1f} °C. Overlay > {SUHI_MAP_CUT:.0f} °C.",
            pdf_index=f"7. Index by {ulabel}",
            pdf_index_cap=f"Metric {METRIC_VERSION}, fixed 0–100 scale.",
            pdf_comp="8. Index components",
            pdf_frac="9. Urban fraction > 43 °C (per-pixel maximum)",
            pdf_suhi_p="10. Urban heat island (SUHI)",
            pdf_suhi_cap=f"Urban LST − {t_rural:.1f} °C rural.",
            pdf_ndvi_p="11. Urban NDVI",
            pdf_table=f"12. Table of {ulabels}",
            pdf_quad=["Peak LST > 43 C", "Mean LST > 35 C", "NDVI", "SUHI vs rural"],
        )
    elif lang == "fr":
        intro1 = (
            f"Ce rapport convertit quatre couches Landsat en un indice de vulnérabilité climatique de "
            f"surface pour {name} ({country}), comparable entre {comparable_units(lang, slug, ulabels)}. "
            f"L’indice a trois mesures de température : un maximum, une moyenne de la période et un îlot "
            f"de chaleur, un différentiel entre une zone tempérée de référence proche et la température "
            f"de la zone. L’indice agrège ces trois mesures et un indice de végétation (NDVI) qui "
            f"pénalise une végétation plus faible."
        )
        intro2 = (
            f"La zone urbaine vient du GHSL 2020 (SMOD ≥ {SMOD_URBAN}) et couvre {urban_km2:.0f} km² sur "
            f"{area_km2:.0f} km² du polygone ({100 * urban_km2 / max(area_km2, 1e-6):.0f} %). Le seuil de "
            f"43 °C est celui du contact prolongé ISO 13732-1. La carte de la moyenne colore à partir de "
            f"{LST_MEAN_MAP_CUT:.0f} °C."
        )
        intro3 = (
            f"La métrique {METRIC_VERSION} n’est pas renormalisée entre les {len(df)} {ulabels} : chaque "
            f"composante a un plafond fixe, de sorte qu’un IVC 60 ici soit comparable à un IVC 60 à "
            f"Iztapalapa ou dans un district de Madrid. z_LST max. et z_LST moyenne sont la fraction urbaine "
            f"au-dessus de 43 °C. z_NDVI inverse le verdissement entre {NDVI_LO:.2f} et {NDVI_HI:.2f}. "
            f"z_SUHI recadre l’écart à {SUHI_INDEX_CAP:.0f} °C. IVC = 100 × moyenne des quatre z."
        )
        lead = (
            f"{unit_name} arrive en tête de l’indice ({hottest.ivc:.0f}/100) : "
            f"{100 * hottest.frac_lst_max_43:.0f} % de sa zone urbaine dépasse 43 °C au maximum par pixel, "
            f"SUHI urbain {hottest.suhi_urban:.1f} °C et NDVI {hottest.ndvi_urban:.2f}. "
            f"{cool_name} arrive en dernier ({coolest.ivc:.0f}/100)."
        )
        method1 = (
            f"Température de surface maximale. Landsat 8 et 9 Collection 2 niveau 2, bande 10 (ST_B10), "
            f"1er avril–31 mai {YEAR}. {n} scènes ; survol {hours}. Masque par pixel du remplissage, des "
            f"nuages, des ombres et des LST hors 0–80 °C. LST = 0,00341802×DN + 149 − 273,15. Maximum des "
            f"observations valides ({n_obs:.1f} obs./pixel). Superposition et indice : fraction urbaine > {LST_MAX_CUT:.0f} °C."
        )
        method2 = (
            f"Température de surface moyenne des observations. Même collection et même masque. Moyenne des "
            f"scènes valides. La carte colore à partir de {LST_MEAN_MAP_CUT:.0f} °C ; l’indice utilise la "
            f"fraction urbaine > {LST_MEAN_INDEX_CUT:.0f} °C."
        )
        method3 = (
            f"Végétation. NDVI = (PIR − rouge)/(PIR + rouge), SR_B5 et SR_B4. Moyenne de la période "
            f"({n} scènes, {hours}). Verdure urbaine : NDVI ≥ {NDVI_VEG:.2f} dans GHSL SMOD ≥ {SMOD_URBAN}. "
            f"Dans l’indice, il entre inversé sur une échelle fixe {NDVI_LO:.2f}–{NDVI_HI:.2f}."
        )
        method4 = (
            f"Îlot de chaleur de surface. SUHI = LST moyenne du pixel − T rurale. T rurale = {t_rural:.1f} °C, {rural}. "
            f"Superposition : SUHI > {SUHI_MAP_CUT:.0f} °C. z_SUHI = min(max(SUHI urbain, 0) / {SUHI_INDEX_CAP:.0f}, 1)."
        )
        ui = dict(
            remote="télédétection urbaine",
            priority=f"Priorité {prio}",
            h1=f"Indice de vulnérabilité climatique : {name}",
            subtitle=(
                f"Avril et mai 2026 · LST maximale, LST moyenne, végétation et îlot de chaleur · "
                f"{len(df)} {ulabels} · {METRIC_VERSION}"
            ),
            why_index="1. Introduction",
            why_prio=f"11. Pourquoi {name} est en Priorité {prio}",
            metric_b=f"Métrique comparable {METRIC_VERSION}.",
            metric_p=(
                f"IVC = 100 × moyenne de z<sub>max</sub>, z<sub>moy</sub>, z<sub>NDVI inv</sub> et z<sub>SUHI</sub>. "
                f"Ville : IVC {meta['city_ivc']:.1f} · SUHI {meta['city_suhi']:.1f} °C · T rurale {t_rural:.1f} °C "
                f"· {n} scènes · {n_obs:.1f} obs./pixel · {hours}."
            ),
            four="3. Quatre méthodologies",
            mh1="1. LST maximale par pixel", mh2="2. LST moyenne des observations",
            mh3="3. Végétation (NDVI)", mh4="4. Îlot de chaleur (SUHI)",
            map1="4. Température de surface maximale par pixel (&gt; 43 °C)",
            map2="5. Température de surface, moyenne des observations (&gt; 35 °C)",
            map3="6. Végétation (NDVI)",
            map4="7. Îlot de chaleur (pixel − rural)",
            cap1=f"Maximum des observations valides. Superposition ISO 13732-1 : {LST_MAX_CUT:.0f} °C. {n} scènes · {hours} · {n_obs:.1f} obs./pixel.",
            cap2=f"Moyenne par pixel. La carte colore à partir de {LST_MEAN_MAP_CUT:.0f} °C ; l’indice utilise &gt; {LST_MEAN_INDEX_CUT:.0f} °C.",
            cap3=f"NDVI moyen du même composite. Verdure urbaine : NDVI ≥ {NDVI_VEG:.2f}.",
            cap4=f"SUHI = LST moyenne − {t_rural:.1f} °C. {rural}. Superposition &gt; {SUHI_MAP_CUT:.0f} °C. SUHI urbain : {meta['city_suhi']:.1f} °C.",
            order=f"9. Classement des {ulabels}",
            units_h=f"10. {ulabels[:1].upper() + ulabels[1:]}",
            summary=(
                f"Superficie {area_km2:.0f} km² · urbaine GHSL {urban_km2:.0f} km² "
                f"({100 * urban_km2 / max(area_km2, 1e-6):.0f} %) · LST max. &gt; 43 °C : "
                f"{100 * meta['city_frac_lst_max_43']:.0f} % · LST moyenne &gt; 43 °C : "
                f"{100 * meta['city_frac_lst_mean_43']:.0f} % · SUHI urbain {meta['city_suhi']:.1f} °C "
                f"· verdure {100 * meta['city_frac_veg']:.0f} % · IVC ville {meta['city_ivc']:.1f}."
            ),
            th_unit=ulabel[:1].upper() + ulabel[1:],
            th_max="LST max. &gt; 43 °C", th_mean="LST moyenne &gt; 43 °C",
            th_suhi="SUHI °C", th_ndvi="NDVI urbain", th_veg="Verdure", th_obs="Obs./pixel",
            stat_max="LST max. &gt; 43 °C", stat_mean="LST moyenne &gt; 43 °C",
            stat_suhi="SUHI urbain", stat_ndvi="NDVI urbain",
            fig_max="LST max. &gt; 43 °C", fig_mean="LST moyenne &gt; 35 °C",
            fig_ndvi="NDVI", fig_suhi="Îlot de chaleur",
            urban="urbain", vs="vs T rurale",
            footer=(
                f"métrique {METRIC_VERSION} · Priorité {prio} · {n} scènes · {hours} · avril–mai {YEAR}"
            ),
            title=f"Indice de vulnérabilité climatique : {name} — avril et mai 2026",
            chart_ivc=f"Indice de vulnérabilité climatique par {ulabel}",
            chart_ivc_x="IVC (0–100) · quatre couches, NDVI inversé, poids égaux",
            chart_frac="Surface urbaine avec LST maximale > 43 °C",
            chart_frac_x=f"% de la zone urbaine GHSL · maximum par pixel, avril–mai {YEAR}",
            chart_ndvi="NDVI moyen en zone urbaine",
            chart_ndvi_x=f"NDVI Landsat 8/9 · avril–mai {YEAR}",
            chart_suhi="Îlot de chaleur urbain (SUHI)",
            chart_suhi_x=f"LST moyenne urbaine − T rurale ({t_rural:.1f} °C)",
            stack_title="Composantes de l’indice de vulnérabilité",
            stack_x="Apport à l’indice (0–100, poids égaux)",
            stack_labs=["LST max. pixel > 43 °C", "LST moyenne > 43 °C", "Déficit de verdure", "Îlot de chaleur (SUHI)"],
            pdf_why="Pourquoi cet indice",
            pdf_cover=f"Anaplian.com  ·  Priorité {prio}  ·  Avril–mai {YEAR}  ·  {METRIC_VERSION}  ·  {n} scènes",
            pdf_city=f"IVC ville {meta['city_ivc']:.1f}/100. SUHI urbain {meta['city_suhi']:.1f} °C. {n_obs:.1f} observations valides par pixel.",
            pdf_m1="3. LST maximale par pixel > 43 °C",
            pdf_m2="4. LST moyenne des observations > 35 °C",
            pdf_m3="5. Végétation (NDVI)",
            pdf_m4="6. Îlot de chaleur (pixel − rural)",
            pdf_c1=f"{n} scènes · {hours} · superposition ISO {LST_MAX_CUT:.0f} °C.",
            pdf_c2=f"Moyenne des observations valides. Indice : fraction urbaine > {LST_MEAN_INDEX_CUT:.0f} °C.",
            pdf_c3=f"NDVI moyen. Verdure urbaine ≥ {NDVI_VEG:.2f}.",
            pdf_c4=f"SUHI = LST moyenne − {t_rural:.1f} °C. Superposition > {SUHI_MAP_CUT:.0f} °C.",
            pdf_index=f"7. Indice par {ulabel}",
            pdf_index_cap=f"Métrique {METRIC_VERSION}, échelle fixe 0–100.",
            pdf_comp="8. Composantes de l’indice",
            pdf_frac="9. Fraction urbaine > 43 °C (maximum par pixel)",
            pdf_suhi_p="10. Îlot de chaleur urbain (SUHI)",
            pdf_suhi_cap=f"LST urbaine − {t_rural:.1f} °C rurale.",
            pdf_ndvi_p="11. NDVI urbain",
            pdf_table=f"12. Tableau des {ulabels}",
            pdf_quad=["LST max > 43 C", "LST moyenne > 35 C", "NDVI", "SUHI vs rural"],
        )
    else:
        intro1 = (
            f"Este reporte convierte cuatro capas Landsat en un índice de vulnerabilidad climática de "
            f"superficie para {name} ({country}), comparable entre {comparable_units(lang, slug, ulabels)}. "
            f"El índice tiene tres medidas de temperatura: una de máxima, otra de promedio en el periodo "
            f"y otra de isla de calor, un diferencial entre una zona templada cercana de referencia y la "
            f"temperatura en la zona. El índice es un agregado de estas tres medidas y un índice de "
            f"vegetación NDVI donde se castiga menor vegetación."
        )
        intro2 = (
            f"La zona urbana se toma del GHSL 2020 (SMOD ≥ {SMOD_URBAN}) y cubre {urban_km2:.0f} km² de "
            f"{area_km2:.0f} km² del polígono ({100 * urban_km2 / max(area_km2, 1e-6):.0f} %). El umbral de "
            f"43 °C es el de contacto prolongado de ISO 13732-1. El mapa de la media colorea desde {LST_MEAN_MAP_CUT:.0f} °C."
        )
        intro3 = (
            f"La métrica {METRIC_VERSION} no se renormaliza entre los {len(df)} {ulabels}: cada componente "
            f"usa un tope fijo, de modo que un IVC 60 aquí sea comparable a un IVC 60 en Iztapalapa o en un "
            f"distrito de Madrid. z_LST máx. y z_LST media son la fracción urbana sobre 43 °C. z_NDVI "
            f"invierte el verdor entre {NDVI_LO:.2f} y {NDVI_HI:.2f}. z_SUHI recorta el diferencial a "
            f"{SUHI_INDEX_CAP:.0f} °C. IVC = 100 × media de las cuatro z."
        )
        lead = (
            f"{unit_name} encabeza el índice ({hottest.ivc:.0f}/100): "
            f"{100 * hottest.frac_lst_max_43:.0f} % de su zona urbana supera 43 °C en el máximo por píxel, "
            f"SUHI urbano {hottest.suhi_urban:.1f} °C y NDVI {hottest.ndvi_urban:.2f}. "
            f"{cool_name} queda al final ({coolest.ivc:.0f}/100)."
        )
        method1 = (
            f"Temperatura de superficie máxima. Landsat 8 y 9 Colección 2 nivel 2, banda 10 (ST_B10), "
            f"1 abril–31 mayo {YEAR}. {n} escenas; sobrepaso {hours}. Máscara por píxel de relleno, nubes, "
            f"sombras y LST fuera de 0–80 °C. LST = 0,00341802×DN + 149 − 273,15. Máximo de las "
            f"observaciones válidas ({n_obs:.1f} obs./píxel). Overlay e índice: fracción urbana > {LST_MAX_CUT:.0f} °C."
        )
        method2 = (
            f"Temperatura de superficie promedio. Misma colección y máscara. Media de las escenas válidas. "
            f"El mapa colorea desde {LST_MEAN_MAP_CUT:.0f} °C; el índice usa la fracción urbana > {LST_MEAN_INDEX_CUT:.0f} °C."
        )
        method3 = (
            f"Vegetación. NDVI = (PIR − rojo)/(PIR + rojo), SR_B5 y SR_B4. Media del periodo ({n} escenas, {hours}). "
            f"Verdor urbano: NDVI ≥ {NDVI_VEG:.2f} dentro de GHSL SMOD ≥ {SMOD_URBAN}. En el índice entra invertido "
            f"con escala fija {NDVI_LO:.2f}–{NDVI_HI:.2f}."
        )
        method4 = (
            f"Isla de calor de superficie. SUHI = LST media del píxel − T rural. T rural = {t_rural:.1f} °C, {rural}. "
            f"Overlay: SUHI > {SUHI_MAP_CUT:.0f} °C. z_SUHI = min(max(SUHI urbano, 0) / {SUHI_INDEX_CAP:.0f}, 1)."
        )
        ui = dict(
            remote="teledetección urbana",
            priority=f"Prioridad {prio}",
            h1=f"Índice de Vulnerabilidad Climática en {name}",
            subtitle=(
                f"Abril y mayo de 2026 · LST máxima, LST media, vegetación e isla de calor · "
                f"{len(df)} {ulabels} · {METRIC_VERSION}"
            ),
            why_index="1. Introducción",
            why_prio=f"11. Por qué {name} está en Prioridad {prio}",
            metric_b=f"Métrica comparable {METRIC_VERSION}.",
            metric_p=(
                f"IVC = 100 × media de z<sub>máx</sub>, z<sub>media</sub>, z<sub>NDVI inv</sub> y z<sub>SUHI</sub>. "
                f"Ciudad: IVC {meta['city_ivc']:.1f} · SUHI {meta['city_suhi']:.1f} °C · T rural {t_rural:.1f} °C "
                f"· {n} escenas · {n_obs:.1f} obs./píxel · {hours}."
            ),
            four="3. Cuatro metodologías",
            mh1="1. LST máxima por píxel", mh2="2. LST media de observaciones",
            mh3="3. Vegetación (NDVI)", mh4="4. Isla de calor (SUHI)",
            map1="4. Temperatura de superficie máxima por píxel (&gt; 43 °C)",
            map2="5. Temperatura de superficie, promedio de observaciones (&gt; 35 °C)",
            map3="6. Vegetación (NDVI)",
            map4="7. Isla de calor (píxel − rural)",
            cap1=f"Máximo de las observaciones válidas. Overlay ISO 13732-1: {LST_MAX_CUT:.0f} °C. {n} escenas · {hours} · {n_obs:.1f} obs./píxel.",
            cap2=f"Media por píxel. El mapa colorea desde {LST_MEAN_MAP_CUT:.0f} °C; el índice usa &gt; {LST_MEAN_INDEX_CUT:.0f} °C.",
            cap3=f"NDVI medio del mismo composite. Verdor urbano: NDVI ≥ {NDVI_VEG:.2f}.",
            cap4=f"SUHI = LST media − {t_rural:.1f} °C. {rural}. Overlay &gt; {SUHI_MAP_CUT:.0f} °C. SUHI urbano: {meta['city_suhi']:.1f} °C.",
            order=f"9. Orden de las {ulabels}",
            units_h=f"10. {ulabels[:1].upper() + ulabels[1:]}",
            summary=(
                f"Área {area_km2:.0f} km² · urbana GHSL {urban_km2:.0f} km² "
                f"({100 * urban_km2 / max(area_km2, 1e-6):.0f} %) · LST máx. &gt; 43 °C: "
                f"{100 * meta['city_frac_lst_max_43']:.0f} % · LST media &gt; 43 °C: "
                f"{100 * meta['city_frac_lst_mean_43']:.0f} % · SUHI urbano {meta['city_suhi']:.1f} °C "
                f"· verdor {100 * meta['city_frac_veg']:.0f} % · IVC ciudad {meta['city_ivc']:.1f}."
            ),
            th_unit=ulabel[:1].upper() + ulabel[1:],
            th_max="LST máx. &gt; 43 °C", th_mean="LST media &gt; 43 °C",
            th_suhi="SUHI °C", th_ndvi="NDVI urbano", th_veg="Verdor", th_obs="Obs./píxel",
            stat_max="LST máx. &gt; 43 °C", stat_mean="LST media &gt; 43 °C",
            stat_suhi="SUHI urbano", stat_ndvi="NDVI urbano",
            fig_max="LST máxima &gt; 43 °C", fig_mean="LST media &gt; 35 °C",
            fig_ndvi="NDVI", fig_suhi="Isla de calor",
            urban="urbano", vs="vs T rural",
            footer=(
                f"métrica {METRIC_VERSION} · Prioridad {prio} · {n} escenas · {hours} · abril–mayo {YEAR}"
            ),
            title=f"Índice de Vulnerabilidad Climática en {name} — abril y mayo de 2026",
            chart_ivc=f"Índice de vulnerabilidad climática por {ulabel}",
            chart_ivc_x="IVC (0–100) · cuatro capas, NDVI invertido, pesos iguales",
            chart_frac="Área urbana con LST máxima > 43 °C",
            chart_frac_x=f"% de la zona urbana GHSL · máximo por píxel, abril–mayo {YEAR}",
            chart_ndvi="NDVI medio en zona urbana",
            chart_ndvi_x=f"NDVI Landsat 8/9 · abril–mayo {YEAR}",
            chart_suhi="Isla de calor urbana (SUHI)",
            chart_suhi_x=f"LST media urbana − T rural ({t_rural:.1f} °C)",
            stack_title="Componentes del índice de vulnerabilidad",
            stack_x="Aporte al índice (0–100, pesos iguales)",
            stack_labs=["LST máx. píxel > 43 °C", "LST media > 43 °C", "Déficit de verdor", "Isla de calor (SUHI)"],
            pdf_why="Por qué este índice",
            pdf_cover=f"Anaplian.com  ·  Prioridad {prio}  ·  Abril–mayo {YEAR}  ·  {METRIC_VERSION}  ·  {n} escenas",
            pdf_city=f"IVC ciudad {meta['city_ivc']:.1f}/100. SUHI urbano {meta['city_suhi']:.1f} °C. {n_obs:.1f} observaciones válidas por píxel.",
            pdf_m1="3. LST máxima por píxel > 43 °C",
            pdf_m2="4. LST media de observaciones > 35 °C",
            pdf_m3="5. Vegetación (NDVI)",
            pdf_m4="6. Isla de calor (píxel − rural)",
            pdf_c1=f"{n} escenas · {hours} · overlay ISO {LST_MAX_CUT:.0f} °C.",
            pdf_c2=f"Media de observaciones válidas. Índice: fracción urbana > {LST_MEAN_INDEX_CUT:.0f} °C.",
            pdf_c3=f"NDVI medio. Verdor urbano ≥ {NDVI_VEG:.2f}.",
            pdf_c4=f"SUHI = LST media − {t_rural:.1f} °C. Overlay > {SUHI_MAP_CUT:.0f} °C.",
            pdf_index=f"7. Índice por {ulabel}",
            pdf_index_cap=f"Métrica {METRIC_VERSION}, escala fija 0–100.",
            pdf_comp="8. Componentes del índice",
            pdf_frac="9. Fracción urbana > 43 °C (máximo por píxel)",
            pdf_suhi_p="10. Isla de calor urbana (SUHI)",
            pdf_suhi_cap=f"LST urbana − {t_rural:.1f} °C rural.",
            pdf_ndvi_p="11. NDVI urbano",
            pdf_table=f"12. Tabla de {ulabels}",
            pdf_quad=["LST max > 43 C", "LST media > 35 C", "NDVI", "SUHI vs rural"],
        )
    extra = intro_and_rank(lang, slug, name, country, ulabel, ulabels, df, meta)
    ui.update(
        intro1=intro1, intro2=intro2, intro3=intro3, lead=lead,
        method1=method1, method2=method2, method3=method3, method4=method4,
        why1=why1, why2=why2, why_city=city["why"],
        name=name, ulabel=ulabel, ulabels=ulabels, hours=hours, prio=prio, pdf=city["pdf"],
        **extra,
    )
    if lang == "en":
        ui.update(
            hotspot_h="8. Heat-exposure sites",
            hotspot_p=(
                "Candidate outdoor-exposure sites: pavement, sheds and terminals with high LST "
                "and people in the sun. The five city sites with the strongest signal are AICM, "
                "Central de Abasto, CETRAM Pantitlán, TAPO and La Merced."
            ),
            hotspot_cap="Sites with high mean LST and outdoor exposure.",
            hotspot_alc="Detail in this borough",
            th_site="Site", th_alc="Borough", th_why="Why it is here",
            four_titles=[
                "Urban area with peak LST > 43 °C",
                "Urban area with mean LST > 43 °C",
                "Urban heat island (SUHI)",
                "Mean urban NDVI",
            ],
            four_xlabels=[
                "% of GHSL urban area · pixel-max",
                "% of GHSL urban area · pixel-mean",
                f"Urban mean LST − rural T ({t_rural:.1f} °C)",
                "Landsat 8/9 NDVI · April–May",
            ],
        )
    elif lang == "fr":
        ui.update(
            hotspot_h="8. Sites d’exposition à la chaleur",
            hotspot_p=(
                "Sites candidats d’exposition en extérieur : revêtement, hangars et terminaux "
                "à LST élevée et personnes au soleil. Les cinq sites urbains au signal le plus "
                "fort sont AICM, Central de Abasto, CETRAM Pantitlán, TAPO et La Merced."
            ),
            hotspot_cap="Sites à LST moyenne élevée et exposition en extérieur.",
            hotspot_alc="Détail dans cette délégation",
            th_site="Site", th_alc="Délégation", th_why="Pourquoi il est là",
            four_titles=[
                "Surface urbaine avec LST max. > 43 °C",
                "Surface urbaine avec LST moyenne > 43 °C",
                "Îlot de chaleur urbain (SUHI)",
                "NDVI urbain moyen",
            ],
            four_xlabels=[
                "% de la zone urbaine GHSL · max-pixel",
                "% de la zone urbaine GHSL · moyenne",
                f"LST urbaine − T rurale ({t_rural:.1f} °C)",
                "NDVI Landsat 8/9 · avril–mai",
            ],
        )
    else:
        ui.update(
            hotspot_h="8. Zonas de exposición al calor",
            hotspot_p=(
                "Sitios candidatos de exposición al aire libre: pavimento, naves y terminales "
                "con LST alta y gente al sol. Los cinco sitios de la ciudad con señal más "
                "fuerte son AICM, Central de Abasto, CETRAM Pantitlán, TAPO y La Merced."
            ),
            hotspot_cap="Sitios con LST media alta y exposición al aire libre.",
            hotspot_alc="Detalle en esta alcaldía",
            th_site="Sitio", th_alc="Alcaldía", th_why="Por qué entra",
            four_titles=[
                "Área urbana con LST máxima > 43 °C",
                "Área urbana con LST media > 43 °C",
                "Isla de calor urbana (SUHI)",
                "NDVI medio en zona urbana",
            ],
            four_xlabels=[
                "% de la zona urbana GHSL · máximo por píxel",
                "% de la zona urbana GHSL · media",
                f"LST urbana − T rural ({t_rural:.1f} °C)",
                "NDVI Landsat 8/9 · abril–mayo",
            ],
        )
    ui["toc_h"] = {"es": "Índice", "en": "Contents", "fr": "Sommaire"}[lang]
    ui["pdf_label"] = {"es": "Informe en PDF", "en": "PDF report", "fr": "Rapport PDF"}[lang]
    ui["pdf_files"] = [
        ("ES", f"{PDF_STEM['es']}_{city_pack(slug, 'es', cfg)['pdf']}_2026.pdf"),
        ("EN", f"{PDF_STEM['en']}_{city_pack(slug, 'en', cfg)['pdf']}_2026.pdf"),
        ("FR", f"{PDF_STEM['fr']}_{city_pack(slug, 'fr', cfg)['pdf']}_2026.pdf"),
    ]
    ui["toc_html"] = [
        ("intro", ui["why_index"]),
        ("rank", ui["rank_h"]),
        ("methods", ui["four"]),
        ("map1", ui["map1"]),
        ("map2", ui["map2"]),
        ("map3", ui["map3"]),
        ("map4", ui["map4"]),
        ("hotspots", ui["hotspot_h"]),
        ("order", ui["order"]),
        ("units", ui["units_h"]),
        ("why", ui["why_prio"]),
    ]
    if slug != "cdmx":
        ui["toc_html"] = [item for item in ui["toc_html"] if item[0] != "hotspots"]
    ui["toc_pdf"] = [
        ui["why_index"],
        ui["rank_h"],
        ui["pdf_m1"], ui["pdf_m2"], ui["pdf_m3"], ui["pdf_m4"],
        ui["pdf_index"], ui["pdf_comp"], ui["pdf_frac"], ui["pdf_suhi_p"],
        ui["pdf_ndvi_p"], ui["pdf_table"],
    ]
    if slug in RICH_SLUGS:
        apply_cdmx_chapter_numbers(ui, lang, slug, name, ulabel, ulabels, prio)
    else:
        ui["toc_pdf"].append("13. " + ui["units_h"].split(". ", 1)[-1])
        ui["toc_pdf"].append("14. " + ui["why_prio"].split(". ", 1)[-1])
        ui["pdf_hotspot"] = ui["hotspot_h"]
        ui["pdf_units"] = "13. " + ui["units_h"].split(". ", 1)[-1]
        ui["pdf_why"] = "14. " + ui["why_prio"].split(". ", 1)[-1]
        ui["pdf_four"] = ui.get("pdf_index") or ""
    return ui


def ensure_favicon(assets: Path) -> None:
    src = BRANDING / "anaplian_logo.jpg"
    if not src.exists():
        return
    assets.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    arr = np.asarray(im)
    mask = arr.mean(axis=2) > 18
    if mask.any():
        ys, xs = np.where(mask)
        pad = 36
        im = im.crop((
            max(0, int(xs.min()) - pad),
            max(0, int(ys.min()) - pad),
            min(im.width, int(xs.max()) + 1 + pad),
            min(im.height, int(ys.max()) + 1 + pad),
        ))
    w, h = im.size
    side = max(w, h)
    canvas = Image.new("RGB", (side, side), (0, 0, 0))
    canvas.paste(im, ((side - w) // 2, (side - h) // 2))
    canvas.resize((32, 32), Image.Resampling.LANCZOS).save(assets / "favicon.png", format="PNG")
    canvas.resize((180, 180), Image.Resampling.LANCZOS).save(
        assets / "apple-touch-icon.png", format="PNG"
    )
    canvas.save(assets / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])


def crop_uniform_border(im: Image.Image, tol: int = 12, pad: int = 6) -> Image.Image:
    arr = np.array(im.convert("RGB"))
    g = arr.mean(axis=2)
    mask = g < 255 - tol
    if not mask.any():
        return im
    ys, xs = np.where(mask)
    return im.crop((
        max(0, int(xs.min()) - pad), max(0, int(ys.min()) - pad),
        min(im.width, int(xs.max()) + 1 + pad), min(im.height, int(ys.max()) + 1 + pad),
    ))


STYLE = """
    :root { --ink:#1a1a1a; --muted:#555; --line:#e6e1d8; --accent:#c2410c; }
    * { box-sizing: border-box; }
    body { margin:0; color:var(--ink); background:#f7f4ef;
      font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif; line-height:1.55; }
    header { background:#111; color:#fff; padding:36px 20px 28px; }
    header .wrap, main, footer .wrap { max-width:960px; margin:0 auto; }
    header .wrap { display:flex; justify-content:space-between; gap:16px; align-items:flex-start; }
    header .titles { min-width:0; }
    h1 { font-size:2.05rem; margin:0 0 8px; letter-spacing:-0.02em; }
    .kicker { color:#f0c27a; font-size:0.82rem; letter-spacing:0.12em; text-transform:uppercase; }
    .langs { display:flex; gap:10px; font-size:0.78rem; letter-spacing:0.08em; flex-shrink:0; padding-top:2px; }
    .langs a { color:#f0c27a; text-decoration:none; }
    .langs a[aria-current="true"] { color:#fff; border-bottom:1px solid #f0c27a; padding-bottom:1px; }
    main { padding:28px 20px 64px; }
    h2 { font-size:1.25rem; margin:2.2rem 0 0.7rem; }
    figure { margin:0 0 1.2rem; }
    figure img { width:100%; height:auto; background:#111; display:block; }
    figure.rank-fig { max-width:680px; margin-left:auto; margin-right:auto; }
    figure.rank-fig img, figure.light img { background:#fff; }
    figure.rank-fig.compact { max-width:460px; }
    figcaption { font-size:0.88rem; color:var(--muted); margin-top:8px; }
    .quad { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
    .quad figure { margin:0; }
    .method { background:#fff; border:1px solid var(--line); padding:1rem 1.1rem; margin:0 0 12px; }
    .methods { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
    .methods .method h3 { margin:0 0 0.45rem; font-size:1.0rem; }
    .methods .method p { margin:0; font-size:0.9rem; color:var(--muted); }
    .metric { background:#fff; border-left:4px solid var(--accent); padding:0.9rem 1.1rem; margin:0 0 1.2rem; }
    @media (max-width: 640px) { .quad, .methods { grid-template-columns:1fr; } header .wrap { flex-direction:column; } }
    table { width:100%; border-collapse:collapse; background:#fff; font-size:0.86rem; }
    th, td { padding:7px 8px; border-bottom:1px solid var(--line); text-align:right; }
    th { background:#111; color:#fff; font-weight:600; }
    th:nth-child(1), td:nth-child(1), th:nth-child(2), td:nth-child(2) { text-align:left; }
    .stats { padding-left:18px; }
    .card { border-top:1px solid var(--line); padding-top:8px; }
    .note { color:var(--muted); font-size:0.95rem; margin:0.4rem 0 0.9rem; }
    .hotspots table { margin:0 0 1.2rem; }
    .pdf-links { margin:12px 0 0; font-size:0.9rem; }
    .pdf-links a { color:#f0c27a; }
    nav.toc { background:#fff; border:1px solid var(--line); padding:1rem 1.2rem 1.1rem; margin:0 0 1.6rem; }
    nav.toc h2 { margin:0 0 0.6rem; font-size:1.05rem; }
    nav.toc ol { margin:0; padding-left:1.25rem; }
    nav.toc li { margin:0.22rem 0; }
    nav.toc a { color:var(--ink); text-decoration:none; }
    nav.toc a:hover { color:var(--accent); }
    footer { background:#111; color:#bbb; padding:18px 20px; }
    footer strong { color:#ddd; }
"""


def hotspot_html_block(lang, ui, paths, slug):
    if slug != "cdmx":
        return ""
    catalog_path = Path(__file__).resolve().parents[1] / "data" / "hotspots" / "cdmx_hotspots.json"
    if not catalog_path.exists():
        return ""
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    top = set(data.get("top5") or [])
    rows = []
    for s in data["sites"]:
        mark = "★ " if s["id"] in top else ""
        lst = s.get("lst_mean_C")
        lst_txt = f"{lst:.1f} °C" if lst is not None else "—"
        why = (s.get("why") or {}).get(lang) or (s.get("why") or {}).get("es") or ""
        rows.append(
            f"<tr><td>{mark}{s['name']}</td><td>{s['alcaldia']}</td>"
            f"<td>{lst_txt}</td><td>{why}</td></tr>"
        )
    return f"""
    <h2 id="hotspots">{ui['hotspot_h']}</h2>
    <p>{ui['hotspot_p']}</p>
    <div class="hotspots">
    <table>
      <thead><tr>
        <th>{ui['th_site']}</th><th>{ui['th_alc']}</th>
        <th>LST media</th><th>{ui['th_why']}</th>
      </tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    </div>
"""


def write_html(lang, ui, paths, df, meta, unit_dir):
    slug = paths["slug"]
    t_rural = meta["t_rural"]
    c_ivc, c_frac, c_comp, c_max, c_suhi, c_ndvi, c_four = (
        chart_name(lang, "05_barras_indice"),
        chart_name(lang, "06_barras_frac_max43"),
        chart_name(lang, "08_componentes"),
        chart_name(lang, "06_barras_frac_max43"),
        chart_name(lang, "09_barras_suhi"),
        chart_name(lang, "07_barras_ndvi"),
        chart_name(lang, "05_cuatro_elementos"),
    )
    rows = []
    for r in df.itertuples():
        rows.append(
            f"<tr><td>{int(r.rank)}</td><td>{r.unit}</td><td>{r.ivc:.1f}</td>"
            f"<td>{100 * r.frac_lst_max_43:.0f}%</td><td>{100 * r.frac_lst_mean_43:.0f}%</td>"
            f"<td>{r.suhi_urban:.1f}</td><td>{r.ndvi_urban:.2f}</td>"
            f"<td>{100 * r.frac_veg_urban:.0f}%</td><td>{r.n_obs_urban:.1f}</td></tr>"
        )
    cards = []
    for r in df.itertuples():
        note = local_note(lang, slug, r.slug) if slug in RICH_SLUGS else ""
        note_html = f'<p class="note">{note}</p>' if note else ""
        zones = local_zones(lang, slug, r.slug) if slug in RICH_SLUGS else ""
        zones_html = f'<p class="note">{zones}</p>' if zones else ""
        alc_hot = paths["unit_assets"] / r.slug / "hotspots.png"
        inset_html = ""
        if alc_hot.exists():
            inset_html = (
                f'<figure><img src="assets/{unit_dir}/{r.slug}/hotspots.png" '
                f'alt="{ui["hotspot_alc"]}, {r.unit}">'
                f'<figcaption>{ui["hotspot_alc"]}</figcaption></figure>'
            )
        cards.append(f"""
    <section class="card" id="{r.slug}">
      <h2>{int(r.rank)}. {r.unit}</h2>
      {note_html}
      <ul class="stats">
        <li><b>IVC {METRIC_VERSION}</b> {r.ivc:.1f} / 100</li>
        <li><b>{ui['stat_max']}</b> {100 * r.frac_lst_max_43:.0f}% {ui['urban']} · {r.lst_max_urban:.1f} °C</li>
        <li><b>{ui['stat_mean']}</b> {100 * r.frac_lst_mean_43:.0f}% {ui['urban']} · {r.lst_mean_urban:.1f} °C</li>
        <li><b>{ui['stat_suhi']}</b> {r.suhi_urban:.1f} °C {ui['vs']} {t_rural:.1f} °C</li>
        <li><b>{ui['stat_ndvi']}</b> {r.ndvi_urban:.2f} · {100 * r.frac_veg_urban:.0f}% · {r.urban_km2:.1f} km² ({100 * r.urban_frac:.0f}%) · {r.n_obs_urban:.1f}</li>
      </ul>
      {inset_html}
      {zones_html}
      <div class="quad">
        <figure><img src="assets/{unit_dir}/{r.slug}/lst_max_43.png" alt="{ui['fig_max']}, {r.unit}"><figcaption>{ui['fig_max']}</figcaption></figure>
        <figure><img src="assets/{unit_dir}/{r.slug}/lst_mean.png" alt="{ui['fig_mean']}, {r.unit}"><figcaption>{ui['fig_mean']}</figcaption></figure>
        <figure><img src="assets/{unit_dir}/{r.slug}/ndvi.png" alt="NDVI, {r.unit}"><figcaption>{ui['fig_ndvi']}</figcaption></figure>
        <figure><img src="assets/{unit_dir}/{r.slug}/suhi.png" alt="SUHI, {r.unit}"><figcaption>{ui['fig_suhi']}</figcaption></figure>
      </div>
    </section>""")
    html = f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{ui['title']}</title>
  <link rel="icon" type="image/png" sizes="32x32" href="assets/favicon.png">
  <link rel="icon" href="assets/favicon.ico">
  <link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
  <link rel="alternate" hreflang="es" href="index.html">
  <link rel="alternate" hreflang="en" href="en.html">
  <link rel="alternate" hreflang="fr" href="fr.html">
  <style>{STYLE}</style>
</head>
<body>
  <header>
    <div class="wrap">
      <div class="titles">
        <div class="kicker">Anaplian.com · {ui['remote']} · {ui['priority']}</div>
        <h1>{ui['h1']}</h1>
        <p>{ui['subtitle']}</p>
        <p class="pdf-links">{ui['pdf_label']}: {' · '.join(f'<a href="{fn}">{lab}</a>' for lab, fn in ui['pdf_files'])}</p>
      </div>
      {lang_nav(lang)}
    </div>
  </header>
  <main>
    <nav class="toc" aria-label="{ui['toc_h']}">
      <h2>{ui['toc_h']}</h2>
      <ol>
        {''.join(f'<li><a href="#{anchor}">{label}</a></li>' for anchor, label in ui['toc_html'])}
      </ol>
    </nav>
    <h2 id="intro">{ui['why_index']}</h2>
    <p>{ui['intro_p1']}</p>
    <p>{ui['intro_p2']}</p>
    <p>{ui['intro_p3']}</p>
    <p>{ui['intro_p4']}</p>
    <h2 id="rank">{ui['rank_h']}</h2>
    <p>{ui['rank_city']}</p>
    {ranking_html_block(lang, ui, paths, slug) or _html_paras(ui['rank_alc'], ui['rank_why'])}
    {ranking_units_html(lang, ui, paths, slug)}
    <h2 id="methods">{ui['four']}</h2>
    <p class="metric"><b>{ui['metric_b']}</b> {ui['metric_p']}</p>
    <div class="methods">
      <div class="method"><h3>{ui['mh1']}</h3><p>{ui['method1']}</p></div>
      <div class="method"><h3>{ui['mh2']}</h3><p>{ui['method2']}</p></div>
      <div class="method"><h3>{ui['mh3']}</h3><p>{ui['method3']}</p></div>
      <div class="method"><h3>{ui['mh4']}</h3><p>{ui['method4']}</p></div>
    </div>
    <h2 id="map1">{ui['map1']}</h2>
    <figure>
      <img src="assets/01_{slug}_lst_max_43.png" alt="{ui['map1']}">
      <figcaption>{ui['cap1']}</figcaption>
    </figure>
    <h2 id="map2">{ui['map2']}</h2>
    <figure>
      <img src="assets/02_{slug}_lst_mean.png" alt="{ui['map2']}">
      <figcaption>{ui['cap2']}</figcaption>
    </figure>
    <h2 id="map3">{ui['map3']}</h2>
    <figure>
      <img src="assets/03_{slug}_ndvi.png" alt="{ui['map3']}">
      <figcaption>{ui['cap3']}</figcaption>
    </figure>
    <h2 id="map4">{ui['map4']}</h2>
    <figure>
      <img src="assets/04_{slug}_suhi.png" alt="{ui['map4']}">
      <figcaption>{ui['cap4']}</figcaption>
    </figure>
    {"" if slug == "cdmx" else hotspot_html_block(lang, ui, paths, slug)}
    <h2 id="order">{ui['order']}</h2>
    {f'<figure class="light"><img src="assets/{c_four}" alt="{ui["order"]}"></figure>' if (paths["assets"] / c_four).exists() else f'''
    <figure><img src="assets/{c_ivc}" alt="{ui['chart_ivc']}"></figure>
    <figure><img src="assets/{c_frac}" alt="{ui['chart_frac']}"></figure>
    <figure><img src="assets/{c_suhi}" alt="{ui['chart_suhi']}"></figure>
    <figure><img src="assets/{c_ndvi}" alt="{ui['chart_ndvi']}"></figure>
    '''}
    <p>{ui['summary']}</p>
    <h2 id="table">{ui.get('table_h') or ui['pdf_table']}</h2>
    <table>
      <thead><tr>
        <th>#</th><th>{ui['th_unit']}</th><th>IVC</th>
        <th>{ui['th_max']}</th><th>{ui['th_mean']}</th>
        <th>{ui['th_suhi']}</th><th>{ui['th_ndvi']}</th><th>{ui['th_veg']}</th><th>{ui['th_obs']}</th>
      </tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    {hotspot_html_block(lang, ui, paths, slug) if slug == "cdmx" else ""}
    <h2 id="units">{ui['units_h']}</h2>
    {''.join(cards)}
    <h2 id="why">{ui['why_prio']}</h2>
    <p>{ui['why1']}</p>
    <p>{ui['why2']}</p>
    <p>{ui['why_city']}</p>
  </main>
  <footer>
    <div class="wrap">
      <strong>Anaplian.com</strong> · USGS Landsat 8/9 C2 L2 · GHSL SMOD 2020 ·
      {ui['footer']}
    </div>
  </footer>
</body>
</html>
"""
    out = paths["site"] / HTML_NAME[lang]
    out.write_text(html, encoding="utf-8")
    print("HTML", out, flush=True)


def write_pdf(lang, ui, paths, df, meta, unit_dir):
    t_rural = meta["t_rural"]
    ASSETS, SITE = paths["assets"], paths["site"]
    UNIT_ASSETS = paths["unit_assets"]
    slug = paths["slug"]

    class PDF(FPDF):
        def footer(self):
            self.set_y(-10)
            self.set_font("Helvetica", size=8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 6, f"Anaplian.com   |   {self.page_no()}", align="C")

    font = Path("C:/Windows/Fonts/arial.ttf")
    fontb = Path("C:/Windows/Fonts/arialbd.ttf")
    pdf = PDF(format="A4", unit="mm")
    pdf.set_auto_page_break(auto=False, margin=10)
    pdf.set_margins(10, 10, 10)
    if font.exists():
        pdf.add_font("Body", "", str(font))
        pdf.add_font("Body", "B", str(fontb if fontb.exists() else font))
        face = "Body"
    else:
        face = "Helvetica"
    page_w, bottom, fit_n = 190, 287, 0

    def write_body(text, size=11, bold=False, color=(20, 20, 20), lh=5.6):
        pdf.set_x(pdf.l_margin)
        pdf.set_font(face, "B" if bold else "", size)
        pdf.set_text_color(*color)
        pdf.multi_cell(page_w, lh, text)

    def remain():
        return max(12.0, bottom - pdf.get_y())

    def jpeg_for_pdf(path, max_side=1400, quality=78):
        nonlocal fit_n
        fit_n += 1
        im = crop_uniform_border(Image.open(path).convert("RGB"))
        scale = min(1.0, max_side / max(im.size))
        if scale < 1:
            im = im.resize((int(im.width * scale), int(im.height * scale)), Image.Resampling.LANCZOS)
        tmp = ASSETS / f"_pdf_fit_{lang}_{fit_n}.jpg"
        im.save(tmp, format="JPEG", quality=quality, optimize=True)
        return tmp, im.size

    def fit_image(path, caption="", max_h=None, scale=1.0):
        if path is None or not Path(path).exists():
            return
        tmp, (iw, ih) = jpeg_for_pdf(path)
        aspect = ih / float(iw)
        cap = 7 if caption else 0
        avail_h = remain() - cap
        w, h = page_w * scale, page_w * scale * aspect
        limit = avail_h
        if max_h:
            limit = min(limit, max_h)
        if h > limit:
            h, w = limit, limit / aspect
        x, y = pdf.l_margin + (page_w - w) / 2.0, pdf.get_y()
        pdf.image(str(tmp), x=x, y=y, w=w, h=h)
        pdf.set_y(y + h + 0.6)
        if caption:
            write_body(caption, 8, False, (80, 80, 80), 3.5)

    def page_title(text):
        pdf.add_page()
        write_body(text, 12, True, (15, 15, 15), 6)
        pdf.ln(1)

    def cover_page():
        pdf.add_page()
        pdf.set_y(18)
        pdf.set_font(face, "B", 22)
        pdf.set_text_color(15, 15, 15)
        pdf.multi_cell(page_w, 10, ui["h1"], align="C")
        pdf.ln(6)
        cover = ASSETS / f"00_{slug}_cover.png"
        if not cover.exists():
            cover = ASSETS / f"04_{slug}_suhi.png"
        if not cover.exists():
            cover = ASSETS / f"01_{slug}_lst_max_43.png"
        if not cover.exists():
            return
        tmp, (iw, ih) = jpeg_for_pdf(cover, max_side=1600, quality=84)
        aspect = ih / float(iw)
        avail_h = bottom - 8 - pdf.get_y()
        w, h = page_w, page_w * aspect
        if h > avail_h:
            h, w = avail_h, avail_h / aspect
        x = pdf.l_margin + (page_w - w) / 2.0
        y = pdf.get_y()
        pdf.image(str(tmp), x=x, y=y, w=w, h=h)
        pdf.set_y(y + h + 1.5)
        cap = ui.get("cover_cap") or ""
        if cap:
            write_body(cap, 8, False, (80, 80, 80), 3.5)

    cover_page()

    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()
    write_body(ui["toc_h"], 14, True, (15, 15, 15), 7)
    pdf.ln(4)
    for line in ui["toc_pdf"]:
        write_body(str(line).replace("&gt;", ">"), 11, False, (25, 25, 25), 6.2)
        pdf.ln(1.2)
    page_title(ui["why_index"])
    for para in (ui["intro_p1"], ui["intro_p2"], ui["intro_p3"], ui["intro_p4"]):
        write_body(para, 10.5, False, (20, 20, 20), 5.5)
        pdf.ln(2.0)
    def write_paras(text):
        for para in str(text).split("\n\n"):
            para = para.strip()
            if not para:
                continue
            write_body(para, 10.5, False, (20, 20, 20), 5.5)
            pdf.ln(2.0)

    page_title(ui["rank_h"])
    write_paras(ui["rank_city"])
    city_comp = ASSETS / chart_name(lang, "ranking_ciudades_componentes")
    if city_comp.exists():
        if remain() < 70:
            pdf.add_page()
        fit_image(city_comp, ui["cap_city_comp"], max_h=78, scale=0.72)
        pdf.ln(1.5)
    write_paras(ui["rank_alc"])
    write_paras(ui["rank_why"])
    if ui.get("rank_soil"):
        write_paras(ui["rank_soil"])
    if slug in RICH_SLUGS and ui.get("subdiv_h"):
        page_title(ui["subdiv_h"])
        write_paras(ui["subdiv_p"])
        unit_top = ASSETS / chart_name(lang, "ranking_unidades_top")
        if unit_top.exists():
            if remain() < 100:
                pdf.add_page()
            fit_image(unit_top, ui["cap_unit_top"], max_h=155)
            pdf.ln(1.0)
        unit_comp = ASSETS / chart_name(lang, "ranking_unidades_componentes")
        if unit_comp.exists():
            pdf.add_page()
            fit_image(unit_comp, ui["cap_unit_comp"], max_h=165, scale=0.92)
    else:
        write_paras(ui.get("rank_units") or "")
        unit_top = ASSETS / chart_name(lang, "ranking_unidades_top")
        if unit_top.exists():
            if remain() < 100:
                pdf.add_page()
            fit_image(unit_top, ui["cap_unit_top"], max_h=155)
        unit_comp = ASSETS / chart_name(lang, "ranking_unidades_componentes")
        if unit_comp.exists():
            pdf.add_page()
            fit_image(unit_comp, ui["cap_unit_comp"], max_h=165, scale=0.92)
    pdf.set_auto_page_break(auto=False, margin=10)

    titles = [ui["pdf_m1"], ui["pdf_m2"], ui["pdf_m3"], ui["pdf_m4"]]
    methods = [ui["method1"], ui["method2"], ui["method3"], ui["method4"]]
    imgs = [
        (ASSETS / f"01_{slug}_lst_max_43.png", ui["pdf_c1"]),
        (ASSETS / f"02_{slug}_lst_mean.png", ui["pdf_c2"]),
        (ASSETS / f"03_{slug}_ndvi.png", ui["pdf_c3"]),
        (ASSETS / f"04_{slug}_suhi.png", ui["pdf_c4"]),
    ]
    for title, method, (img, cap) in zip(titles, methods, imgs):
        page_title(title)
        write_body(method, 9.5, False, (30, 30, 30), 5.0)
        pdf.ln(1.5)
        fit_image(img, cap)

    four_chart = ASSETS / chart_name(lang, "05_cuatro_elementos")
    if four_chart.exists():
        page_title(ui.get("pdf_four") or ui["pdf_index"])
        fit_image(four_chart, max_h=248)
    else:
        page_title(ui["pdf_index"])
        fit_image(ASSETS / chart_name(lang, "05_barras_indice"), ui["pdf_index_cap"])
        page_title(ui["pdf_comp"])
        fit_image(ASSETS / chart_name(lang, "08_componentes"))
        page_title(ui["pdf_frac"])
        fit_image(ASSETS / chart_name(lang, "06_barras_frac_max43"))
        page_title(ui["pdf_suhi_p"])
        fit_image(ASSETS / chart_name(lang, "09_barras_suhi"), ui["pdf_suhi_cap"])
        page_title(ui["pdf_ndvi_p"])
        fit_image(ASSETS / chart_name(lang, "07_barras_ndvi"))

    page_title(ui["pdf_table"])
    headers = ["#", ui["th_unit"][:10], "IVC", "Max43%", "Med43%", "SUHI", "NDVI"]
    col_w = [12, 58, 22, 26, 26, 24, 22]
    pdf.set_font(face, "B", 8)
    pdf.set_fill_color(20, 20, 20)
    pdf.set_text_color(255, 255, 255)
    pdf.set_x(pdf.l_margin)
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 7, h, fill=True, align="C" if i else "L")
    pdf.ln()
    fill = False
    for r in df.itertuples():
        if pdf.get_y() > 275:
            page_title(ui["pdf_table"])
            pdf.set_font(face, "B", 8)
            pdf.set_fill_color(20, 20, 20)
            pdf.set_text_color(255, 255, 255)
            pdf.set_x(pdf.l_margin)
            for i, h in enumerate(headers):
                pdf.cell(col_w[i], 7, h, fill=True, align="C" if i else "L")
            pdf.ln()
        pdf.set_x(pdf.l_margin)
        pdf.set_font(face, "", 8)
        pdf.set_text_color(20, 20, 20)
        pdf.set_fill_color(247, 244, 239) if fill else pdf.set_fill_color(255, 255, 255)
        vals = [str(int(r.rank)), str(r.unit)[:28], f"{r.ivc:.1f}",
                f"{100 * r.frac_lst_max_43:.0f}", f"{100 * r.frac_lst_mean_43:.0f}",
                f"{r.suhi_urban:.1f}", f"{r.ndvi_urban:.2f}"]
        for i, v in enumerate(vals):
            pdf.cell(col_w[i], 6.4, v, fill=True, align="L" if i < 2 else "R")
        pdf.ln()
        fill = not fill

    if slug == "cdmx":
        catalog_path = Path(__file__).resolve().parents[1] / "data" / "hotspots" / "cdmx_hotspots.json"
        page_title(ui["pdf_hotspot"])
        write_body(ui["hotspot_p"], 9.5, False, (30, 30, 30), 5.0)
        pdf.ln(1.5)
        if catalog_path.exists():
            data = json.loads(catalog_path.read_text(encoding="utf-8"))
            top = set(data.get("top5") or [])
            for s in data.get("sites") or []:
                if remain() < 22:
                    pdf.add_page()
                mark = "* " if s.get("id") in top else ""
                lst = s.get("lst_mean_C")
                lst_txt = f"{lst:.1f} C" if lst is not None else ""
                why = (s.get("why") or {}).get(lang) or (s.get("why") or {}).get("es") or ""
                write_body(
                    f"{mark}{s.get('name', '')}  ·  {s.get('alcaldia', '')}"
                    + (f"  ·  LST media {lst_txt}" if lst_txt else ""),
                    9.0, True, (20, 20, 20), 4.4,
                )
                if why:
                    write_body(why, 8.5, False, (50, 50, 50), 4.2)
                pdf.ln(0.8)

    pdf.add_page()
    write_body(ui["pdf_units"], 12, True, (15, 15, 15), 6)
    pdf.ln(2)
    first_unit = True
    for r in df.itertuples():
        if not first_unit:
            pdf.add_page()
        first_unit = False
        write_body(f"{int(r.rank)}. {r.unit}   ·   IVC {r.ivc:.1f}", 12, True, (15, 15, 15), 6)
        pdf.ln(1)
        note = local_note(lang, slug, r.slug) if slug in RICH_SLUGS else ""
        if note:
            write_body(note, 9.0, False, (40, 40, 40), 4.6)
            pdf.ln(1.0)
        write_body(
            f"LST max > 43 C: {100 * r.frac_lst_max_43:.0f}% {ui['urban']} ({r.lst_max_urban:.1f} C). "
            f"LST mean > 43 C: {100 * r.frac_lst_mean_43:.0f}% {ui['urban']} ({r.lst_mean_urban:.1f} C). "
            f"SUHI {r.suhi_urban:.1f} C {ui['vs']} {t_rural:.1f} C. "
            f"NDVI {r.ndvi_urban:.2f}; {r.urban_km2:.1f} km2; {r.n_obs_urban:.1f} obs./pixel.",
            8.5, False, (40, 40, 40), 4.2,
        )
        pdf.ln(1.0)
        alc_hot = UNIT_ASSETS / r.slug / "hotspots.png"
        if alc_hot.exists() and remain() > 70:
            fit_image(alc_hot, ui["hotspot_alc"], max_h=88)
            pdf.ln(0.6)
        zones = local_zones(lang, slug, r.slug) if slug in RICH_SLUGS else ""
        if zones:
            write_body(zones, 8.8, False, (40, 40, 40), 4.4)
            pdf.ln(0.8)
        paths_img = [
            UNIT_ASSETS / r.slug / "lst_max_43.png",
            UNIT_ASSETS / r.slug / "lst_mean.png",
            UNIT_ASSETS / r.slug / "ndvi.png",
            UNIT_ASSETS / r.slug / "suhi.png",
        ]
        labels = ui["pdf_quad"]
        gap, cap_h = 3.0, 5.0
        cell_w = (page_w - gap) / 2.0
        cell_h = remain() / 2.0
        start_y = pdf.get_y()
        for j, (path, lab) in enumerate(zip(paths_img, labels)):
            if not path.exists():
                continue
            col, row = j % 2, j // 2
            x = pdf.l_margin + col * (cell_w + gap)
            y = start_y + row * cell_h
            tmp, (iw, ih) = jpeg_for_pdf(path, max_side=900, quality=75)
            box_h = cell_h - cap_h
            scale = min(cell_w / iw, box_h / ih)
            w, h = iw * scale, ih * scale
            pdf.image(str(tmp), x=x + (cell_w - w) / 2.0, y=y, w=w, h=h)
            pdf.set_xy(x, y + box_h + 0.2)
            pdf.set_font(face, "", 8)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(cell_w, cap_h - 0.6, lab, align="C")

    page_title(ui["pdf_why"])
    for para in (ui["why1"], ui["why2"], ui["why_city"]):
        write_body(para, 10.5, False, (20, 20, 20), 5.5)
        pdf.ln(2.0)

    pdf_path = SITE / f"{PDF_STEM[lang]}_{ui['pdf']}_2026.pdf"
    pdf.output(str(pdf_path))
    for leftover in ASSETS.glob(f"_pdf_fit_{lang}_*"):
        leftover.unlink(missing_ok=True)
    print("PDF", pdf_path, flush=True)


def append_internal_log(message: str, files: list[str] | None = None) -> None:
    path = Path(__file__).resolve().parent / "internal_change_log.md"
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    lines = [f"- **{stamp}** — {message}"]
    for name in files or []:
        lines.append(f"  - `{name}`")
    entry = "\n".join(lines) + "\n"
    if path.exists():
        path.write_text(path.read_text(encoding="utf-8") + entry, encoding="utf-8")
    else:
        path.write_text(
            "# Log interno de cambios\n\n"
            "Registro de modificaciones a la página Anaplian y a los reportes PDF.\n\n"
            + entry,
            encoding="utf-8",
        )


def localize_site(cfg, paths, df, meta, *, unit_dir="unidades", langs=LANGS, make_charts=None):
    if "unit" not in df.columns and "alcaldia" in df.columns:
        df = df.rename(columns={"alcaldia": "unit"})
    meta = dict(meta)
    meta.setdefault("slug", paths["slug"])
    cfg = dict(cfg)
    cfg.setdefault("slug", paths["slug"])
    if paths.get("slug") in RICH_SLUGS:
        copy_ranking_charts(paths["assets"])
    ensure_favicon(paths["assets"])
    for lang in langs:
        ui = copy_pack(lang, cfg, df, meta)
        if make_charts:
            make_charts(lang, ui, paths["assets"], df)
        write_html(lang, ui, paths, df, meta, unit_dir)
        write_pdf(lang, ui, paths, df, meta, unit_dir)
    pdfs = [f"{PDF_STEM[lang]}_{city_pack(paths['slug'], lang, cfg)['pdf']}_2026.pdf" for lang in langs]
    extra = []
    slug = paths.get("slug")
    if slug in RICH_SLUGS:
        extra.append(f"assets/00_{slug}_cover.png")
    append_internal_log(
        f"Actualización del sitio {slug}: HTML {', '.join(langs)} y PDF regenerados.",
        [str(HTML_NAME[lang]) for lang in langs] + pdfs + extra,
    )
