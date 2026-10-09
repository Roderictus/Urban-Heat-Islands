"""Shared Priority-1 selection text and comparable-metric constants."""

METRIC_VERSION = "ivc-l4-v1"

WHY_PRIORITY1_P1 = (
    "Estas ciudades son la Prioridad 1 de un recorte explícito: más de dos millones de habitantes "
    "en la franja 18–42 °N, el mismo cinturón latitudinal en el que el proyecto ya mide islas de calor. "
    "No se eligieron por ser las más calientes del planeta, sino por el producto peligro × exposición × "
    "vulnerabilidad. IPCC, OMS/OMM, el índice GUHVI (2025) y el ranking Oxford 2026 (205 ciudades de más "
    "de un millón) coinciden en ese marco: Riad o Dubai tienen picos brutales y mucha refrigeración; "
    "Karachi o Delhi tienen menos capacidad de afrontamiento y más mortalidad esperada. Oxford concentra "
    "más del 95 % de las peor rankeadas en Sur/Sureste de Asia y África; Basora, vecina de Bagdad, es la "
    "ciudad de mayor riesgo de esa lista."
)

WHY_PRIORITY1_P2 = (
    "Dentro de esa franja, Prioridad 1 cubre cuatro climas que el índice Landsat debe distinguir con la "
    "misma métrica ivc-l4-v1: el pre-monzón seco de Delhi (la mayor población expuesta a olas de calor), "
    "el árido de El Cairo y Bagdad (picos de LST entre los más altos; El Cairo entra en el top 50 Oxford), "
    "el húmedo costero de Karachi (ola mortal de 2015; Mora et al.: condiciones equivalentes podrían "
    "volverse anuales a +2 °C) y dos anclas del proyecto —Ciudad de México en el borde sur, aire fresco "
    "por altitud pero LST urbana por encima de 60 °C, y Madrid en el borde norte, mediterráneo interior "
    "con olas e incremento relativo rápido, ya en la franja Fra-Spa-Por. Abril–mayo de 2026 es la ventana "
    "común a propósito: en Delhi y Karachi es el pico pre-monzón; en El Cairo y Bagdad ya hay calor "
    "intenso; en Madrid y CDMX es primavera, no el máximo anual. Se mantiene para que un IVC 60 en un "
    "distrito sea comparable entre ciudades."
)

WHY_PRIORITY2_P1 = (
    "Prioridad 2 sigue el mismo recorte —más de dos millones de habitantes en 18–42 °N— y el mismo "
    "marco peligro × exposición × vulnerabilidad, un peldaño por debajo de las seis de cabecera. "
    "No sustituye a Delhi o Karachi: las complementa. Lahore, Dhaka y Ahmedabad concentran el "
    "crecimiento de persona-días de calor extremo en Sur de Asia (Tuholske 2021); Phoenix es el "
    "referente ECOSTRESS de quemaduras por pavimento (49–60 °C) ya usado en el estilo cartográfico "
    "del proyecto; Teherán aporta una megaciudad semiárida de cuenca cerrada; Monterrey es el par "
    "seco-industrial de la Ciudad de México."
)

WHY_PRIORITY2_P2 = (
    "La métrica es la misma ivc-l4-v1 y la ventana sigue siendo abril–mayo de 2026, para que un IVC 60 "
    "en un town de Lahore sea comparable a Iztapalapa o a un urban village de Phoenix. En Lahore, "
    "Ahmedabad y Dhaka esa ventana es pre-monzón o temporada caliente. En Phoenix y Monterrey el "
    "máximo anual es junio–agosto; entran a propósito en primavera para no romper la escala fija. "
    "Ahmedabad, además, tiene un plan de acción térmica pionero en India: el índice mide exposición "
    "de superficie, no el éxito del plan."
)

WHY_PRIORITY3_P1 = (
    "Prioridad 3 cierra el recorte de más de dos millones en 18–42 °N con contrastes de capacidad "
    "de afrontamiento, no con las ciudades más calientes que queden. Riad tiene picos de desierto "
    "y mucha refrigeración: sirve de contraste frente a Bagdad o El Cairo. Houston aporta calor "
    "húmedo estadounidense; Wuhan, una ciudad-horno de cuenca en China; Barcelona y Roma anclan "
    "el Mediterráneo costero e interior frente a Madrid; Casablanca pone el Magreb en la misma "
    "latitud que Phoenix, con menos capacidad de adaptación que Europa."
)

WHY_PRIORITY3_P2 = (
    "La métrica sigue siendo ivc-l4-v1 y la ventana abril–mayo de 2026. En Riad y Casablanca esa "
    "ventana ya es temporada caliente. En Houston y Wuhan el pico suele ser julio–agosto; en "
    "Barcelona y Roma es primavera, como en Madrid. Entran a propósito en la misma escala fija, "
    "para que un IVC 60 en un distrito de Houston o un municipio de Roma sea comparable a "
    "Iztapalapa o a un urban village de Phoenix."
)
