INSERT INTO public.directus_collections (collection, icon, note, hidden, singleton, accountability, sort, collapse, versioning) VALUES
    ('product_families', 'category', 'Familias de productos por tenant', false, false, 'all', 20, 'open', false),
    ('product_categories', 'account_tree', 'Categorías jerárquicas por tenant', false, false, 'all', 21, 'open', false),
    ('products', 'inventory_2', 'Productos vendibles por tenant', false, false, 'all', 22, 'open', false),
    ('catalog_sources', 'cloud_download', 'Fuentes de catálogo', false, false, 'all', 23, 'open', false),
    ('catalog_ingestions', 'sync', 'Ejecuciones de carga', false, false, 'all', 24, 'open', false),
    ('product_changes', 'history', 'Auditoría de cambios de producto', false, false, 'all', 25, 'open', false)
ON CONFLICT (collection) DO UPDATE SET icon = EXCLUDED.icon, note = EXCLUDED.note, hidden = EXCLUDED.hidden, sort = EXCLUDED.sort, collapse = EXCLUDED.collapse;
