from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SourceKind(str, Enum):
    FILE = "file"
    ECOMMERCE = "ecommerce"
    FACEBOOK_PAGE = "facebook_page"
    WHATSAPP_CATALOG = "whatsapp_catalog"


class ExtractionMethod(str, Enum):
    STRUCTURED = "structured"
    HEURISTIC = "heuristic"
    LLM = "llm"
    VISION = "vision"


class Source(BaseModel):
    location: str = Field(..., min_length=1)
    kind: SourceKind


class Target(BaseModel):
    source: Source
    location: str = Field(..., min_length=1)
    label: str | None = Field(default=None)


class Artifact(BaseModel):
    artifact_id: str
    target: Target
    content_type: str
    size_bytes: int = Field(..., ge=0)
    fetched_at: datetime

    model_config = ConfigDict(frozen=True)


class ItemProvenance(BaseModel):
    artifact_id: str
    source_location: str
    locator: str | None = Field(default=None, description="Row, post id, page or region inside the artifact")


class CatalogItem(BaseModel):
    name: str = Field(..., min_length=1)
    external_id: str | None = Field(default=None, description="Stable id in the source: product id, post id")
    external_url: str | None = Field(default=None, description="Canonical product or post URL in the source")
    sku: str | None = Field(default=None)
    raw_price: str | None = Field(default=None)
    price_bob: Decimal | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None)
    measure_quantity: Decimal | None = Field(default=None, gt=0)
    image_url: str | None = Field(default=None)
    attributes: dict[str, str] = Field(default_factory=dict)
    provenance: ItemProvenance
    method: ExtractionMethod
    confidence: float = Field(..., ge=0, le=1)


class HarvestLimits(BaseModel):
    max_targets: int = Field(default=20, ge=1, le=500)


class HarvestReport(BaseModel):
    source: Source
    artifacts: list[Artifact] = Field(default_factory=list)
    items: list[CatalogItem] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
