"use client";

import { FileSpreadsheet, FileText, Link, Package } from "lucide-react";
import { useProductsQuery } from "@/features/products/api/products";
import { Button } from "@/shared/ui/button";
import { EmptyState } from "@/shared/ui/empty-state";
import { PageContent } from "@/shared/ui/page-content";
import { FullPageSpinner } from "@/shared/ui/spinner";

const loaders = [
  { label: "Cargar Excel", description: "Próximamente: archivo estructurado", icon: FileSpreadsheet },
  { label: "Cargar PDF", description: "Próximamente: extracción para revisión", icon: FileText },
  { label: "Cargar desde enlace", description: "Próximamente: conector por sitio", icon: Link },
];

export function ProductsView() {
  const { data: products = [], isLoading, error } = useProductsQuery();
  if (isLoading) return <FullPageSpinner />;
  if (error) return <p className="text-destructive">No se pudo cargar el catálogo.</p>;

  return <PageContent>
    <PageContent.Header icon={Package} title="Productos" subtitle="Catálogo del tenant activo, precios en BOB y existencias observadas." className="px-0 pt-0" />
    <PageContent.Body className="gap-6 px-0 pb-0">
      <section className="grid gap-3 md:grid-cols-3">
        {loaders.map(({ label, description, icon: Icon }) => <div key={label} className="rounded-lg border bg-card p-4">
          <Icon className="mb-3 h-5 w-5 text-primary" />
          <h2 className="font-medium">{label}</h2><p className="mt-1 text-sm text-muted-foreground">{description}</p>
          <Button className="mt-4 w-full" variant="outline" disabled>Próximamente</Button>
        </div>)}
      </section>
      {products.length === 0 ? <EmptyState icon={Package} title="Aún no hay productos" description="Cuando los cargadores estén disponibles, podrás importar el catálogo de este tenant." /> :
        <div className="overflow-hidden rounded-lg border"><table className="w-full text-sm"><thead className="bg-muted/50 text-left"><tr><th className="p-3">Producto</th><th className="p-3">SKU</th><th className="p-3">Medida</th><th className="p-3 text-right">Venta</th></tr></thead><tbody>{products.map((product) => <tr key={product.uuid} className="border-t"><td className="p-3 font-medium">{product.name}</td><td className="p-3 text-muted-foreground">{product.sku}</td><td className="p-3">{product.measureQuantity} {product.unitCode}</td><td className="p-3 text-right">Bs {product.salePriceBob}</td></tr>)}</tbody></table></div>}
    </PageContent.Body>
  </PageContent>;
}
