"""Tropicalized unit notes and ranking copy for Ahmedabad and Phoenix (ES / EN / FR)."""

from __future__ import annotations

NOTES = {
    "ahmedabad": {
        "sabarmati": {
            "es": "Taluka urbana del río y el casco (IVC 63). Casi todo el máximo y el 89 % de la media urbana superan 43 °C. El Sabarmati no enfría la losa: techos densos, andenes y poco verdor (NDVI 0.22). El SUHI es negativo porque el rural del distrito ya está a ~48 °C.",
            "en": "Urban river-and-old-city taluka (IVC 63). Almost all of pixel-max and 89 % of the urban mean exceed 43 °C. The Sabarmati does not cool the slab: dense roofs, platforms and little green (NDVI 0.22). SUHI is negative because district rural land is already ~48 °C.",
            "fr": "Taluka urbaine du fleuve et de la vieille ville (IVC 63). Presque tout le max-pixel et 89 % de la moyenne urbaine dépassent 43 °C. Le Sabarmati ne refroidit pas la dalle : toits denses, quais et peu de verdure (NDVI 0,22). Le SUHI est négatif car le rural du district est déjà à ~48 °C.",
        },
        "viramgam": {
            "es": "Poblado sobre llanura caliente (IVC 62). El 100 % del máximo urbano y el 94 % de la media cruzan 43 °C. Poco suelo GHSL urbano (6 %), pero ese suelo es asfalto de cabecera y techo de lámina en un periurbano que ya es carga de calor de fondo.",
            "en": "Town on a hot plain (IVC 62). 100 % of urban pixel-max and 94 % of the mean cross 43 °C. Little GHSL urban land (6 %), but that land is seat-town asphalt and metal roofs on a peri-urban fabric that is already a background heat load.",
            "fr": "Bourg sur plaine chaude (IVC 62). 100 % du max-pixel urbain et 94 % de la moyenne franchissent 43 °C. Peu de sol urbain GHSL (6 %), mais ce sol est asphalte de chef-lieu et tôle dans un périurbain déjà chargé en chaleur de fond.",
        },
        "detroj_rampura": {
            "es": "Periurbano agrícola (IVC 61). La fracción de media > 43 °C es la más alta del distrito (96 %). Lotes, suelo desnudo y cubiertas; el NDVI 0.33 es el más verde de las talukas, y aun así el compuesto no baja de 43 °C.",
            "en": "Agricultural peri-urban belt (IVC 61). The share of mean > 43 °C is the district’s highest (96 %). Lots, bare soil and roofs; NDVI 0.33 is the greenest of the talukas, and the composite still does not fall below 43 °C.",
            "fr": "Ceinture périurbaine agricole (IVC 61). La part de moyenne > 43 °C est la plus haute du district (96 %). Lots, sol nu et toits ; le NDVI 0,33 est le plus vert des talukas, et le composite ne descend toujours pas sous 43 °C.",
        },
        "sanand": {
            "es": "Corredor industrial (IVC 60). Naves del GIDC, plantas automotrices y patios de carga. El 100 % del máximo urbano > 43 °C; el SUHI sigue negativo: las naves están tan calientes como el periurbano, no más.",
            "en": "Industrial corridor (IVC 60). GIDC sheds, auto plants and yards. 100 % of urban pixel-max > 43 °C; SUHI stays negative: the sheds are as hot as the peri-urban plain, not hotter.",
            "fr": "Couloir industriel (IVC 60). Hangars du GIDC, usines auto et cours. 100 % du max-pixel urbain > 43 °C ; le SUHI reste négatif : les hangars sont aussi chauds que la plaine périurbaine, pas plus.",
        },
        "daskroi": {
            "es": "Anillo este de la ciudad (IVC 60). Bodegas, carretera y urbanización abierta. El 100 % del máximo y el 88 % de la media urbana > 43 °C, con verdor 0.29 que no corta la losa del anillo.",
            "en": "Eastern ring of the city (IVC 60). Warehouses, highway and open housing. 100 % of pixel-max and 88 % of the urban mean > 43 °C, with greenness 0.29 that does not cut the ring-road slab.",
            "fr": "Anneau est de la ville (IVC 60). Entrepôts, route et lotissements. 100 % du max-pixel et 88 % de la moyenne urbaine > 43 °C, verdure 0,29 qui ne coupe pas la dalle de l’anneau.",
        },
        "bavla": {
            "es": "Eje sur de naves y carretera (IVC 60). El 100 % del máximo urbano > 43 °C y el 89 % de la media. Asfalto de tráiler y techos industriales; el periurbano no ofrece una referencia fresca.",
            "en": "Southern axis of sheds and highway (IVC 60). 100 % of urban pixel-max > 43 °C and 89 % of the mean. Trailer asphalt and industrial roofs; the peri-urban belt offers no cool reference.",
            "fr": "Axe sud de hangars et de route (IVC 60). 100 % du max-pixel urbain > 43 °C et 89 % de la moyenne. Asphalte de poids lourds et toits industriels ; le périurbain n’offre pas de référence fraîche.",
        },
        "dholka": {
            "es": "La taluka menos extrema (IVC 58) y aun así en el top 25 mundial. Un poco más de verdor (NDVI 0.32) y 85 % de media > 43 °C. El piso del distrito ya es alto: aquí no hay un ‘fresco’, hay menos losa.",
            "en": "The least extreme taluka (IVC 58) and still in the global top 25. A little more green (NDVI 0.32) and 85 % of the mean > 43 °C. The district floor is already high: this is not ‘cool’, it is less slab.",
            "fr": "La taluka la moins extrême (IVC 58), encore dans le top 25 mondial. Un peu plus de verdure (NDVI 0,32) et 85 % de moyenne > 43 °C. Le plancher du district est déjà haut : ce n’est pas « frais », c’est moins de dalle.",
        },
    },
    "phoenix": {
        "maryvale": {
            "es": "El urban village más vulnerable (IVC 71). Arterias, estacionamientos y azoteas bajas al poniente; NDVI 0.14, el 75 % de la media urbana > 43 °C. Es losa sobre desierto, no un diferencial tipo CDMX.",
            "en": "The most vulnerable urban village (IVC 71). Arterials, parking and low roofs on the west side; NDVI 0.14, 75 % of the urban mean > 43 °C. Slab on desert, not a CDMX-style differential.",
            "fr": "Le village urbain le plus vulnérable (IVC 71). Artères, parkings et toits bas à l’ouest ; NDVI 0,14, 75 % de la moyenne urbaine > 43 °C. Dalle sur désert, pas un différentiel type Mexico.",
        },
        "central_city": {
            "es": "Núcleo y bodegas (IVC 71). El NDVI urbano más bajo de Phoenix (0.11): estacionamientos, viaductos y el borde del aeropuerto Sky Harbor. El 100 % del máximo y el 73 % de la media > 43 °C.",
            "en": "Core and warehouses (IVC 71). Phoenix’s lowest urban NDVI (0.11): parking, overpasses and the Sky Harbor airport edge. 100 % of pixel-max and 73 % of the mean > 43 °C.",
            "fr": "Noyau et entrepôts (IVC 71). NDVI urbain le plus bas de Phoenix (0,11) : parkings, viaducs et lisière de l’aéroport Sky Harbor. 100 % du max-pixel et 73 % de la moyenne > 43 °C.",
        },
        "estrella": {
            "es": "Expansión suroeste (IVC 65). Urbanización nueva sobre desierto: asfalto fresco, techos y poco árbol (NDVI 0.15). El 62 % de la media urbana ya cruza 43 °C.",
            "en": "Southwest expansion (IVC 65). New housing on desert: fresh asphalt, roofs and few trees (NDVI 0.15). 62 % of the urban mean already crosses 43 °C.",
            "fr": "Expansion sud-ouest (IVC 65). Lotissements neufs sur désert : asphalte frais, toits et peu d’arbres (NDVI 0,15). 62 % de la moyenne urbaine franchit déjà 43 °C.",
        },
        "south_mountain": {
            "es": "Reserva frente a ladera pavimentada (IVC 62). South Mountain Preserve no entra al índice urbano; el GHSL ≥ 21 está en las faldas asfaltadas, con 56 % de media > 43 °C.",
            "en": "Preserve versus paved foothills (IVC 62). South Mountain Preserve is not in the urban index; GHSL ≥ 21 sits on the asphalted slopes, with 56 % of the mean > 43 °C.",
            "fr": "Réserve face aux piémonts pavés (IVC 62). South Mountain Preserve n’entre pas dans l’indice urbain ; le GHSL ≥ 21 est sur les pentes asphaltées, 56 % de moyenne > 43 °C.",
        },
        "ahwatukee_foothills": {
            "es": "Fraccionamiento planificado (IVC 62). Techos de teja, arterias y lotes desérticos; el 99 % del máximo > 43 °C y la media aún al 52 %.",
            "en": "Master-planned foothills (IVC 62). Tile roofs, arterials and desert lots; 99 % of pixel-max > 43 °C and the mean still at 52 %.",
            "fr": "Lotissement planifié (IVC 62). Toits de tuiles, artères et lots désertiques ; 99 % du max-pixel > 43 °C et la moyenne encore à 52 %.",
        },
        "alhambra": {
            "es": "Corredor I-17 (IVC 61). Placas comerciales, asfalto y 60 % de media urbana > 43 °C. Un poco más de verdor que Maryvale (NDVI 0.20), no suficiente para bajar el máximo.",
            "en": "I-17 corridor (IVC 61). Commercial pads, asphalt and 60 % of the urban mean > 43 °C. A little more green than Maryvale (NDVI 0.20), not enough to cut the peak.",
            "fr": "Couloir I-17 (IVC 61). Dalles commerciales, asphalte et 60 % de moyenne urbaine > 43 °C. Un peu plus de verdure que Maryvale (NDVI 0,20), pas assez pour baisser le max.",
        },
        "encanto": {
            "es": "Trama antigua (IVC 57). Más árbol que el poniente; el 46 % de la media > 43 °C. El máximo sigue en el 96 %: pico de azotea en un barrio con algo de dosel.",
            "en": "Older grid (IVC 57). More trees than the west side; 46 % of the mean > 43 °C. Pixel-max is still 96 %: roof peak in a neighbourhood with some canopy.",
            "fr": "Trame ancienne (IVC 57). Plus d’arbres que l’ouest ; 46 % de moyenne > 43 °C. Le max-pixel reste à 96 % : pic de toiture dans un quartier un peu canopé.",
        },
        "north_mountain": {
            "es": "Norte mixto (IVC 56). El 99 % del máximo > 43 °C, pero la media baja al 38 %: menos carga continua que Maryvale, misma losa de mediodía.",
            "en": "Mixed north (IVC 56). 99 % of pixel-max > 43 °C, but the mean drops to 38 %: less all-day load than Maryvale, the same midday slab.",
            "fr": "Nord mixte (IVC 56). 99 % du max-pixel > 43 °C, mais la moyenne tombe à 38 % : moins de charge continue que Maryvale, même dalle de midi.",
        },
        "laveen": {
            "es": "Conversión agrícola (IVC 51). Campos que pasan a calle y techo; el 30 % de la media urbana > 43 °C. El índice pesa el GHSL nuevo, no el resto de parcela.",
            "en": "Agricultural conversion (IVC 51). Fields turning into street and roof; 30 % of the urban mean > 43 °C. The index weights new GHSL land, not the remaining plot.",
            "fr": "Conversion agricole (IVC 51). Champs qui deviennent rue et toit ; 30 % de moyenne urbaine > 43 °C. L’indice pèse le nouveau GHSL, pas la parcelle restante.",
        },
        "deer_valley": {
            "es": "Norte de expansión (IVC 50). Casi todo el máximo > 43 °C; la media solo el 20 %. Pico de techo en un urban village más abierto, junto al aeropuerto norte.",
            "en": "Northern expansion (IVC 50). Almost all of pixel-max > 43 °C; the mean only 20 %. Roof peak in a more open urban village, by the northern airport.",
            "fr": "Expansion nord (IVC 50). Presque tout le max-pixel > 43 °C ; la moyenne seulement 20 %. Pic de toiture dans un village plus ouvert, près de l’aéroport nord.",
        },
        "rio_vista": {
            "es": "Canal y desierto (IVC 47). SUHI negativo: el rural del polígono ya calienta. El 12 % de media > 43 °C; el máximo sigue saturado.",
            "en": "Canal and desert (IVC 47). Negative SUHI: rural land in the polygon already heats. 12 % of the mean > 43 °C; pixel-max still saturates.",
            "fr": "Canal et désert (IVC 47). SUHI négatif : le rural du polygone chauffe déjà. 12 % de moyenne > 43 °C ; le max-pixel sature encore.",
        },
        "north_gateway": {
            "es": "Desierto planeado del norte (IVC 47). SUHI −1.4 °C; 12 % de media > 43 °C. Es el contraste de Phoenix: menos losa continua, mismo techo al sol de abril.",
            "en": "Planned northern desert (IVC 47). SUHI −1.4 °C; 12 % of the mean > 43 °C. Phoenix’s contrast: less continuous slab, the same April roof in the sun.",
            "fr": "Désert planifié du nord (IVC 47). SUHI −1,4 °C ; 12 % de moyenne > 43 °C. Le contraste de Phoenix : moins de dalle continue, même toit d’avril au soleil.",
        },
        "paradise_valley": {
            "es": "Lotes más grandes (IVC 46). Un poco más de dosel; 10 % de media > 43 °C. El máximo (98 %) muestra que la teja sigue cruzando el umbral.",
            "en": "Larger lots (IVC 46). A little more canopy; 10 % of the mean > 43 °C. Pixel-max (98 %) shows tile roofs still crossing the threshold.",
            "fr": "Lots plus grands (IVC 46). Un peu plus de canopée ; 10 % de moyenne > 43 °C. Le max-pixel (98 %) montre que la tuile franchit encore le seuil.",
        },
        "camelback_east": {
            "es": "Camelback y avenidas (IVC 45). NDVI 0.22, el más alto del núcleo este; 16 % de media > 43 °C. Resorts y arteria: sombra fragmentada sobre asfalto.",
            "en": "Camelback and avenues (IVC 45). NDVI 0.22, the highest in the eastern core; 16 % of the mean > 43 °C. Resorts and arterial: fragmented shade on asphalt.",
            "fr": "Camelback et avenues (IVC 45). NDVI 0,22, le plus haut du noyau est ; 16 % de moyenne > 43 °C. Resorts et artère : ombre fragmentée sur asphalte.",
        },
        "desert_view": {
            "es": "El menos vulnerable (IVC 44). Norte de conservación y baja densidad; solo el 7 % de la media urbana > 43 °C. El máximo sigue en 98 %: el desierto no perdona el techo, sí la media.",
            "en": "The least vulnerable (IVC 44). Northern conservation land and low density; only 7 % of the urban mean > 43 °C. Pixel-max is still 98 %: desert does not forgive the roof, it does forgive the mean.",
            "fr": "Le moins vulnérable (IVC 44). Conservation nord et faible densité ; seulement 7 % de moyenne urbaine > 43 °C. Le max-pixel reste à 98 % : le désert ne pardonne pas le toit, il pardonne la moyenne.",
        },
    },
}

ZONES = {
    "ahmedabad": {
        "sabarmati": {
            "es": "En la taluka: casco viejo, riverfront del Sabarmati y techos corridos; el agua del río no compensa concreto ni lámina. La falta de dosel y el asfalto de andén inciden en que el 89 % de la media urbana supere 43 °C.",
            "en": "In the taluka: old city, Sabarmati riverfront and continuous roofs; river water does not offset concrete or metal. Lack of canopy and platform asphalt drive 89 % of the urban mean above 43 °C.",
            "fr": "Dans la taluka : vieille ville, riverfront du Sabarmati et toits continus ; l’eau du fleuve ne compense ni le béton ni la tôle. Le manque de canopée et l’asphalte des quais font que 89 % de la moyenne urbaine dépasse 43 °C.",
        },
        "viramgam": {
            "es": "En la cabecera: asfalto de poblado y techos de lámina sobre una llanura que en abril–mayo ya supera 43 °C fuera de la ciudad. El ‘urbano’ es una isla de pavimento en un mar caliente, no un contraste fresco.",
            "en": "In the town seat: village asphalt and metal roofs on a plain that already exceeds 43 °C in April–May outside the city. The ‘urban’ bit is a pavement island in a hot sea, not a cool contrast.",
            "fr": "Au chef-lieu : asphalte de bourg et toits de tôle sur une plaine qui dépasse déjà 43 °C en avril–mai hors ville. L’« urbain » est un îlot de revêtement dans une mer chaude, pas un contraste frais.",
        },
        "detroj_rampura": {
            "es": "En el poblado: lotes, suelo desnudo y cubiertas; la vegetación agrícola no entra al índice urbano. Por eso la media > 43 °C llega al 96 % pese a un NDVI algo más alto.",
            "en": "In the settlement: lots, bare soil and roofs; agricultural vegetation does not enter the urban index. That is why mean > 43 °C reaches 96 % despite a slightly higher NDVI.",
            "fr": "Dans le bourg : lots, sol nu et toits ; la végétation agricole n’entre pas dans l’indice urbain. D’où 96 % de moyenne > 43 °C malgré un NDVI un peu plus haut.",
        },
        "sanand": {
            "es": "En el corredor GIDC: naves, patios de maniobra y plantas automotrices. Concreto de cubierta y asfalto de carga; el periurbano no es más fresco que la nave.",
            "en": "On the GIDC corridor: sheds, yards and auto plants. Roof concrete and loading asphalt; the peri-urban belt is no cooler than the shed.",
            "fr": "Sur le couloir GIDC : hangars, cours et usines auto. Béton de toiture et asphalte de quai ; le périurbain n’est pas plus frais que le hangar.",
        },
        "daskroi": {
            "es": "En el anillo este: bodegas, carretera y fraccionamientos abiertos. La losa del periurbano de Ahmedabad es el patrón: techo, patio y poco árbol.",
            "en": "On the eastern ring: warehouses, highway and open tracts. Ahmedabad’s peri-urban slab is the pattern: roof, yard and few trees.",
            "fr": "Sur l’anneau est : entrepôts, route et lotissements ouverts. La dalle périurbaine d’Ahmedabad est le motif : toit, cour et peu d’arbres.",
        },
        "bavla": {
            "es": "En el eje sur: naves, tráileres y carretera. El asfalto de paso de carga y las cubiertas industriales mantienen la media urbana cerca del 89 % sobre 43 °C.",
            "en": "On the southern axis: sheds, trailers and highway. Freight asphalt and industrial roofs keep the urban mean near 89 % above 43 °C.",
            "fr": "Sur l’axe sud : hangars, remorques et route. L’asphalte de fret et les toits industriels maintiennent la moyenne urbaine près de 89 % au-dessus de 43 °C.",
        },
        "dholka": {
            "es": "En la cabecera de Dholka: un poco más de verdor y aún 85 % de media > 43 °C. Es el ‘fresco’ relativo del distrito: menos nave, no un oasis.",
            "en": "In Dholka town: a little more green and still 85 % of the mean > 43 °C. The district’s relative ‘cool’: fewer sheds, not an oasis.",
            "fr": "Au chef-lieu de Dholka : un peu plus de verdure et encore 85 % de moyenne > 43 °C. Le « frais » relatif du district : moins de hangars, pas un oasis.",
        },
    },
    "phoenix": {
        "maryvale": {
            "es": "En el recuadro oeste: arterias de seis carriles, estacionamientos de plaza y azoteas bajas. Casi no hay dosel; el asfalto y el concreto de losa explican el 75 % de media > 43 °C.",
            "en": "On the west side: six-lane arterials, strip-mall parking and low roofs. Almost no canopy; asphalt and slab concrete explain 75 % of the mean > 43 °C.",
            "fr": "À l’ouest : artères à six voies, parkings de strip-mall et toits bas. Presque pas de canopée ; asphalte et dalle expliquent 75 % de moyenne > 43 °C.",
        },
        "central_city": {
            "es": "En el núcleo: centro, bodegas y el borde del Sky Harbor. Pistas, plataformas y estacionamientos sustituyen vegetación; el NDVI 0.11 es el piso de la ciudad.",
            "en": "In the core: downtown, warehouses and the Sky Harbor edge. Runways, aprons and parking replace vegetation; NDVI 0.11 is the city’s floor.",
            "fr": "Dans le noyau : centre, entrepôts et lisière de Sky Harbor. Pistes, aires et parkings remplacent la végétation ; le NDVI 0,11 est le plancher de la ville.",
        },
        "estrella": {
            "es": "En la expansión suroeste: calles nuevas, techos y desierto rasurado. El asfalto fresco sobre suelo desnudo empuja la media al 62 % sobre 43 °C.",
            "en": "In the southwest expansion: new streets, roofs and scraped desert. Fresh asphalt on bare soil pushes the mean to 62 % above 43 °C.",
            "fr": "Dans l’expansion sud-ouest : rues neuves, toits et désert raclé. L’asphalte frais sur sol nu pousse la moyenne à 62 % au-dessus de 43 °C.",
        },
        "south_mountain": {
            "es": "En las faldas: la reserva es verde; el índice mira el GHSL de ladera —casas, arteria y estacionamiento— no el monte.",
            "en": "On the foothills: the preserve is green; the index looks at hillside GHSL — houses, arterial and parking — not the mountain.",
            "fr": "Sur les piémonts : la réserve est verte ; l’indice regarde le GHSL de versant — maisons, artère et parking — pas la montagne.",
        },
        "ahwatukee_foothills": {
            "es": "En el fraccionamiento: teja, arteria y lote desértico. Poca sombra de calle; el máximo de azotea cruza 43 °C en el 99 % del suelo urbano.",
            "en": "In the subdivision: tile, arterial and desert lot. Little street shade; roof-top maxima cross 43 °C on 99 % of urban land.",
            "fr": "Dans le lotissement : tuile, artère et lot désertique. Peu d’ombre de rue ; les max de toiture franchissent 43 °C sur 99 % du sol urbain.",
        },
        "alhambra": {
            "es": "Sobre el I-17: placas comerciales, gasolineras y asfalto de acceso. Un dosel fragmentado no corta la media del 60 % sobre 43 °C.",
            "en": "Along I-17: commercial pads, stations and access asphalt. Fragmented canopy does not cut the 60 % mean above 43 °C.",
            "fr": "Le long de l’I-17 : dalles commerciales, stations et asphalte d’accès. Une canopée fragmentée ne coupe pas les 60 % de moyenne au-dessus de 43 °C.",
        },
        "encanto": {
            "es": "En la trama antigua: más árbol que Maryvale, aún 96 % de máximo > 43 °C. El dosel baja la media, no el pico de techo.",
            "en": "On the older grid: more trees than Maryvale, still 96 % of pixel-max > 43 °C. Canopy lowers the mean, not the roof peak.",
            "fr": "Sur la trame ancienne : plus d’arbres que Maryvale, encore 96 % de max-pixel > 43 °C. La canopée baisse la moyenne, pas le pic de toiture.",
        },
        "north_mountain": {
            "es": "En el norte mixto: arteria y techo; la media (38 %) ya no es la carga continua de Maryvale, el máximo sí satura.",
            "en": "In the mixed north: arterial and roof; the mean (38 %) is no longer Maryvale’s all-day load, the maximum still saturates.",
            "fr": "Dans le nord mixte : artère et toit ; la moyenne (38 %) n’est plus la charge continue de Maryvale, le maximum sature encore.",
        },
        "laveen": {
            "es": "En la conversión: parcela agrícola junto a calle nueva. El índice toma el asfalto reciente, no el resto de campo.",
            "en": "On the conversion: agricultural plot next to a new street. The index takes the recent asphalt, not the remaining field.",
            "fr": "Sur la conversion : parcelle agricole contre rue neuve. L’indice prend l’asphalte récent, pas le champ restant.",
        },
        "deer_valley": {
            "es": "En el norte: aeropuerto y expansión. Mucho máximo de techo, poca media continua: el suelo aún no es una losa de mediodía.",
            "en": "In the north: airport and expansion. Much roof-top max, little continuous mean: the land is not yet an all-day slab.",
            "fr": "Au nord : aéroport et expansion. Beaucoup de max de toiture, peu de moyenne continue : le sol n’est pas encore une dalle de midi.",
        },
        "rio_vista": {
            "es": "Junto al canal: agua agrícola y techo. El rural del polígono calienta; el SUHI negativo dice que la referencia no es fresca.",
            "en": "By the canal: agricultural water and roof. Rural land in the polygon heats; negative SUHI says the reference is not cool.",
            "fr": "Près du canal : eau agricole et toit. Le rural du polygone chauffe ; le SUHI négatif dit que la référence n’est pas fraîche.",
        },
        "north_gateway": {
            "es": "En el desierto planeado: baja densidad, menos losa. El 12 % de media > 43 °C es el contraste con Maryvale, no un bosque.",
            "en": "On the planned desert: low density, less slab. 12 % of the mean > 43 °C is the contrast with Maryvale, not a forest.",
            "fr": "Sur le désert planifié : faible densité, moins de dalle. 12 % de moyenne > 43 °C est le contraste avec Maryvale, pas une forêt.",
        },
        "paradise_valley": {
            "es": "En lotes amplios: más jardín relativo; el techo sigue cruzando 43 °C. La media (10 %) baja porque hay menos asfalto continuo.",
            "en": "On large lots: relatively more garden; the roof still crosses 43 °C. The mean (10 %) drops because there is less continuous asphalt.",
            "fr": "Sur grands lots : relativement plus de jardin ; le toit franchit encore 43 °C. La moyenne (10 %) baisse faute d’asphalte continu.",
        },
        "camelback_east": {
            "es": "Bajo Camelback: resorts, avenida y un dosel irregular. El verdor 0.22 es el más alto del este; el asfalto de corredor sigue caliente.",
            "en": "Under Camelback: resorts, avenue and uneven canopy. Greenness 0.22 is the eastern high; the corridor asphalt stays hot.",
            "fr": "Sous Camelback : resorts, avenue et canopée irrégulière. La verdure 0,22 est le haut de l’est ; l’asphalte du couloir reste chaud.",
        },
        "desert_view": {
            "es": "En el norte de conservación: poca densidad y 7 % de media > 43 °C. El techo de abril sigue rojo en el máximo; la media ya no.",
            "en": "On northern conservation land: low density and 7 % of the mean > 43 °C. The April roof still runs red at pixel-max; the mean no longer does.",
            "fr": "Sur la conservation nord : faible densité et 7 % de moyenne > 43 °C. Le toit d’avril reste rouge au max-pixel ; plus à la moyenne.",
        },
    },
}


def unit_note(lang: str, city: str, slug: str) -> str:
    pack = (NOTES.get(city) or {}).get(slug) or {}
    return pack.get(lang) or pack.get("es") or ""


def unit_zones(lang: str, city: str, slug: str) -> str:
    pack = (ZONES.get(city) or {}).get(slug) or {}
    return pack.get(lang) or pack.get("es") or ""


def local_note(lang: str, city: str, slug: str) -> str:
    if city == "cdmx":
        from cdmx_alcaldia_copy import alcaldia_note
        return alcaldia_note(lang, slug)
    return unit_note(lang, city, slug)


def local_zones(lang: str, city: str, slug: str) -> str:
    if city == "cdmx":
        from cdmx_alcaldia_copy import alcaldia_zones
        return alcaldia_zones(lang, slug)
    return unit_zones(lang, city, slug)


def tropical_rank(lang: str, slug: str, ctx: dict) -> dict | None:
    """City-specific rank / soil / subdivision paragraphs. None = use generic copy."""
    if slug == "ahmedabad":
        return _ahmedabad(lang, ctx)
    if slug == "phoenix":
        return _phoenix(lang, ctx)
    return None


def _ahmedabad(lang: str, ctx: dict) -> dict:
    name, n_cities, ivc = ctx["name"], ctx["n_cities"], ctx["ivc"]
    suhi, t_rural = ctx["suhi"], ctx["t_rural"]
    nxt_name, nxt_ivc = ctx["nxt_name"], ctx["nxt_ivc"]
    hottest, coolest = ctx["hottest"], ctx["coolest"]
    n_units_all, n_top, top25_txt = ctx["n_units_all"], ctx["n_top"], ctx["top25_txt"]
    ulabels, n_units = ctx["ulabels"], ctx["n_units"]
    frac_max = ctx["frac_max"]
    frac_mean = ctx["frac_mean"]
    if lang == "en":
        return dict(
            rank_city=(
                f"{name} ranks 1 of {n_cities} cities measured in April and May 2026, with a "
                f"Climate Vulnerability Index (IVC) of {ivc:.1f} out of 100. It leads because "
                f"almost all of the urban fabric exceeds 43 °C at pixel-max ({100 * frac_max:.0f} %) "
                f"and at the composite mean ({100 * frac_mean:.0f} %). The rural reference is itself "
                f"about {t_rural:.0f} °C, so SUHI is {suhi:+.1f} °C and adds nothing: this is "
                f"background heat, not a classic city-versus-countryside island. "
                f"{nxt_name} ({nxt_ivc:.1f}) comes next."
            ),
            rank_alc=(
                f"Inside the district the {n_units} {ulabels} sit in a narrow band "
                f"({coolest.ivc:.0f}–{hottest.ivc:.0f}). {hottest.unit} leads (IVC {hottest.ivc:.0f}): "
                f"old city, riverfront and dense roofs along the Sabarmati. Viramgam, Detroj-Rampura, "
                f"Sanand, Daskroi and Bavla follow within three points: peri-urban seats, GIDC sheds "
                f"and highway asphalt. {coolest.unit} ranks last ({coolest.ivc:.0f}) with a little more green, "
                f"not a cool refuge."
            ),
            rank_why=(
                f"The ranking is almost flat because climate sets the floor: GHSL rural land already "
                f"reaches ~{t_rural:.0f} °C, so z_SUHI is zero across most talukas. What remains is "
                f"z_LST max, z_LST mean and a moderate greenness deficit. Shade, cool roofs and trees "
                f"still matter for people; they barely move a city index when the surroundings are "
                f"already above 43 °C.\n\n"
                f"Mexico City, third in the city ranking, is the opposite pattern: a strong heat island "
                f"over a cool rural reference. Ahmedabad is the pre-monsoon load of Gujarat, with a "
                f"pioneering heat-action plan that this index does not score."
            ),
            rank_soil=(
                "Land cover in the five highest-IVC talukas is metal roofs, industrial sheds, highway "
                "asphalt and little tree canopy. Sabarmati is continuous urban roof along the river. "
                "Viramgam and Detroj-Rampura are town seats on a hot plain: pavement of the taluka "
                "head, bare lots, agricultural green that does not enter the urban mask. Sanand adds "
                "GIDC sheds, auto plants and loading yards. Daskroi is the eastern warehouse-and-ring "
                "belt. The Sabarmati river and peri-urban fields do not offset the slab the index sees."
            ),
            subdiv_h="3. Highest-IVC subdivisions",
            subdiv_p=(
                f"Among {n_units_all} political subdivisions of the 18 cities in the comparable index, "
                f"all {n_top} Ahmedabad talukas enter the top 25: {top25_txt}. "
                "The city is first because the whole district is a high floor, not because one "
                "neighbourhood saturates SUHI. The components chart shows z_LST max and z_LST mean "
                "near 1.0 and z_SUHI at zero: a hot plain, not an urban island."
            ),
        )
    if lang == "fr":
        return dict(
            rank_city=(
                f"{name} occupe la 1re place sur {n_cities} villes mesurées en avril et mai 2026, avec un "
                f"indice de vulnérabilité climatique (IVC) de {ivc:.1f} sur 100. Elle arrive en tête "
                f"parce que presque tout le tissu urbain dépasse 43 °C au max-pixel ({100 * frac_max:.0f} %) "
                f"et à la moyenne du composite ({100 * frac_mean:.0f} %). La référence rurale est elle-même "
                f"d’environ {t_rural:.0f} °C, donc le SUHI est de {suhi:+.1f} °C et n’ajoute rien : c’est "
                f"une chaleur de fond, pas un îlot classique ville–campagne. "
                f"{nxt_name} ({nxt_ivc:.1f}) suit."
            ),
            rank_alc=(
                f"Dans le district, les {n_units} {ulabels} tiennent dans une bande étroite "
                f"({coolest.ivc:.0f}–{hottest.ivc:.0f}). {hottest.unit} arrive en tête (IVC {hottest.ivc:.0f}) : "
                f"vieille ville, riverfront et toits denses le long du Sabarmati. Viramgam, Detroj-Rampura, "
                f"Sanand, Daskroi et Bavla suivent à trois points : chefs-lieux périurbains, hangars GIDC "
                f"et asphalte de route. {coolest.unit} arrive dernière ({coolest.ivc:.0f}), un peu plus verte, "
                f"pas un refuge frais."
            ),
            rank_why=(
                f"Le classement est presque plat parce que le climat fixe le plancher : le rural GHSL "
                f"atteint déjà ~{t_rural:.0f} °C, donc z_SUHI est nul dans la plupart des talukas. Il reste "
                f"z_LST max., z_LST moyenne et un déficit de verdure modéré. L’ombre, les toits froids et "
                f"les arbres comptent encore pour les gens ; ils bougent à peine un indice de ville quand "
                f"l’environnement dépasse déjà 43 °C.\n\n"
                f"Mexico, troisième du classement des villes, est le schéma inverse : un îlot de chaleur "
                f"fort sur une référence rurale fraîche. Ahmedabad, c’est la charge de pré-mousson du "
                f"Gujarat, avec un plan d’action chaleur pionnier que cet indice ne note pas."
            ),
            rank_soil=(
                "La couverture du sol dans les cinq talukas au plus fort IVC, ce sont toits de tôle, "
                "hangars industriels, asphalte de route et peu de canopée. Sabarmati est un toit urbain "
                "continu le long du fleuve. Viramgam et Detroj-Rampura sont des chefs-lieux sur plaine "
                "chaude : revêtement du bourg, lots nus, verdure agricole hors masque urbain. Sanand "
                "ajoute hangars GIDC, usines auto et cours de chargement. Daskroi est la ceinture est "
                "d’entrepôts et d’anneau. Le Sabarmati et les champs périurbains ne compensent pas la "
                "dalle que voit l’indice."
            ),
            subdiv_h="3. Subdivisions à l’IVC le plus élevé",
            subdiv_p=(
                f"Parmi les {n_units_all} subdivisions politiques des 18 villes de l’indice comparable, "
                f"les {n_top} talukas d’Ahmedabad entrent dans le top 25 : {top25_txt}. "
                "La ville est première parce que tout le district est un plancher haut, pas parce qu’un "
                "quartier sature le SUHI. Le graphique des composantes montre z_LST max. et z_LST moyenne "
                "près de 1,0 et z_SUHI à zéro : une plaine chaude, pas un îlot urbain."
            ),
        )
    return dict(
        rank_city=(
            f"{name} ocupa el lugar 1 de {n_cities} ciudades medidas en abril y mayo de 2026, "
            f"con un Índice de Vulnerabilidad Climática (IVC) de {ivc:.1f} sobre 100. Encabeza "
            f"porque casi todo el tejido urbano supera 43 °C en el máximo por píxel ({100 * frac_max:.0f} %) "
            f"y en la media del compuesto ({100 * frac_mean:.0f} %). La referencia rural ya está a unos "
            f"{t_rural:.0f} °C, así que el SUHI es {suhi:+.1f} °C y no suma: es calor de fondo, no una "
            f"isla clásica ciudad–campo. {nxt_name} ({nxt_ivc:.1f}) queda a continuación."
        ),
        rank_alc=(
            f"Dentro del distrito, las {n_units} {ulabels} caben en una franja estrecha "
            f"({coolest.ivc:.0f}–{hottest.ivc:.0f}). {hottest.unit} encabeza (IVC {hottest.ivc:.0f}): "
            f"casco, riverfront y techos densos a lo largo del Sabarmati. Viramgam, Detroj-Rampura, "
            f"Sanand, Daskroi y Bavla siguen a tres puntos: cabeceras periurbanas, naves del GIDC "
            f"y asfalto de carretera. {coolest.unit} queda al final ({coolest.ivc:.0f}), con un poco más "
            f"de verdor, no un refugio fresco."
        ),
        rank_why=(
            f"El ranking es casi plano porque el clima fija el piso: el rural GHSL ya llega a "
            f"~{t_rural:.0f} °C, así que z_SUHI vale cero en casi todas las talukas. Quedan z_LST máx., "
            f"z_LST media y un déficit de verdor moderado. La sombra, los techos fríos y el arbolado "
            f"siguen importando para la gente; apenas mueven un índice de ciudad cuando el entorno "
            f"ya supera 43 °C.\n\n"
            f"La Ciudad de México, tercera en el ranking de ciudades, es el patrón inverso: una isla "
            f"de calor fuerte sobre una referencia rural fresca. Ahmedabad es la carga pre-monzón de "
            f"Guyarat, con un plan de acción térmica pionero que este índice no califica."
        ),
        rank_soil=(
            "El tipo de suelo en las cinco talukas de mayor IVC es techo de lámina, naves "
            "industriales, asfalto de carretera y poco dosel. Sabarmati es cubierta urbana continua "
            "junto al río. Viramgam y Detroj-Rampura son cabeceras en llanura caliente: pavimento "
            "del poblado, lotes desnudos, verdor agrícola que no entra a la máscara urbana. Sanand "
            "suma naves del GIDC, plantas automotrices y patios de carga. Daskroi es el anillo este "
            "de bodegas. El Sabarmati y los campos periurbanos no compensan la losa que ve el índice."
        ),
        subdiv_h="3. Subdivisiones con mayor IVC",
        subdiv_p=(
            f"Entre las {n_units_all} subdivisiones políticas de las 18 ciudades del índice "
            f"comparable, las {n_top} talukas de Ahmedabad entran al top 25: {top25_txt}. "
            "La ciudad es primera porque todo el distrito es un piso alto, no porque un barrio "
            "sature el SUHI. La gráfica de componentes muestra z_LST máx. y z_LST media cerca de "
            "1.0 y z_SUHI en cero: una llanura caliente, no una isla urbana."
        ),
    )


def _phoenix(lang: str, ctx: dict) -> dict:
    name, n_cities, ivc = ctx["name"], ctx["n_cities"], ctx["ivc"]
    suhi, t_rural = ctx["suhi"], ctx["t_rural"]
    nxt_name, nxt_ivc = ctx["nxt_name"], ctx["nxt_ivc"]
    hottest, coolest = ctx["hottest"], ctx["coolest"]
    n_units_all, n_top, top25_txt = ctx["n_units_all"], ctx["n_top"], ctx["top25_txt"]
    ulabels, n_units = ctx["ulabels"], ctx["n_units"]
    frac_max = ctx["frac_max"]
    frac_mean = ctx["frac_mean"]
    top = ctx["top_rows"]
    if lang == "en":
        return dict(
            rank_city=(
                f"{name} ranks 2 of {n_cities} cities measured in April and May 2026, with a "
                f"Climate Vulnerability Index (IVC) of {ivc:.1f} out of 100. Ahmedabad leads. "
                f"{nxt_name} ({nxt_ivc:.1f}) comes next. Almost all of the urban pixel-max exceeds "
                f"43 °C ({100 * frac_max:.0f} %); the composite mean does so on {100 * frac_mean:.0f} % "
                f"of urban land. Rural desert is already about {t_rural:.0f} °C, so urban SUHI is only "
                f"{suhi:+.1f} °C. What sets Phoenix apart is pavement and a greenness deficit on a hot "
                f"desert, not a CDMX-style island over a cool forest."
            ),
            rank_alc=(
                f"Inside the city the index concentrates in the west and the core. "
                f"{hottest.unit} leads (IVC {hottest.ivc:.0f}): arterials, parking and low roofs. "
                f"{top[1].unit} ({top[1].ivc:.0f}) adds downtown, warehouses and the Sky Harbor edge "
                f"(NDVI 0.11). {top[2].unit} ({top[2].ivc:.0f}) is new sprawl on scraped desert. "
                f"{top[3].unit} ({top[3].ivc:.0f}) mixes the preserve with paved foothills. "
                f"{top[4].unit} ({top[4].ivc:.0f}) is master-planned tile roofs. "
                f"{coolest.unit} ranks last ({coolest.ivc:.0f}), on the northern conservation fringe."
            ),
            rank_why=(
                f"West-side villages (Maryvale, Central City) combine slab, parking and almost no "
                f"canopy; mean LST still exceeds 43 °C on most of the urban mask. Northern villages "
                f"(Desert View, North Gateway, Paradise Valley) keep a high pixel-max — desert roofs "
                f"in April — but the mean falls because density and asphalt drop.\n\n"
                f"Unlike Mexico City, Phoenix cannot lean on a cool rural reference "
                f"(~{t_rural:.0f} °C). Unlike Ahmedabad, the mean is not already saturated at 89 %. "
                f"Design still moves the mean: shade, albedo and less parking separate Maryvale from "
                f"Desert View. {coolest.unit} shows the floor of the city ranking."
            ),
            rank_soil=(
                "Land cover in the five highest-IVC urban villages is asphalt, parking, low roofs "
                "and airport or arterial slab, with little green. Maryvale is strip-mall parking and "
                "six-lane roads. Central City adds downtown decks and the Sky Harbor runways and "
                "aprons. Estrella is fresh pavement on desert. South Mountain’s urban score sits on "
                "the asphalted foothills, not on the preserve. Ahwatukee Foothills is tile roofs and "
                "arterials on desert lots. Canopy is fragmented; it does not offset the slab."
            ),
            subdiv_h="3. Highest-IVC subdivisions",
            subdiv_p=(
                f"Among {n_units_all} political subdivisions of the 18 cities in the comparable index, "
                f"{n_top} Phoenix urban villages enter the top 25: {top25_txt}. "
                "Maryvale sits 5th overall, between Azcapotzalco and Cuauhtémoc. The components chart "
                "shows high z_LST max and greenness deficit, with a modest SUHI: desert pavement, "
                f"not a 13 °C island. Desert View ({coolest.ivc:.0f}) stays well outside the top 25."
            ),
        )
    if lang == "fr":
        return dict(
            rank_city=(
                f"{name} occupe la 2e place sur {n_cities} villes mesurées en avril et mai 2026, avec un "
                f"indice de vulnérabilité climatique (IVC) de {ivc:.1f} sur 100. Ahmedabad arrive en tête. "
                f"{nxt_name} ({nxt_ivc:.1f}) suit. Presque tout le max-pixel urbain dépasse 43 °C "
                f"({100 * frac_max:.0f} %) ; la moyenne du composite le fait sur {100 * frac_mean:.0f} % "
                f"du sol urbain. Le désert rural est déjà à environ {t_rural:.0f} °C, donc le SUHI urbain "
                f"n’est que de {suhi:+.1f} °C. Ce qui distingue Phoenix, c’est le revêtement et le déficit "
                f"de verdure sur un désert chaud, pas un îlot type Mexico sur une forêt fraîche."
            ),
            rank_alc=(
                f"Dans la ville, l’indice se concentre à l’ouest et dans le noyau. "
                f"{hottest.unit} arrive en tête (IVC {hottest.ivc:.0f}) : artères, parkings et toits bas. "
                f"{top[1].unit} ({top[1].ivc:.0f}) ajoute le centre, les entrepôts et la lisière de Sky Harbor "
                f"(NDVI 0,11). {top[2].unit} ({top[2].ivc:.0f}) est l’étalement neuf sur désert raclé. "
                f"{top[3].unit} ({top[3].ivc:.0f}) mélange la réserve et les piémonts pavés. "
                f"{top[4].unit} ({top[4].ivc:.0f}) ce sont toits de tuiles planifiés. "
                f"{coolest.unit} arrive dernière ({coolest.ivc:.0f}), sur la frange de conservation nord."
            ),
            rank_why=(
                f"Les villages de l’ouest (Maryvale, Central City) allient dalle, parkings et presque "
                f"pas de canopée ; la LST moyenne dépasse encore 43 °C sur la plus grande part du masque "
                f"urbain. Au nord (Desert View, North Gateway, Paradise Valley) le max-pixel reste haut "
                f"— toits de désert en avril — mais la moyenne baisse avec la densité et l’asphalte.\n\n"
                f"Contrairement à Mexico, Phoenix ne s’appuie pas sur une référence rurale fraîche "
                f"(~{t_rural:.0f} °C). Contrairement à Ahmedabad, la moyenne n’est pas déjà saturée à 89 %. "
                f"Le dessin urbain déplace encore la moyenne : ombre, albédo et moins de parking séparent "
                f"Maryvale de Desert View. {coolest.unit} montre le plancher du classement de la ville."
            ),
            rank_soil=(
                "La couverture du sol dans les cinq villages urbains au plus fort IVC, c’est asphalte, "
                "parkings, toits bas et dalle d’aéroport ou d’artère, avec peu de verdure. Maryvale, ce "
                "sont parkings de strip-mall et routes à six voies. Central City ajoute dalles du centre "
                "et pistes de Sky Harbor. Estrella, c’est le revêtement neuf sur désert. Le score urbain "
                "de South Mountain est sur les piémonts asphaltés, pas sur la réserve. Ahwatukee Foothills, "
                "toits de tuiles et artères sur lots désertiques. La canopée est fragmentée ; elle ne "
                "compense pas la dalle."
            ),
            subdiv_h="3. Subdivisions à l’IVC le plus élevé",
            subdiv_p=(
                f"Parmi les {n_units_all} subdivisions politiques des 18 villes de l’indice comparable, "
                f"{n_top} villages urbains de Phoenix entrent dans le top 25 : {top25_txt}. "
                "Maryvale est 5e au général, entre Azcapotzalco et Cuauhtémoc. Le graphique des "
                "composantes montre un z_LST max. et un déficit de verdure élevés, avec un SUHI modeste : "
                f"revêtement de désert, pas un îlot de 13 °C. Desert View ({coolest.ivc:.0f}) reste hors "
                "du top 25."
            ),
        )
    return dict(
        rank_city=(
            f"{name} ocupa el lugar 2 de {n_cities} ciudades medidas en abril y mayo de 2026, "
            f"con un Índice de Vulnerabilidad Climática (IVC) de {ivc:.1f} sobre 100. Encabeza "
            f"Ahmedabad. {nxt_name[:1].upper() + nxt_name[1:] if nxt_name else nxt_name} ({nxt_ivc:.1f}) queda a continuación. Casi todo el máximo "
            f"urbano supera 43 °C ({100 * frac_max:.0f} %); la media del compuesto lo hace en el "
            f"{100 * frac_mean:.0f} % del suelo urbano. El desierto rural ya está a unos {t_rural:.0f} °C, "
            f"así que el SUHI urbano es solo {suhi:+.1f} °C. Lo que distingue a Phoenix es el pavimento "
            f"y el déficit de verdor sobre un desierto caliente, no una isla tipo CDMX sobre un bosque fresco."
        ),
        rank_alc=(
            f"Dentro de la ciudad el índice se concentra en el poniente y el núcleo. "
            f"{hottest.unit} encabeza (IVC {hottest.ivc:.0f}): arterias, estacionamientos y azoteas bajas. "
            f"{top[1].unit} ({top[1].ivc:.0f}) suma el centro, bodegas y el borde del Sky Harbor "
            f"(NDVI 0.11). {top[2].unit} ({top[2].ivc:.0f}) es expansión nueva sobre desierto rasurado. "
            f"{top[3].unit} ({top[3].ivc:.0f}) mezcla la reserva con las faldas pavimentadas. "
            f"{top[4].unit} ({top[4].ivc:.0f}) son techos de teja planificados. "
            f"{coolest.unit} queda al final ({coolest.ivc:.0f}), en la franja de conservación del norte."
        ),
        rank_why=(
            f"Los villages del poniente (Maryvale, Central City) juntan losa, estacionamiento y casi "
            f"nada de dosel; la LST media sigue sobre 43 °C en la mayor parte de la máscara urbana. "
            f"En el norte (Desert View, North Gateway, Paradise Valley) el máximo por píxel sigue alto "
            f"—techos de desierto en abril— pero la media baja con la densidad y el asfalto.\n\n"
            f"A diferencia de la Ciudad de México, Phoenix no se apoya en una referencia rural fresca "
            f"(~{t_rural:.0f} °C). A diferencia de Ahmedabad, la media no está saturada al 89 %. "
            f"El diseño aún mueve la media: sombra, albedo y menos estacionamiento separan Maryvale "
            f"de Desert View. {coolest.unit} muestra el piso del ranking de la ciudad."
        ),
        rank_soil=(
            "El tipo de suelo en los cinco urban villages de mayor IVC es asfalto, estacionamiento, "
            "azoteas bajas y losa de aeropuerto o arteria, con poca vegetación. Maryvale son plazas "
            "y vías de seis carriles. Central City suma losas del centro y pistas del Sky Harbor. "
            "Estrella es pavimento nuevo sobre desierto. El puntaje urbano de South Mountain está en "
            "las faldas asfaltadas, no en la reserva. Ahwatukee Foothills son teja y arterias sobre "
            "lotes desérticos. El dosel es fragmentado; no compensa la losa."
        ),
        subdiv_h="3. Subdivisiones con mayor IVC",
        subdiv_p=(
            f"Entre las {n_units_all} subdivisiones políticas de las 18 ciudades del índice "
            f"comparable, {n_top} urban villages de Phoenix entran al top 25: {top25_txt}. "
            "Maryvale ocupa el 5.° lugar general, entre Azcapotzalco y Cuauhtémoc. La gráfica de "
            "componentes muestra z_LST máx. y déficit de verdor altos, con un SUHI modesto: "
            f"pavimento de desierto, no una isla de 13 °C. Desert View ({coolest.ivc:.0f}) queda "
            "fuera del top 25."
        ),
    )
