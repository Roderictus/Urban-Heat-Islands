# Îlots de chaleur à Paris

**Surtitre.** Anaplian.com · télédétection urbaine

**Titre.** Îlots de chaleur à Paris

**Chapô.** Avril et mai 2026 · Landsat 8 et 9 · 20 arrondissements · température de surface et NDVI

## Introduction

La hausse de la température moyenne de la planète aggrave la vulnérabilité aux chaleurs excessives. Il ne s'agit pas seulement d'un degré de plus dans la moyenne globale : cette hausse pousse davantage de journées au-delà de seuils dangereux pour la santé, le travail en extérieur et les réseaux d'eau et d'énergie. En ville, le risque se concentre. L'asphalte, le béton, les toitures sombres et le métal absorbent une grande part du rayonnement solaire et le restituent en chaleur. Rues étroites et immeubles forment des canyons qui piègent l'air chaud. Le résultat : des îlots de chaleur — parkings, hangars, avenues et toitures où la surface atteint des températures que le corps ne tolère pas en exposition prolongée.

Avec Landsat 8 et Landsat 9, nous cartographions les surfaces les plus chaudes de Paris et de ses 20 arrondissements. La carte est la moyenne par pixel de 7 scènes d'avril et mai 2026, acquises vers 12 h 40, heure locale. Sur chaque pixel, nuages, ombres et valeurs invalides sont masqués avant de moyenner ; on ne jette pas la scène entière. Le capteur thermique — bande 10, entre 10,6 et 11,2 micromètres — estime la chaleur du sol, des toits et du bitume, pas celle de l'air à l'ombre. Seules les surfaces au-dessus de 25 °C sont coloriées. En parallèle, le NDVI montre où la végétation est dense. La température de la commune se compare à la moyenne des zones rurales dans un rayon de 20 km (ceinture verte d'Île-de-France). Le 98e centile du composite atteint 27.9 °C ; l'écart urbain–rural (SUHI) est de +3.6 °C.

Ces pics ne sont pas un épisode isolé : avec davantage de vagues de chaleur et de surfaces imperméables, ils tendent à s'aggraver. Ils servent à repérer des lieux d'intervention. L'urbanisme tactique permet de tester ombres temporaires, peinture à fort albédo dans les cours d'école, et trottoirs plus perméables. La végétation reste le levier le plus durable : un arbre intercepte le soleil et rafraîchit l'air par transpiration. Bois de Boulogne, bois de Vincennes, coulées de la Seine et toitures végétalisées réduisent la charge thermique. La donnée satellitaire n'indique pas le projet local ; elle montre où agir d'abord.

## En une ligne

À Paris, au printemps 2026, la température moyenne de surface de la commune est de 21.9 °C, contre 18.3 °C dans la ceinture rurale (+3.6 °C). Le NDVI moyen est de 0.35. 9e arrondissement est l'arrondissement le plus chaud en moyenne ; 16e arrondissement le plus frais ; 12e arrondissement le plus végétalisé.

## Méthodologie

Les cartes sont un composite large : la moyenne par pixel des 7 scènes Landsat 8 et Landsat 9 (Collection 2, niveau 2) acquises entre le 1er avril et le 31 mai 2026. On ne jette pas une scène entière pour cause de nuages : sur chaque pixel, le remplissage, les nuages, les ombres et les températures hors de la plage valide (0 à 80 °C) sont masqués, puis les observations utiles sont moyennées. Les satellites survolent Paris vers 12 h 40, heure locale (près de 10 h 40 UTC). Ce qui est peint n'est pas l'air à l'ombre, mais la température de surface — toits, asphalte, sol nu et végétation — avec la bande 10 de l'infrarouge thermique (10,6 à 11,2 micromètres ; LST = 0,00341802 × DN + 149 − 273,15). En jaune à rouge n'apparaissent que les surfaces au-dessus de 25 °C. Le verdure est mesuré par le NDVI (rouge et proche infrarouge). L'écart urbain–rural soustrait 18.3 °C, moyenne des classes rurales du GHSL 2020 (SMOD 11, 12 et 13, hors eau) dans un rayon de 20 km autour de la commune. Les 20 arrondissements municipaux viennent des données ouvertes de la Ville de Paris.

## Arrondissements

| Arrondissement | Max (°C) | Moyenne (°C) | SUHI (°C) | NDVI |
| --- | ---: | ---: | ---: | ---: |
| 9e arrondissement | 47.6 | 25.0 | +6.7 | 0.12 |
| 8e arrondissement | 50.8 | 24.5 | +6.2 | 0.21 |
| 10e arrondissement | 50.5 | 24.5 | +6.2 | 0.18 |
| 2e arrondissement | 47.3 | 24.1 | +5.8 | 0.09 |
| 17e arrondissement | 51.2 | 23.6 | +5.2 | 0.25 |
| 19e arrondissement | 54.0 | 23.5 | +5.2 | 0.35 |
| 18e arrondissement | 52.4 | 23.3 | +4.9 | 0.25 |
| 13e arrondissement | 53.7 | 22.9 | +4.5 | 0.32 |
| 4e arrondissement | 48.7 | 22.7 | +4.4 | 0.20 |
| 11e arrondissement | 48.5 | 22.7 | +4.4 | 0.22 |
| 3e arrondissement | 47.2 | 22.4 | +4.1 | 0.15 |
| 1er arrondissement | 48.0 | 22.3 | +4.0 | 0.18 |
| 14e arrondissement | 50.0 | 22.1 | +3.8 | 0.35 |
| 20e arrondissement | 53.1 | 21.9 | +3.6 | 0.35 |
| 5e arrondissement | 46.9 | 21.7 | +3.4 | 0.25 |
| 15e arrondissement | 56.5 | 21.5 | +3.2 | 0.30 |
| 6e arrondissement | 47.5 | 21.2 | +2.9 | 0.23 |
| 7e arrondissement | 47.6 | 21.2 | +2.9 | 0.29 |
| 12e arrondissement | 55.7 | 20.7 | +2.4 | 0.54 |
| 16e arrondissement | 50.2 | 19.3 | +1.0 | 0.51 |
