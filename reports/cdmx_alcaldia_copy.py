"""Short alcaldía notes for the CDMX IVC report (ES / EN / FR)."""

NOTES = {
    "venustiano_carranza": {
        "es": "La alcaldía más vulnerable (IVC 83). Casi todo el tejido urbano supera 43 °C en el máximo por píxel y el SUHI llega a +18 °C. Aquí están el AICM, la TAPO y la Ciudad Deportiva: pistas, andenes y losa continua, sin suelo de conservación que baje la media.",
        "en": "The most vulnerable borough (IVC 83). Almost all of the urban fabric exceeds 43 °C at pixel-max and SUHI reaches +18 °C. AICM, TAPO and the sports city sit here: runways, platforms and continuous slab, with no conservation land to pull the mean down.",
        "fr": "La délégation la plus vulnérable (IVC 83). Presque tout le tissu urbain dépasse 43 °C au max-pixel et le SUHI atteint +18 °C. AICM, TAPO et la cité sportive s’y trouvent : pistes, quais et dalle continue, sans terre de conservation pour baisser la moyenne.",
    },
    "iztacalco": {
        "es": "La más pequeña y enteramente urbana (IVC 80). CETRAM Pantitlán concentra el transbordo; techos y viaducto cubren el resto. El 97 % del máximo urbano supera 43 °C y el SUHI es +17 °C: no hay rural interno que diluya el índice.",
        "en": "The smallest, fully urban borough (IVC 80). CETRAM Pantitlán holds the transfer; roofs and the viaduct cover the rest. 97 % of urban pixel-max exceeds 43 °C and SUHI is +17 °C: there is no internal rural land to dilute the index.",
        "fr": "La plus petite, entièrement urbaine (IVC 80). Le CETRAM Pantitlán porte la correspondance ; toits et viaduc couvrent le reste. 97 % du max-pixel urbain dépasse 43 °C et le SUHI est de +17 °C : pas de rural interne pour diluer l’indice.",
    },
    "iztapalapa": {
        "es": "La mayor masa urbana (IVC 76, 113 km²). Oriente pavimentado y la Central de Abasto; 93 % del máximo > 43 °C. El verdor es bajo (NDVI 0.17) y el SUHI se satura en el tope del índice (+16 °C). El ranking de ciudad se decide en buena parte aquí.",
        "en": "The largest urban mass (IVC 76, 113 km²). Paved east side and Central de Abasto; 93 % of pixel-max > 43 °C. Greenness is low (NDVI 0.17) and SUHI hits the index cap (+16 °C). Much of the city ranking is decided here.",
        "fr": "La plus grande masse urbaine (IVC 76, 113 km²). Est minéral et Central de Abasto ; 93 % du max-pixel > 43 °C. Peu de verdure (NDVI 0,17) et SUHI au plafond de l’indice (+16 °C). Une bonne part du classement de la ville se joue ici.",
    },
    "azcapotzalco": {
        "es": "Norte industrial (IVC 75). Vallejo y El Rosario: naves, patios de carga y poco árbol. El pico de LST está entre los más altos de la ciudad; el 96 % del urbano cruza 43 °C en el máximo. No es desierto: es techo y concreto junto a GAM.",
        "en": "Industrial north (IVC 75). Vallejo and El Rosario: sheds, yards and few trees. The LST peak is among the city’s highest; 96 % of urban land crosses 43 °C at pixel-max. Not desert: roof and concrete next to GAM.",
        "fr": "Nord industriel (IVC 75). Vallejo et El Rosario : hangars, cours et peu d’arbres. Le pic de LST est parmi les plus hauts de la ville ; 96 % de l’urbain franchit 43 °C au max-pixel. Pas un désert : toits et béton contre GAM.",
    },
    "cuauhtemoc": {
        "es": "Centro histórico y corredor Reforma (IVC 71). La Merced, el Zócalo y Juárez: piedra, lámina y comercio de calle. El 85 % del máximo urbano > 43 °C; hay algo más de media vegetal que en VC, pero el SUHI sigue en +16 °C.",
        "en": "Historic centre and Reforma corridor (IVC 71). La Merced, the Zócalo and Juárez: stone, metal roofs and street trade. 85 % of urban pixel-max > 43 °C; a little more vegetation than VC, but SUHI is still +16 °C.",
        "fr": "Centre historique et couloir Reforma (IVC 71). La Merced, le Zócalo et Juárez : pierre, tôle et commerce de rue. 85 % du max-pixel urbain > 43 °C ; un peu plus de végétation qu’à VC, mais le SUHI reste à +16 °C.",
    },
    "tlahuac": {
        "es": "Dos mitades (IVC 64). El poblado y el oriente urbano se calientan (84 % máx. > 43 °C); chinampas y conservación al sur bajan la media de la alcaldía. El índice urbano sigue alto porque el GHSL ≥ 21 está en el asfalto, no en la chinampa.",
        "en": "Two halves (IVC 64). The town and urban east heat up (84 % max > 43 °C); chinampas and southern conservation land pull the borough mean down. The urban index stays high because GHSL ≥ 21 sits on asphalt, not on the chinampa.",
        "fr": "Deux moitiés (IVC 64). Le bourg et l’est urbain chauffent (84 % max > 43 °C) ; chinampas et conservation sud baissent la moyenne. L’indice urbain reste haut car le GHSL ≥ 21 est sur l’asphalte, pas sur la chinampa.",
    },
    "gustavo_a_madero": {
        "es": "Puerta norte (IVC 63). Indios Verdes y la Central del Norte: transbordo y losa. El 84 % del máximo urbano > 43 °C; hay más área y un poco más de verdor que en Iztacalco, pero el SUHI urbano sigue en +13 °C.",
        "en": "Northern gate (IVC 63). Indios Verdes and Central del Norte: transfer and slab. 84 % of urban pixel-max > 43 °C; more area and a little more green than Iztacalco, but urban SUHI is still +13 °C.",
        "fr": "Porte nord (IVC 63). Indios Verdes et Central del Norte : correspondance et dalle. 84 % du max-pixel urbain > 43 °C ; plus de surface et un peu plus de verdure qu’Iztacalco, mais le SUHI urbain reste à +13 °C.",
    },
    "benito_juarez": {
        "es": "Alcaldía 100 % urbana y compacta (IVC 59). Viaducto, WTC y Nápoles: el máximo cruza 43 °C en el 83 % del suelo, pero la media del compuesto casi no lo hace (1 %). Es pico de azotea, no una carga continua de mediodía.",
        "en": "Fully urban and compact (IVC 59). Beltway, WTC and Nápoles: pixel-max crosses 43 °C on 83 % of the land, but the composite mean almost never does (1 %). Roof peak, not an all-day load.",
        "fr": "Entièrement urbaine et compacte (IVC 59). Viaduc, WTC et Nápoles : le max-pixel franchit 43 °C sur 83 % du sol, mais la moyenne du composite presque jamais (1 %). Pic de toiture, pas une charge continue.",
    },
    "coyoacan": {
        "es": "Contraste interno (IVC 57). Ciudad Universitaria y el pedregal enfrían; Taxqueña y el Anillo Periférico calientan. Tres cuartas partes del máximo urbano > 43 °C, con más NDVI (0.27) que el oriente.",
        "en": "Internal contrast (IVC 57). Ciudad Universitaria and the Pedregal cool; Taxqueña and the beltway heat. Three quarters of urban pixel-max > 43 °C, with more NDVI (0.27) than the east.",
        "fr": "Contraste interne (IVC 57). Ciudad Universitaria et le Pedregal refroidissent ; Taxqueña et le périphérique chauffent. Trois quarts du max-pixel urbain > 43 °C, avec plus de NDVI (0,27) que l’est.",
    },
    "milpa_alta": {
        "es": "Polígono rural con poblados calientes (IVC 49). Solo el 17 % es urbano GHSL, pero ese 17 % tiene 70 % del máximo > 43 °C. El índice de alcaldía mezcla cabecera (Villa Milpa Alta) y ladera; no describe el bosque.",
        "en": "Rural polygon with hot villages (IVC 49). Only 17 % is GHSL urban, but that 17 % has 70 % of pixel-max > 43 °C. The borough index mixes the town seat (Villa Milpa Alta) and the slope; it does not describe the forest.",
        "fr": "Polygone rural à villages chauds (IVC 49). Seuls 17 % sont urbains GHSL, mais ces 17 % ont 70 % du max-pixel > 43 °C. L’indice mélange le chef-lieu (Villa Milpa Alta) et le versant ; il ne décrit pas la forêt.",
    },
    "miguel_hidalgo": {
        "es": "Chapultepec frente a Tacubaya (IVC 43). La mitad del suelo urbano tiene verdor ≥ 0.30; el 43 % del máximo aún > 43 °C. El SUHI (+12 °C) es isla respecto al Ajusco, no un desierto interno.",
        "en": "Chapultepec versus Tacubaya (IVC 43). Half of urban land has greenness ≥ 0.30; 43 % of pixel-max is still > 43 °C. SUHI (+12 °C) is an island versus the Ajusco, not an internal desert.",
        "fr": "Chapultepec face à Tacubaya (IVC 43). La moitié du sol urbain a une verdure ≥ 0,30 ; 43 % du max-pixel reste > 43 °C. Le SUHI (+12 °C) est un îlot vis-à-vis de l’Ajusco, pas un désert interne.",
    },
    "alvaro_obregon": {
        "es": "Observatorio y barrancas (IVC 40). El CETRAM y el periférico calientan un 36 % del máximo urbano; las cañadas bajan NDVI medio de la alcaldía. El índice pesa el GHSL ≥ 21, no el bosque de las laderas.",
        "en": "Observatorio and ravines (IVC 40). The CETRAM and beltway heat 36 % of urban pixel-max; the canyons pull borough-mean NDVI down. The index weights GHSL ≥ 21, not the hillside forest.",
        "fr": "Observatorio et ravins (IVC 40). Le CETRAM et le périphérique chauffent 36 % du max-pixel urbain ; les canyons baissent le NDVI moyen. L’indice pèse le GHSL ≥ 21, pas la forêt des versants.",
    },
    "xochimilco": {
        "es": "Centro y chinampas (IVC 37). Embarcaderos y avenida se calientan; el 38 % del máximo urbano > 43 °C. El NDVI 0.39 y el agua agrícola bajan el IVC de la alcaldía sin apagar el andén.",
        "en": "Centre and chinampas (IVC 37). Piers and the avenue heat up; 38 % of urban pixel-max > 43 °C. NDVI 0.39 and agricultural water lower the borough IVC without cooling the dock.",
        "fr": "Centre et chinampas (IVC 37). Embarcadères et avenue chauffent ; 38 % du max-pixel urbain > 43 °C. Le NDVI 0,39 et l’eau agricole baissent l’IVC sans éteindre le quai.",
    },
    "la_magdalena_contreras": {
        "es": "Poblado contra sierra (IVC 34). Solo un tercio del polígono es urbano; ese tercio aún tiene SUHI +11 °C. El 24 % del máximo > 43 °C. El bosque del sur-poniente es la referencia rural de toda la ciudad, no un “enfriamiento” del centro de Contreras.",
        "en": "Town against sierra (IVC 34). Only a third of the polygon is urban; that third still has SUHI +11 °C. 24 % of pixel-max > 43 °C. The south-west forest is the rural reference for the whole city, not a cooling of Contreras town.",
        "fr": "Bourg contre sierra (IVC 34). Un tiers seulement du polygone est urbain ; ce tiers a encore un SUHI de +11 °C. 24 % du max-pixel > 43 °C. La forêt sud-ouest est la référence rurale de toute la ville, pas un « refroidissement » du centre de Contreras.",
    },
    "tlalpan": {
        "es": "Hospitales frente al Ajusco (IVC 33). El corredor de institutos y periférico es losa; el 32 % del máximo urbano > 43 °C. Dos tercios del polígono no son urbanos: el bosque que define T_rural 25.6 °C está sobre todo aquí y en Contreras.",
        "en": "Hospitals facing the Ajusco (IVC 33). The institute corridor and beltway are slab; 32 % of urban pixel-max > 43 °C. Two thirds of the polygon is not urban: the forest that sets T_rural 25.6 °C is mostly here and in Contreras.",
        "fr": "Hôpitaux face à l’Ajusco (IVC 33). Le couloir d’instituts et le périphérique sont dalle ; 32 % du max-pixel urbain > 43 °C. Deux tiers du polygone ne sont pas urbains : la forêt qui fixe T_rural 25,6 °C est surtout ici et à Contreras.",
    },
    "cuajimalpa_de_morelos": {
        "es": "La menos vulnerable (IVC 11). Santa Fe es una isla de torres y estacionamientos; el 5 % del máximo urbano > 43 °C y el SUHI urbano es solo +3.7 °C. El bosque de agua domina el polígono y acerca T urbana a T rural.",
        "en": "The least vulnerable (IVC 11). Santa Fe is an island of towers and parking; 5 % of urban pixel-max > 43 °C and urban SUHI is only +3.7 °C. The water forest dominates the polygon and pulls urban T toward rural T.",
        "fr": "La moins vulnérable (IVC 11). Santa Fe est un îlot de tours et parkings ; 5 % du max-pixel urbain > 43 °C et le SUHI urbain n’est que de +3,7 °C. La forêt d’eau domine le polygone et rapproche T urbaine de T rurale.",
    },
}


# One or two lines on the boxed sites in each borough hotspot inset.
ZONES = {
    "venustiano_carranza": {
        "es": "En los recuadros: AICM — pistas, plataformas y terminales de asfalto y concreto; la cobertura del aeropuerto sustituye áreas verdes y registra la LST media más alta de la muestra. TAPO — andenes y lámina, filas al sol junto al aeropuerto. Ciudad Deportiva (Autódromo / Foro Sol) — pista, estacionamientos y gradas, pavimento masivo. Mercado Jamaica — patios abiertos y techos de lámina en el oriente pavimentado.",
        "en": "In the boxes: AICM — runways, aprons and terminals of asphalt and concrete; airport coverage replaces green space and records the sample’s highest mean LST. TAPO — platforms and metal roofs, queues in the sun beside the airport. Sports city (Autódromo / Foro Sol) — track, parking and stands, massive pavement. Jamaica market — open yards and metal roofs on the paved east side.",
        "fr": "Dans les encadrés : AICM — pistes, aires et terminaux d’asphalte et de béton ; la couverture aéroportuaire remplace les espaces verts et enregistre la LST moyenne la plus haute de l’échantillon. TAPO — quais et tôle, files au soleil contre l’aéroport. Cité sportive (Autódromo / Foro Sol) — piste, parkings et gradins, revêtement massif. Marché Jamaica — cours ouvertes et toits de tôle dans l’est minéral.",
    },
    "iztacalco": {
        "es": "En el recuadro: CETRAM Pantitlán, el transbordo más cargado de la red — metro, Mexibús y autobuses sobre losa de concreto; colas y andenes a cielo abierto, sin vegetación que corte la radiación.",
        "en": "In the box: CETRAM Pantitlán, the busiest transfer in the network — metro, Mexibús and buses on a concrete slab; open-air queues and platforms, with no vegetation to cut the radiation.",
        "fr": "Dans l’encadré : CETRAM Pantitlán, la correspondance la plus chargée du réseau — métro, Mexibús et bus sur dalle de béton ; files et quais à ciel ouvert, sans végétation pour couper le rayonnement.",
    },
    "iztapalapa": {
        "es": "En el recuadro: Central de Abasto, donde se encuentran bodegas en las que se almacenan y reparten perecederos; la falta de vegetación, el asfalto de patios y andenes y las naves de concreto y lámina inciden en la temperatura de superficie (~46 °C).",
        "en": "In the box: Central de Abasto, warehouses where perishables are stored and dispatched; lack of vegetation, asphalt yards and platforms, and concrete and metal sheds drive surface temperature (~46 °C).",
        "fr": "Dans l’encadré : Central de Abasto, hangars où l’on stocke et répartit les denrées périssables ; le manque de végétation, l’asphalte des cours et quais et les naves de béton et de tôle pèsent sur la température de surface (~46 °C).",
    },
    "azcapotzalco": {
        "es": "En los recuadros: Vallejo — corredor industrial de naves, patios de carga y poco árbol; el concreto de las cubiertas y el asfalto de los patios concentran el pico de LST. CETRAM El Rosario — losa y autobuses en el norte de la alcaldía, con mínima cobertura vegetal.",
        "en": "In the boxes: Vallejo — industrial corridor of sheds, loading yards and few trees; roof concrete and yard asphalt concentrate the LST peak. CETRAM El Rosario — slab and buses in the north of the borough, with almost no green cover.",
        "fr": "Dans les encadrés : Vallejo — couloir industriel de hangars, cours de chargement et peu d’arbres ; le béton des toits et l’asphalte des cours concentrent le pic de LST. CETRAM El Rosario — dalle et bus dans le nord de la délégation, presque sans couvert végétal.",
    },
    "cuauhtemoc": {
        "es": "En los recuadros: La Merced — mercado histórico y comercio de calle, techos de lámina y poca sombra. Zócalo — plaza de piedra y azoteas del centro histórico; turismo y comercio al sol. Reforma–Juárez — corredor de oficinas y asfalto, terrazas compactas con vegetación fragmentada (Alameda).",
        "en": "In the boxes: La Merced — historic market and street trade, metal roofs and little shade. Zócalo — stone plaza and historic-centre roofs; tourism and trade in the sun. Reforma–Juárez — office and asphalt corridor, compact terraces with fragmented greenery (Alameda).",
        "fr": "Dans les encadrés : La Merced — marché historique et commerce de rue, toits de tôle et peu d’ombre. Zócalo — place de pierre et toits du centre historique ; tourisme et commerce au soleil. Reforma–Juárez — couloir de bureaux et d’asphalte, terrasses compactes et verdure fragmentée (Alameda).",
    },
    "tlahuac": {
        "es": "En el recuadro: centro de Tláhuac, la cabecera urbana asfaltada; el IVC alto está en el poblado y no en las chinampas ni en la conservación del sur, donde sí hay agua y verdor.",
        "en": "In the box: downtown Tláhuac, the paved urban seat; the high IVC sits in the town, not in the chinampas or southern conservation land, where water and green remain.",
        "fr": "Dans l’encadré : centre de Tláhuac, chef-lieu urbain asphalté ; l’IVC élevé est dans le bourg, pas dans les chinampas ni la conservation sud, où restent l’eau et la verdure.",
    },
    "gustavo_a_madero": {
        "es": "En los recuadros: CETRAM Indios Verdes — puerta norte del metro, transbordo masivo, techos bajos y andenes descubiertos. Central del Norte — terminal de autobuses, andenes y losa junto a la franja industrial del norte.",
        "en": "In the boxes: CETRAM Indios Verdes — northern metro gate, mass transfer, low roofs and uncovered platforms. Central del Norte — bus terminal, platforms and slab next to the northern industrial belt.",
        "fr": "Dans les encadrés : CETRAM Indios Verdes — porte nord du métro, correspondance de masse, toits bas et quais découverts. Central del Norte — gare routière, quais et dalle contre la ceinture industrielle du nord.",
    },
    "benito_juarez": {
        "es": "En el recuadro: WTC / Nápoles — viaducto, azoteas y estacionamientos en una alcaldía 100 % urbana; casi no hay media > 43 °C, pero el máximo de azotea sí cruza el umbral en la mayor parte del suelo.",
        "en": "In the box: WTC / Nápoles — beltway, roofs and parking in a fully urban borough; the composite mean almost never exceeds 43 °C, but roof-top maxima cross the threshold on most of the land.",
        "fr": "Dans l’encadré : WTC / Nápoles — viaduc, toits et parkings dans une délégation 100 % urbaine ; la moyenne dépasse à peine 43 °C, mais les max de toiture franchissent le seuil sur la plus grande part du sol.",
    },
    "coyoacan": {
        "es": "En el recuadro: CETRAM Taxqueña — puerta sur de metro, tren ligero y autobuses sobre losa; el contraste con Ciudad Universitaria y el Pedregal, más verdes, es el de la alcaldía.",
        "en": "In the box: CETRAM Taxqueña — southern metro, light-rail and bus gate on a slab; the contrast with greener Ciudad Universitaria and the Pedregal is the borough’s story.",
        "fr": "Dans l’encadré : CETRAM Taxqueña — porte sud métro, métro léger et bus sur dalle ; le contraste avec Ciudad Universitaria et le Pedregal, plus verts, est celui de la délégation.",
    },
    "milpa_alta": {
        "es": "En el recuadro: Villa Milpa Alta, la cabecera; el 17 % urbano del polígono sigue caliente (70 % del máximo > 43 °C) sobre asfalto de poblado, no sobre el bosque de la ladera.",
        "en": "In the box: Villa Milpa Alta, the town seat; the polygon’s 17 % urban share is still hot (70 % of pixel-max > 43 °C) on village asphalt, not on the hillside forest.",
        "fr": "Dans l’encadré : Villa Milpa Alta, le chef-lieu ; les 17 % urbains du polygone restent chauds (70 % du max-pixel > 43 °C) sur l’asphalte du bourg, pas sur la forêt du versant.",
    },
    "miguel_hidalgo": {
        "es": "En el recuadro: Tacubaya — nudo de metro y camión en el borde sur, losa y avenidas; Chapultepec, al norte del recuadro, es el contraste verde que la alcaldía sí tiene y el oriente no.",
        "en": "In the box: Tacubaya — metro and bus node on the southern edge, slab and avenues; Chapultepec, north of the box, is the green contrast this borough has and the east does not.",
        "fr": "Dans l’encadré : Tacubaya — nœud métro/bus au bord sud, dalle et avenues ; Chapultepec, au nord de l’encadré, est le contraste vert que cette délégation a et l’est n’a pas.",
    },
    "alvaro_obregon": {
        "es": "En el recuadro: CETRAM Observatorio — terminal poniente y cabecera de la línea 1, andenes y periférico de asfalto; las barrancas verdes bajan el IVC de la alcaldía pero no la losa del transbordo.",
        "en": "In the box: CETRAM Observatorio — western terminal and Line 1 head, platforms and asphalt beltway; green ravines lower the borough IVC but not the transfer slab.",
        "fr": "Dans l’encadré : CETRAM Observatorio — terminus ouest et tête de la ligne 1, quais et périphérique d’asphalte ; les ravins verts baissent l’IVC de la délégation, pas la dalle de correspondance.",
    },
    "xochimilco": {
        "es": "En el recuadro: embarcaderos del centro — muelle, avenida y techos; las chinampas y el agua agrícola bajan el IVC de la alcaldía, pero el andén de concreto sigue caliente.",
        "en": "In the box: downtown piers — dock, avenue and roofs; chinampas and agricultural water lower the borough IVC, but the concrete dock stays hot.",
        "fr": "Dans l’encadré : embarcadères du centre — quai, avenue et toits ; les chinampas et l’eau agricole baissent l’IVC, mais le quai de béton reste chaud.",
    },
    "la_magdalena_contreras": {
        "es": "En el recuadro: centro de Contreras, la franja urbana pegada a la sierra; asfalto de poblado y techos, mientras el bosque del sur-poniente —referencia rural de toda la ciudad— queda fuera del recuadro.",
        "en": "In the box: downtown Contreras, the urban strip against the sierra; village asphalt and roofs, while the south-west forest — rural reference for the whole city — sits outside the box.",
        "fr": "Dans l’encadré : centre de Contreras, bande urbaine contre la sierra ; asphalte du bourg et toits, tandis que la forêt sud-ouest — référence rurale de toute la ville — reste hors cadre.",
    },
    "tlalpan": {
        "es": "En el recuadro: corredor de hospitales e institutos — losa médica y periférico frente al Ajusco; el bosque que fija T rural 25.6 °C está al sur del recuadro, no en la plataforma hospitalaria.",
        "en": "In the box: hospital and institute corridor — medical slab and beltway facing the Ajusco; the forest that sets T rural 25.6 °C sits south of the box, not on the hospital platform.",
        "fr": "Dans l’encadré : couloir d’hôpitaux et d’instituts — dalle médicale et périphérique face à l’Ajusco ; la forêt qui fixe T rural 25,6 °C est au sud de l’encadré, pas sur la plateforme hospitalière.",
    },
    "cuajimalpa_de_morelos": {
        "es": "En el recuadro: Santa Fe — torres, estacionamientos y losa en la alcaldía más fresca; isla local de concreto sobre el bosque de agua, que sí cubre el resto del polígono.",
        "en": "In the box: Santa Fe — towers, parking and slab in the coolest borough; a local concrete island over the water forest that still covers the rest of the polygon.",
        "fr": "Dans l’encadré : Santa Fe — tours, parkings et dalle dans la délégation la plus fraîche ; îlot local de béton sur la forêt d’eau, qui couvre encore le reste du polygone.",
    },
}


def alcaldia_note(lang: str, slug: str) -> str:
    pack = NOTES.get(slug) or {}
    return pack.get(lang) or pack.get("es") or ""


def alcaldia_zones(lang: str, slug: str) -> str:
    pack = ZONES.get(slug) or {}
    return pack.get(lang) or pack.get("es") or ""
