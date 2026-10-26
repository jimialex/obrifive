from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from src.domain.exceptions import HarvesterError
from src.domain.models import Artifact, CatalogItem, HarvestLimits, HarvestReport, Source, Target
from src.infrastructure.container import HarvesterContainer, build_container
from src.infrastructure.settings import HarvesterSettings

SERVER_INSTRUCTIONS = (
    "Harvests hardware-store product catalogs from files, e-commerce sites, Facebook pages and WhatsApp "
    "catalogs. Typical flow: detect_source -> list_targets -> fetch_target -> extract_items, or harvest for "
    "the whole pipeline. Items are candidates for human review, never applied products."
)

LocationParam = Annotated[
    str,
    Field(description="Source location: an http(s) URL or inbox://<relative path> for uploaded files"),
]
MaxTargetsParam = Annotated[int, Field(ge=1, le=500, description="Maximum number of targets to visit")]


def _container(ctx: Context) -> HarvesterContainer:
    return ctx.lifespan_context["container"]


def create_server(harvester_settings: HarvesterSettings | None = None) -> FastMCP:
    resolved_settings = harvester_settings or HarvesterSettings()

    @asynccontextmanager
    async def lifespan(_server: FastMCP) -> AsyncGenerator[dict[str, Any]]:
        async with build_container(resolved_settings) as harvester_container:
            yield {"container": harvester_container}

    mcp = FastMCP("obrifive-harvester", instructions=SERVER_INSTRUCTIONS, lifespan=lifespan)

    @mcp.tool(annotations={"readOnlyHint": True})
    async def detect_source(location: LocationParam, ctx: Context) -> Source:
        """Classify a location into a supported source kind."""
        try:
            return _container(ctx).detect_source.execute(location)
        except HarvesterError as harvester_error:
            raise ToolError(str(harvester_error))

    @mcp.tool(annotations={"readOnlyHint": True})
    async def list_targets(location: LocationParam, ctx: Context, max_targets: MaxTargetsParam = 20) -> list[Target]:
        """List the pages, posts, files or catalog entries to fetch from a source."""
        harvester_container = _container(ctx)
        try:
            source = harvester_container.detect_source.execute(location)
            return await harvester_container.list_targets.execute(source, HarvestLimits(max_targets=max_targets))
        except HarvesterError as harvester_error:
            raise ToolError(str(harvester_error))

    @mcp.tool
    async def fetch_target(target: Target, ctx: Context) -> Artifact:
        """Fetch one target and store its raw content as an artifact."""
        try:
            return await _container(ctx).fetch_target.execute(target)
        except HarvesterError as harvester_error:
            raise ToolError(str(harvester_error))

    @mcp.tool(annotations={"readOnlyHint": True})
    async def extract_items(artifact_id: str, ctx: Context) -> list[CatalogItem]:
        """Extract candidate catalog items from a stored artifact."""
        try:
            return await _container(ctx).extract_items.execute(artifact_id)
        except HarvesterError as harvester_error:
            raise ToolError(str(harvester_error))

    @mcp.tool
    async def harvest(location: LocationParam, ctx: Context, max_targets: MaxTargetsParam = 20) -> HarvestReport:
        """Run detect, list, fetch and extract for a source and report items and per-target errors."""
        try:
            return await _container(ctx).harvest_source.execute(location, HarvestLimits(max_targets=max_targets))
        except HarvesterError as harvester_error:
            raise ToolError(str(harvester_error))

    return mcp


mcp = create_server()

if __name__ == "__main__":
    mcp.run()
