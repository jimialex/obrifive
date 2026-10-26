---
title: "0010 — Catálogo de productos por tenant y cargas trazables"
---

Estado: aceptado por la incorporación del módulo de productos, 2026-10-23.

## Contexto y drivers

Los tenants necesitan incorporar catálogos de ferretería desde archivos y sitios
web, actualizar sus precios o existencias y conocer el origen de cada cambio.

## Opciones

1. Actualizar productos directamente desde cada parser.
2. Mantener fuentes, ejecuciones, filas staging e historial de cambios.

## Decisión

Se elige la opción 2. `products` es un bounded context propio; cada presentación
vendible es un SKU por tenant, con familia opcional. Las fuentes reconcilian por
identidad externa y luego SKU. PDF queda en revisión; Excel es estructurado y los
scrapers son adaptadores aislados. BOB usa valores decimales y las ausencias no
eliminan productos.

## Consecuencias

Las importaciones son repetibles y auditables, a cambio de más tablas y una UI de
revisión. Inventario transaccional, conversión de moneda y conectores universales
quedan fuera de este módulo.
