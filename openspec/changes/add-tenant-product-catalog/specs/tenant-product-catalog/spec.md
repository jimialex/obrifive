# Spec Delta

## Purpose

Permite que cada tenant administre un catálogo propio de productos vendibles sin exponer datos de otros tenants.

## ADDED Requirements

### Requirement: Catálogo aislado por tenant
El sistema SHALL permitir a un miembro autorizado crear, consultar, editar y desactivar productos exclusivamente dentro del tenant activo. Cada producto MUST tener nombre, SKU único por tenant, unidad de medida, precio de compra y venta en BOB; la familia y la cantidad disponible son opcionales.

#### Scenario: Crear una presentación vendible
- **WHEN** un miembro crea "Pintura blanca 1 L" con SKU, precios BOB y unidad L
- **THEN** el producto queda disponible únicamente en el catálogo del tenant activo

#### Scenario: Aislamiento entre tenants
- **WHEN** un miembro consulta un producto que pertenece a otro tenant
- **THEN** el sistema no devuelve ni modifica el producto

### Requirement: Búsqueda y clasificación
El sistema SHALL permitir categorías jerárquicas, familias y características por producto, y una búsqueda paginada por texto, categoría, unidad, disponibilidad y rango de precio.

#### Scenario: Buscar por característica
- **WHEN** un miembro busca "galvanizado"
- **THEN** recibe productos cuyo nombre, detalle o característica contenga ese texto

### Requirement: Formato monetario BOB
El sistema MUST almacenar precios como valores decimales BOB y aceptar entradas equivalentes con punto o coma decimal.

#### Scenario: Normalizar coma decimal
- **WHEN** un miembro registra un precio "124,50"
- **THEN** el producto conserva el valor decimal BOB 124.50
