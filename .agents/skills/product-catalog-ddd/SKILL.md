---
name: product-catalog-ddd
description: Diseña o implementa productos, catálogos, importaciones y scraping por tenant preservando los límites DDD, la trazabilidad y el aislamiento. Úsalo para cambios del módulo products; no para inventario transaccional o facturación.
---

# Catálogo de productos por tenant

Lee `plans/productos-tenant.md`, el OpenSpec activo, `backend/AGENTS.md` y/o
`frontend/AGENTS.md` antes de cambiar el módulo.

- Cada producto y fuente pertenece al tenant resuelto por la dependencia; nunca
  aceptes un `tenant_id` desde el cuerpo para sortear el scope.
- Los precios BOB, stock y medidas usan `Decimal`, nunca `float`. El stock es
  observacional: no añadas kardex, reservas ni conversiones de moneda sin una
  nueva definición y ADR.
- Toda importación conserva fuente, ejecución, origen y cambios. Reconciliación:
  ID/URL externo, luego SKU del tenant; una ambigüedad queda en revisión.
- Usa `schema-change` para tablas/migraciones, `backend-change` para casos de
  uso y adaptadores, `frontend-change` para la UI y `openapi-sync` al cambiar
  contratos HTTP. Browser sólo llama a `/api`.
- PDF pasa por staging; un scraper es un adaptador por sitio y nunca contiene
  reglas del dominio. La actualización programada se encola desde un comando
  operacional, no desde un scheduler de la API.

Valida los límites de tenant, idempotencia de importaciones, historial de cambios
y búsqueda antes de cerrar el cambio.
