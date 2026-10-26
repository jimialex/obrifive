# E1 — Cobertura de tiendas web de ferreterías bolivianas

Fecha: 2026-10-26. Scripts: `e1_ecommerce_probe.py` (HTTP) y `browser_probe.py`
(Chromium headless). Volumen bajo: ~1 solicitud por segundo, una sola pasada.

## Muestra

La búsqueda web encontró muy pocas ferreterías bolivianas con tienda propia. Los
directorios (amarillas.bo, boliviaentusmanos.com, boliviaempresas.com) no publican
sitios web, solo teléfonos. Muestra final: 3 sitios propios y 3 tiendas dentro del
marketplace Construex. Después de E2 se agregaron dos sitios descubiertos en
Facebook (Galba y Ferretería Universal).

| Sitio | Plataforma | Catálogo legible | Precios | Mejor estrategia |
| --- | --- | --- | --- | --- |
| ferreteriapari.com (Santa Cruz) | WooCommerce | Sí: Store API pública, 94 productos, 92 con SKU | **No**: todos en 0, se cotiza por WhatsApp | API `wp-json/wc/store/v1/products` |
| morales.com.bo (Tarija, Potosí) | Shopify | Sí en navegador (607 productos en Construcción y Ferretería) | **Sí**, en Bs | Navegador; HTTP directo y `products.json` responden 429 |
| mastertoolsbolivia.framer.website (Cochabamba) | Framer | No: página institucional sin catálogo | No | No aplica; derivar a WhatsApp/Facebook |
| galba.com.bo (Santa Cruz, hallado en E2) | WooCommerce | Sí: Store API pública, 837 productos, 99 % con SKU | **Sí**: 91 % con precio en BOB (muestra de 100) | API `wp-json/wc/store/v1/products` |
| ferreteriauniversal.com.bo (hallado en E2) | — | No: el dominio no responde | — | No aplica |
| Construex: Ferretería Capriles, Todo Ideal, El Ofertón | Next.js (marketplace) | Sí: nombre y descripción en el HTML del servidor | **No**: formulario "Cotiza gratis" | Un adaptador para todo el marketplace |

## Conclusiones

1. **La web pocas veces trae precios.** Solo 2 de 5 fuentes con catálogo los
   publican (Morales y Galba). Lo común es un catálogo sin precio y la cotización
   por WhatsApp o formulario. El precio tendrá que venir sobre todo de
   cotizaciones, listas PDF o fotos (E4).
2. **Los datos estructurados no sirven aquí.** Ningún sitio expone JSON-LD
   `Product`; Pari solo tiene el marcado de Yoast (WebPage, Organization).
3. **Las APIs de plataforma sí sirven.** WooCommerce es la plataforma más común
   (Pari y Galba) y su Store API entrega el catálogo con SKU, categorías y precio
   en BOB cuando existe. Shopify bloquea clientes HTTP
   (429) pero sirve la página al navegador.
4. **Construex es un canal en sí mismo.** Varias ferreterías publican ahí; un solo
   adaptador cubre a todas. Su `robots.txt` permite `User-agent: *`, bloquea bots de
   IA conocidos y declara `ai-train=no` (no aplica a extracción, pero conviene
   respetarlo y no reutilizar su contenido para entrenar).
5. **WhatsApp aparece en la mayoría de los sitios** como canal de venta y cotización, lo que
   refuerza el webhook de WhatsApp (T8) como fuente principal de precios.

## Impacto en el plan

- Subir prioridad: adaptador WooCommerce (T2), adaptador Construex (nuevo), entrada
  de cotizaciones por WhatsApp (T8) y extractor de visión (T5).
- Bajar prioridad: adaptador JSON-LD/sitemap genérico (T1).
- Shopify necesita navegador (T3) o `products.json` desde el contexto del navegador.
- Los productos sin precio deben poder entrar a revisión con `price_bob` vacío.

## Nota sobre el script

La detección de plataformas por subcadenas da falsos positivos: Galba salió como
`vtex` además de WooCommerce. Para producción, detectar por señales específicas
(rutas de API, cabeceras) en vez de buscar texto en el HTML.
