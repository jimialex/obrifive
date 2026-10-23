# Propuesta

## Por qué

Los tenants necesitan centralizar catálogos de ferretería y construcción que hoy
llegan desde hojas de cálculo, PDF y tiendas web, sin perder su aislamiento ni
la trazabilidad de precios y existencias. El cambio permite administrar esos
productos y actualizar sus datos de forma repetible y auditable.

## Qué cambia

- Añade un catálogo de productos vendibles por tenant con familias opcionales,
  categorías jerárquicas, unidades de medida, características, precios BOB y
  existencias opcionales.
- Añade fuentes de catálogo y ejecuciones de ingestión para cargas manuales,
  Excel, PDF y adaptadores de scraping web.
- Conserva filas extraídas, reconciliación por identidad externa o SKU e
  historial inmutable de los cambios aplicados.
- Añade búsqueda y filtros de productos, además de pantallas para el catálogo,
  categorías, fuentes y estado de las ejecuciones.
- Añade una guía reutilizable para que Codex y Claude preserven los límites DDD
  del módulo durante su evolución.

## Capacidades

### Nuevas capacidades

- `tenant-product-catalog`: administración y consulta aislada de productos,
  categorías, medidas, precios y existencias por tenant.
- `catalog-ingestion`: importación y actualización trazable de catálogos desde
  fuentes de archivos o web.

### Capacidades modificadas

- Ninguna.

## Impacto

- Backend FastAPI: nuevo módulo `products`, modelos SQLAlchemy compartidos,
  migración Alembic, endpoints y trabajo diferido.
- Frontend Next.js: entidades, features, rutas protegidas y BFF para catálogo.
- Infraestructura: RustFS/S3 conserva archivos de origen; RabbitMQ procesa
  importaciones y actualizaciones programadas desde un comando operacional.
- Documentación: ADR del límite del módulo, plan de implementación y skill
  distribuido para Claude y Codex.
