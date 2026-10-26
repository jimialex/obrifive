# Tasks

## 1. Base del catálogo

- [ ] 1.1 Crear el módulo `products`, modelos ORM, migración e invariantes de tenancy; verificar con `just backend check-migrations` y tests de repositorio.
- [ ] 1.2 Implementar entidades, puertos, repositorios y casos de uso de productos, familias, categorías y características; verificar con pytest unitario.
- [ ] 1.3 Exponer CRUD y búsqueda paginada con contratos OpenAPI; verificar con pruebas API de aislamiento por tenant y `just backend openapi`.

## 2. Interfaz de catálogo

- [ ] 2.1 Añadir entidades y feature frontend para lista, filtros y detalle de productos; verificar con Vitest y `just frontend check`.
- [ ] 2.2 Añadir formularios accesibles de producto, familia y categoría; verificar estados vacío, error y éxito en pruebas de componentes.

## 3. Ingestión trazable

- [ ] 3.1 Añadir fuentes, ejecuciones, staging, identidad externa e historial; verificar idempotencia y filas ambiguas con pruebas unitarias y repositorio.
- [ ] 3.2 Implementar carga S3 y adaptador Excel; verificar una carga repetida sin duplicados y sus cambios auditados.
- [ ] 3.3 Implementar staging PDF, puerto de scraper y comando de actualización vencida; verificar que PDF no aplique filas sin revisión y que el comando encole fuentes debidas.

## 4. Operación y guía

- [ ] 4.1 Añadir UI de fuentes, cargas y revisión; verificar el flujo browser → BFF → API.
- [ ] 4.2 Crear ADR y skill `product-catalog-ddd`, sincronizarlo; verificar con `just agent-check`, `just sync-skills` y `just agent-check`.

## 5. Evidencia integrada

- [ ] 5.1 Ejecutar `just check`, pruebas focalizadas, migraciones, OpenAPI y build frontend; registrar revisión, resultados y criterios pendientes en esta change.
