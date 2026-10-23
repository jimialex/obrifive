# Diseño

## Contexto

El backend usa módulos DDD con ORM SQLAlchemy centralizado, tenancy por dependencia y comandos diferidos. El frontend usa slices por feature y BFF same-origin. Ver `proposal.md` y las especificaciones del cambio.

## Objetivos / no objetivos

**Objetivos:** catálogo aislado, búsqueda, precios decimales BOB y cargas trazables desde fuentes externas.

**No objetivos:** kardex, reservas, conversión de moneda, conector universal de scraping ni aplicación automática de filas PDF.

## Decisiones

- Crear `products` como bounded context; entidades de dominio y puertos viven allí, mientras ORM y revisiones Alembic permanecen en `common/database`. Alternativa descartada: extender `tenants`, que mezclaría membresía con comercio.
- Representar cada presentación como `Product` con SKU único por tenant y `ProductFamily` opcional. Alternativa descartada: variantes JSON, que impide consultas y conciliación confiable.
- Guardar dinero, stock y medidas en `NUMERIC`; BOB queda implícito en v1. Alternativa descartada: `float`, por errores de precisión.
- Modelar ingestión como fuente, ejecución y fila staging; la ejecución conserva el origen y el historial de cambios. Alternativa descartada: actualizar productos directamente desde parsers, que elimina auditoría y revisión.
- Usar puertos de importador y scraper; Excel será el primer adaptador, PDF queda en staging. Alternativa descartada: acoplar parsers a endpoints.
- Un comando operacional encuentra fuentes vencidas y encola trabajos. Alternativa descartada: scheduler dentro de la API, que duplica ejecuciones al escalar.

## Riesgos / trade-offs

- [PDF con tablas ambiguas] → conservar filas para revisión y no aplicar automáticamente.
- [Scraping frágil por sitio] → adaptadores aislados, reintentos acotados y errores por ejecución.
- [Importaciones duplicadas] → checksum e identidades externas únicas por fuente.
- [Migración con muchos índices] → validar en base vacía y desde la revisión anterior.

## Plan de migración

1. Desplegar tablas e índices sin consumidores.
2. Desplegar API y worker, luego frontend.
3. Cargar fuentes nuevas; no hay datos previos que transformar.
4. Revertir la aplicación dejando tablas intactas si fuera necesario; no ejecutar downgrade destructivo en producción.
