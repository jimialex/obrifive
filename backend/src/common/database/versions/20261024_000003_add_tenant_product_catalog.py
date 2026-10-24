"""Add tenant-scoped product catalog persistence.

Revision ID: 20261024_000003
Revises: 20260907_000002
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20261024_000003"
down_revision = "20260907_000002"
branch_labels = None
depends_on = None


def _uuid() -> sa.Column:
    return sa.Column("uuid", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False)


def _timestamps() -> list[sa.Column]:
    return [sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False)]


def upgrade() -> None:
    op.create_table("product_families", _uuid(), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("name", sa.String(255), nullable=False), sa.Column("description", sa.Text()), *_timestamps(), sa.ForeignKeyConstraint(["tenant_id"], ["tenants.uuid"], name="fk_product_families_tenant_id", ondelete="CASCADE"), sa.UniqueConstraint("tenant_id", "name", name="uq_product_families_tenant_name"))
    op.create_table("product_categories", _uuid(), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("parent_id", postgresql.UUID(as_uuid=True)), sa.Column("name", sa.String(255), nullable=False), *_timestamps(), sa.ForeignKeyConstraint(["tenant_id"], ["tenants.uuid"], name="fk_product_categories_tenant_id", ondelete="CASCADE"), sa.ForeignKeyConstraint(["parent_id"], ["product_categories.uuid"], name="fk_product_categories_parent_id", ondelete="SET NULL"), sa.UniqueConstraint("tenant_id", "parent_id", "name", name="uq_product_categories_tenant_parent_name"))
    op.create_table("products", _uuid(), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("family_id", postgresql.UUID(as_uuid=True)), sa.Column("category_id", postgresql.UUID(as_uuid=True)), sa.Column("sku", sa.String(100), nullable=False), sa.Column("name", sa.String(255), nullable=False), sa.Column("description", sa.Text()), sa.Column("unit_code", sa.String(20), nullable=False), sa.Column("measure_quantity", sa.Numeric(18, 4), server_default="1", nullable=False), sa.Column("purchase_price_bob", sa.Numeric(18, 4), nullable=False), sa.Column("sale_price_bob", sa.Numeric(18, 4), nullable=False), sa.Column("available_quantity", sa.Numeric(18, 4)), sa.Column("availability", sa.String(30), server_default="available", nullable=False), sa.Column("last_stock_observed_at", sa.DateTime(timezone=True)), *_timestamps(), sa.ForeignKeyConstraint(["tenant_id"], ["tenants.uuid"], name="fk_products_tenant_id", ondelete="CASCADE"), sa.ForeignKeyConstraint(["family_id"], ["product_families.uuid"], name="fk_products_family_id", ondelete="SET NULL"), sa.ForeignKeyConstraint(["category_id"], ["product_categories.uuid"], name="fk_products_category_id", ondelete="SET NULL"), sa.UniqueConstraint("tenant_id", "sku", name="uq_products_tenant_sku"))
    op.create_index("ix_products_tenant_name", "products", ["tenant_id", "name"])
    op.create_table("product_attribute_values", _uuid(), sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("name", sa.String(100), nullable=False), sa.Column("value", sa.Text(), nullable=False), *_timestamps(), sa.ForeignKeyConstraint(["product_id"], ["products.uuid"], name="fk_product_attribute_values_product_id", ondelete="CASCADE"), sa.UniqueConstraint("product_id", "name", name="uq_product_attribute_values_product_name"))
    op.create_table("catalog_sources", _uuid(), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("kind", sa.String(30), nullable=False), sa.Column("name", sa.String(255), nullable=False), sa.Column("location", sa.Text()), sa.Column("config", postgresql.JSONB()), sa.Column("refresh_interval_minutes", sa.Integer()), sa.Column("next_refresh_at", sa.DateTime(timezone=True)), sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False), *_timestamps(), sa.ForeignKeyConstraint(["tenant_id"], ["tenants.uuid"], name="fk_catalog_sources_tenant_id", ondelete="CASCADE"))
    op.create_table("catalog_ingestions", _uuid(), sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("raw_asset_key", sa.Text()), sa.Column("checksum", sa.String(128)), sa.Column("accepted_count", sa.Integer(), server_default="0", nullable=False), sa.Column("rejected_count", sa.Integer(), server_default="0", nullable=False), sa.Column("completed_at", sa.DateTime(timezone=True)), *_timestamps(), sa.ForeignKeyConstraint(["source_id"], ["catalog_sources.uuid"], name="fk_catalog_ingestions_source_id", ondelete="CASCADE"))
    op.create_table("product_changes", _uuid(), sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("ingestion_id", postgresql.UUID(as_uuid=True)), sa.Column("action", sa.String(30), nullable=False), sa.Column("previous_values", postgresql.JSONB()), sa.Column("new_values", postgresql.JSONB()), *_timestamps(), sa.ForeignKeyConstraint(["product_id"], ["products.uuid"], name="fk_product_changes_product_id", ondelete="CASCADE"), sa.ForeignKeyConstraint(["ingestion_id"], ["catalog_ingestions.uuid"], name="fk_product_changes_ingestion_id", ondelete="SET NULL"))


def downgrade() -> None:
    for table in ("product_changes", "catalog_ingestions", "catalog_sources", "product_attribute_values", "products", "product_categories", "product_families"):
        op.drop_table(table)
