from decimal import Decimal
from pathlib import Path

import pytest
from expects import contain, equal, expect, have_len
from fastmcp import Client
from fastmcp.exceptions import ToolError

from src.infrastructure.settings import HarvesterSettings
from src.presentation.server import create_server


@pytest.fixture
def harvester_settings(tmp_path: Path) -> HarvesterSettings:
    inbox_dir = tmp_path / "inbox"
    inbox_dir.mkdir()
    (inbox_dir / "ferreteria.csv").write_text('sku,nombre,precio\nTB-1,Tubo PVC 1/2,"25,00"\n')
    return HarvesterSettings(data_dir=tmp_path / "artifacts", inbox_dir=inbox_dir)


class HarvesterServerTests:
    async def test_exposes_pipeline_tools(self, harvester_settings: HarvesterSettings):
        async with Client(create_server(harvester_settings)) as mcp_client:
            mcp_tools = await mcp_client.list_tools()

        expect({mcp_tool.name for mcp_tool in mcp_tools}).to(
            equal({"detect_source", "list_targets", "fetch_target", "extract_items", "harvest"})
        )

    async def test_harvests_inbox_csv(self, harvester_settings: HarvesterSettings):
        async with Client(create_server(harvester_settings)) as mcp_client:
            tool_result = await mcp_client.call_tool("harvest", {"location": "inbox://ferreteria.csv"})

        harvest_report = tool_result.structured_content or {}
        expect(harvest_report["errors"]).to(equal([]))
        expect(harvest_report["items"]).to(have_len(1))
        expect(harvest_report["items"][0]["sku"]).to(equal("TB-1"))
        expect(Decimal(harvest_report["items"][0]["price_bob"])).to(equal(Decimal("25.00")))

    async def test_rejects_inbox_path_traversal(self, harvester_settings: HarvesterSettings):
        async with Client(create_server(harvester_settings)) as mcp_client:
            tool_result = await mcp_client.call_tool(
                "harvest", {"location": "inbox://../outside.csv"}, raise_on_error=False
            )

        harvest_report = tool_result.structured_content or {}
        expect(harvest_report["errors"][0]).to(contain("Inbox file not found"))

    async def test_reports_unsupported_source_as_tool_error(self, harvester_settings: HarvesterSettings):
        async with Client(create_server(harvester_settings)) as mcp_client:
            with pytest.raises(ToolError) as tool_error:
                await mcp_client.call_tool("detect_source", {"location": "https://ferreteria.example/tienda"})

        expect(str(tool_error.value)).to(contain("No adapter can handle source"))
