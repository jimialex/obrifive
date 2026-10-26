from fastapi import APIRouter, Depends
from sqlalchemy import select

from src.common.database.models.products.catalog import ProductORM
from src.common.infrastructure.dependencies.common import AsyncSessionDep
from src.common.infrastructure.dependencies.tenant import get_required_tenant_user, required_tenant_for
from src.common.domain.models.tenants.tenant_user import TenantUser
from src.common.infrastructure.responses.api_json import ApiJSONResponse

products_router = APIRouter(prefix="/products", tags=["products"])


async def list_products(
    session: AsyncSessionDep,
    current_tenant_user: TenantUser = Depends(get_required_tenant_user),
) -> ApiJSONResponse:
    """Lists only the products owned by the tenant selected through X-Tenant."""
    tenant = required_tenant_for(current_tenant_user)
    rows = (await session.scalars(select(ProductORM).where(ProductORM.tenant_id == tenant.uuid).order_by(ProductORM.name))).all()
    return ApiJSONResponse(content=[
        {
            "uuid": str(product.uuid), "sku": product.sku, "name": product.name,
            "description": product.description, "unitCode": product.unit_code,
            "measureQuantity": str(product.measure_quantity),
            "purchasePriceBob": str(product.purchase_price_bob),
            "salePriceBob": str(product.sale_price_bob),
            "availableQuantity": str(product.available_quantity) if product.available_quantity is not None else None,
            "availability": product.availability,
        }
        for product in rows
    ])


products_router.add_api_route("", list_products, methods=["GET"], summary="List products for the X-Tenant header")
