from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import httpx

from src.application.registries import ItemExtractorRegistry, SourceAdapterRegistry
from src.application.use_cases import DetectSource, ExtractItems, FetchTarget, HarvestSource, ListTargets
from src.infrastructure.adapters.file_source_adapter import FileSourceAdapter
from src.infrastructure.extractors.csv_item_extractor import CsvItemExtractor
from src.infrastructure.settings import HarvesterSettings
from src.infrastructure.stores.filesystem_artifact_store import FilesystemArtifactStore


@dataclass
class HarvesterContainer:
    detect_source: DetectSource
    list_targets: ListTargets
    fetch_target: FetchTarget
    extract_items: ExtractItems
    harvest_source: HarvestSource


@asynccontextmanager
async def build_container(harvester_settings: HarvesterSettings) -> AsyncGenerator[HarvesterContainer]:
    harvester_settings.data_dir.mkdir(parents=True, exist_ok=True)
    harvester_settings.inbox_dir.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(
        timeout=harvester_settings.http_timeout_seconds,
        headers={"User-Agent": harvester_settings.user_agent},
    ) as http_client:
        artifact_store = FilesystemArtifactStore(root_dir=harvester_settings.data_dir)
        source_adapter_registry = SourceAdapterRegistry(
            adapters=[
                FileSourceAdapter(
                    artifact_store=artifact_store,
                    http_client=http_client,
                    inbox_dir=harvester_settings.inbox_dir,
                    max_download_bytes=harvester_settings.max_download_bytes,
                ),
            ]
        )
        item_extractor_registry = ItemExtractorRegistry(extractors=[CsvItemExtractor()])
        detect_source = DetectSource(source_adapter_registry=source_adapter_registry)
        list_targets = ListTargets(source_adapter_registry=source_adapter_registry)
        fetch_target = FetchTarget(source_adapter_registry=source_adapter_registry)
        extract_items = ExtractItems(artifact_store=artifact_store, item_extractor_registry=item_extractor_registry)
        yield HarvesterContainer(
            detect_source=detect_source,
            list_targets=list_targets,
            fetch_target=fetch_target,
            extract_items=extract_items,
            harvest_source=HarvestSource(
                detect_source=detect_source,
                list_targets=list_targets,
                fetch_target=fetch_target,
                extract_items=extract_items,
            ),
        )
