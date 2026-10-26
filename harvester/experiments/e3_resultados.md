# E3 — ¿El catálogo de WhatsApp se ve en un navegador?

Fecha: 2026-10-26. Script: `browser_probe.py` (Chromium headless, sin sesión).
Caso: el número de WhatsApp que publica Ferretería Pari en su sitio web.

## Resultado

**No.** `wa.me/c/<número>` redirige a `whatsapp.com/catalog/<número>/`. La página
confirma que el catálogo existe (título "Ver el catálogo de ferretería ferropari en
WhatsApp"), pero solo ofrece "Abrir aplicación" o "Continuar en WhatsApp Web". No
muestra productos, precios ni imágenes, y no hace llamadas a APIs con datos del
catálogo.

No se probó WhatsApp Web con una cuenta ni clientes no oficiales: requieren sesión
de un número real, violan los términos de WhatsApp y arriesgan el bloqueo del número.
Tampoco se suplantaron bots de vista previa para obtener metadatos.

## Conclusiones

1. El enlace `wa.me/c/` sirve solo para **detectar** que una ferretería tiene
   catálogo, no para leerlo.
2. Las vías legítimas para obtener el catálogo de WhatsApp son:
   - **Con autorización de la ferretería:** si su catálogo vive en Meta Commerce
     Manager, leerlo con la API de catálogos.
   - **Por reenvío:** la ferretería reenvía productos, fotos o cotizaciones a un
     número de Obrifive en WhatsApp Cloud API (T8), y pasan por el extractor de
     visión (T5).
3. Para ferreterías de terceros sin autorización no hay una vía oficial.

## Impacto en el plan

- T8 (webhook de WhatsApp Cloud) es la vía principal para el canal WhatsApp.
- Añadir a `detect_source` el reconocimiento de `wa.me/c/` y `whatsapp.com/catalog/`
  como `whatsapp_catalog`, con una respuesta que indique la vía soportada en lugar de
  intentar leerlo.
- Validar en E5 si las ferreterías tienen el catálogo en Commerce Manager o solo en
  la app WhatsApp Business.
