# Harvester — servidor MCP de catálogos

Servidor [FastMCP](https://gofastmcp.com) que obtiene catálogos de ferreterías desde
archivos, tiendas web, páginas de Facebook y catálogos de WhatsApp, y los devuelve
como `CatalogItem` candidatos. No escribe en la base de datos de Obrifive: el
backend convierte los ítems en filas de revisión (`catalog-ingestion`).

## Flujo

```
detect_source → list_targets → fetch_target → extract_items
                     (o harvest para todo el flujo)
```

| Herramienta | Entrada | Salida |
| --- | --- | --- |
| `detect_source` | `location` | `Source` con su `kind` |
| `list_targets` | `location`, `max_targets` | `Target[]` |
| `fetch_target` | `Target` | `Artifact` guardado en el store |
| `extract_items` | `artifact_id` | `CatalogItem[]` con procedencia y confianza |
| `harvest` | `location`, `max_targets` | `HarvestReport` con artefactos, ítems y errores |

Ubicaciones soportadas hoy: URLs `http(s)` a archivos y `inbox://<ruta>` para
archivos dentro de `HARVESTER_INBOX_DIR`. El único extractor es CSV.

## Capas

| Capa | Contenido |
| --- | --- |
| `src/domain` | Contratos (`Source`, `Target`, `Artifact`, `CatalogItem`), puertos y normalización de precios BOB |
| `src/application` | Registros de adaptadores/extractores y casos de uso |
| `src/infrastructure` | Adaptadores por canal, extractores, store de artefactos, settings y wiring |
| `src/presentation` | Servidor FastMCP y herramientas |

## Extender

- **Nuevo canal**: implementa `SourceAdapter` en `src/infrastructure/adapters/` y
  regístralo en `src/infrastructure/container.py`. `can_handle` debe ser barato y no
  hacer red.
- **Nuevo formato**: implementa `ItemExtractor` en `src/infrastructure/extractors/`
  y regístralo. Usa `ExtractionMethod.LLM` o `VISION` para resultados de modelos;
  esos ítems siempre van a revisión.

## Comandos

```bash
just harvester install   # uv sync
just harvester dev       # stdio
just harvester serve     # HTTP en :8300
just harvester test
just harvester check
```

## Configuración

| Variable | Default |
| --- | --- |
| `HARVESTER_DATA_DIR` | `.data/artifacts` |
| `HARVESTER_INBOX_DIR` | `.data/inbox` |
| `HARVESTER_HTTP_TIMEOUT_SECONDS` | `30` |
| `HARVESTER_MAX_DOWNLOAD_BYTES` | `26214400` |
