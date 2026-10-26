# E2 — ¿Qué expone una página de Facebook sin sesión?

Fecha: 2026-10-26. Script: `browser_probe.py` (Chromium headless, sin sesión, una
visita por página, 3 desplazamientos, pausa de 8 s entre páginas).

## Muestra

Seis páginas de ferreterías bolivianas encontradas por búsqueda web: Ferretería
Universal, Galba, FERBO y Casa Cruceña (Santa Cruz); Tools Center Stanley y
Moyatec (El Alto).

## Resultado

| Dato | Visible sin sesión |
| --- | --- |
| Nombre, categoría, seguidores | Sí, en las 6 |
| Dirección, teléfono, correo | Sí, en las 6 |
| Sitio web propio | 2 de 6 (`ferreteriauniversal.com.bo`, `galba.com.bo`) |
| Publicaciones | 1 o 2 por página, con texto truncado ("Ver más") |
| Productos o precios | No: las publicaciones visibles eran saludos y promociones genéricas |
| Fotos, catálogo, tienda | No: tras desplazarse aparece un modal de login que tapa la página |

El muro de login aparece en la primera visita, apenas se desplaza la página; no
hace falta insistir para que aparezca.

## Conclusiones

1. **El scraping de Facebook sin sesión no sirve para obtener catálogos.** Solo
   expone la ficha y una o dos publicaciones. Insistir (más páginas, cuentas falsas,
   evadir el modal) iría contra los términos de Meta y sería frágil.
2. **La ficha sí sirve para descubrir otros canales**: sitio web, número de
   WhatsApp, correo y dirección. Una página de Facebook se convierte en un punto de
   partida que deriva a canales legibles (web en E1, WhatsApp en T8).
3. **El contenido real de Facebook solo es accesible con autorización**: la
   ferretería conecta su página y se leen publicaciones y fotos con Graph API (T7).

## Impacto en el plan

- Descartar T11 (scraping público de Facebook).
- Añadir un adaptador "ficha de Facebook" barato que solo extrae los enlaces a otros
  canales y deriva a sus adaptadores.
- T7 (Graph API con OAuth de la página) queda como única vía para publicaciones,
  condicionada a E5.
- Probar en E1 los dos sitios descubiertos (`ferreteriauniversal.com.bo`,
  `galba.com.bo`).
