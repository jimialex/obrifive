from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.common.database.mixins.common import Base, UUIDTimestampMixin


class ProductFamilyORM(Base, UUIDTimestampMixin):
    __tablename__ = "product_families"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_product_families_tenant_name"),)
    tenant_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("tenants.uuid", ondelete="CASCADE", name="fk_product_families_tenant_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class ProductCategoryORM(Base, UUIDTimestampMixin):
    __tablename__ = "product_categories"
    __table_args__ = (UniqueConstraint("tenant_id", "parent_id", "name", name="uq_product_categories_tenant_parent_name"),)
    tenant_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("tenants.uuid", ondelete="CASCADE", name="fk_product_categories_tenant_id"), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("product_categories.uuid", ondelete="SET NULL", name="fk_product_categories_parent_id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class ProductORM(Base, UUIDTimestampMixin):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("tenant_id", "sku", name="uq_products_tenant_sku"),
        Index("ix_products_tenant_name", "tenant_id", "name"),
    )
    tenant_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("tenants.uuid", ondelete="CASCADE", name="fk_products_tenant_id"), nullable=False)
    family_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("product_families.uuid", ondelete="SET NULL", name="fk_products_family_id"), nullable=True)
    category_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("product_categories.uuid", ondelete="SET NULL", name="fk_products_category_id"), nullable=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit_code: Mapped[str] = mapped_column(String(20), nullable=False)
    measure_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, server_default="1")
    purchase_price_bob: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    sale_price_bob: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    available_quantity: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    availability: Mapped[str] = mapped_column(String(30), nullable=False, server_default="available")
    last_stock_observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ProductAttributeValueORM(Base, UUIDTimestampMixin):
    __tablename__ = "product_attribute_values"
    __table_args__ = (UniqueConstraint("product_id", "name", name="uq_product_attribute_values_product_name"),)
    product_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("products.uuid", ondelete="CASCADE", name="fk_product_attribute_values_product_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)


class CatalogSourceORM(Base, UUIDTimestampMixin):
    __tablename__ = "catalog_sources"
    tenant_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("tenants.uuid", ondelete="CASCADE", name="fk_catalog_sources_tenant_id"), nullable=False)
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    config: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    refresh_interval_minutes: Mapped[int | None] = mapped_column(nullable=True)
    next_refresh_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, server_default="true")


class CatalogIngestionORM(Base, UUIDTimestampMixin):
    __tablename__ = "catalog_ingestions"
    source_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("catalog_sources.uuid", ondelete="CASCADE", name="fk_catalog_ingestions_source_id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    raw_asset_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    accepted_count: Mapped[int] = mapped_column(nullable=False, server_default="0")
    rejected_count: Mapped[int] = mapped_column(nullable=False, server_default="0")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ProductChangeORM(Base, UUIDTimestampMixin):
    __tablename__ = "product_changes"
    product_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("products.uuid", ondelete="CASCADE", name="fk_product_changes_product_id"), nullable=False)
    ingestion_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("catalog_ingestions.uuid", ondelete="SET NULL", name="fk_product_changes_ingestion_id"), nullable=True)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    previous_values: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
