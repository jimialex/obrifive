# Spec Delta

## Purpose

Permite incorporar y actualizar catálogos por tenant desde archivos o fuentes web preservando su origen y cada cambio aplicado.

## ADDED Requirements

### Requirement: Fuentes y ejecuciones trazables
El sistema SHALL registrar fuentes de catálogo por tenant y una ejecución inmutable por carga o actualización, con estado, origen, checksum, conteos y errores.

#### Scenario: Registrar una carga Excel
- **WHEN** un miembro carga un Excel válido para una fuente del tenant
- **THEN** el sistema conserva la ejecución, el archivo de origen y sus resultados

### Requirement: Aplicación segura de registros
El sistema MUST aplicar automáticamente sólo filas válidas con identidad inequívoca. La conciliación MUST usar primero ID o URL externo y después SKU del tenant; filas inválidas o ambiguas MUST quedar en revisión.

#### Scenario: Actualizar un producto identificado por URL
- **WHEN** una ejecución contiene una URL externa vinculada a un producto
- **THEN** actualiza los datos observados y registra el cambio sin duplicarlo

### Requirement: Formatos y ausencias
El sistema SHALL procesar Excel estructurado, MUST enviar filas PDF a revisión y MUST conservar activos los productos no observados, registrando su última observación.

#### Scenario: Extraer un PDF
- **WHEN** un miembro carga un catálogo PDF
- **THEN** sus filas extraídas quedan disponibles para revisión antes de afectar productos
