from dataclasses import dataclass

from src.application.registries import ItemExtractorRegistry, SourceAdapterRegistry
from src.domain.exceptions import HarvesterError
from src.domain.models import Artifact, CatalogItem, HarvestLimits, HarvestReport, Source, Target
from src.domain.ports import ArtifactStore


@dataclass
class DetectSource:
    source_adapter_registry: SourceAdapterRegistry

    def execute(self, location: str) -> Source:
        source_adapter = self.source_adapter_registry.detect(location)
        return Source(location=location, kind=source_adapter.kind)


@dataclass
class ListTargets:
    source_adapter_registry: SourceAdapterRegistry

    async def execute(self, source: Source, limits: HarvestLimits) -> list[Target]:
        source_adapter = self.source_adapter_registry.for_kind(source.kind)
        return await source_adapter.discover(source, max_targets=limits.max_targets)


@dataclass
class FetchTarget:
    source_adapter_registry: SourceAdapterRegistry

    async def execute(self, target: Target) -> Artifact:
        source_adapter = self.source_adapter_registry.for_kind(target.source.kind)
        return await source_adapter.fetch(target)


@dataclass
class ExtractItems:
    artifact_store: ArtifactStore
    item_extractor_registry: ItemExtractorRegistry

    async def execute(self, artifact_id: str) -> list[CatalogItem]:
        artifact = await self.artifact_store.get(artifact_id)
        item_extractor = self.item_extractor_registry.for_artifact(artifact)
        artifact_content = await self.artifact_store.read(artifact_id)
        return await item_extractor.extract(artifact, artifact_content)


@dataclass
class HarvestSource:
    detect_source: DetectSource
    list_targets: ListTargets
    fetch_target: FetchTarget
    extract_items: ExtractItems

    async def execute(self, location: str, limits: HarvestLimits) -> HarvestReport:
        source = self.detect_source.execute(location)
        harvest_report = HarvestReport(source=source)
        targets = await self.list_targets.execute(source, limits)
        for target in targets:
            try:
                artifact = await self.fetch_target.execute(target)
                harvest_report.artifacts.append(artifact)
                harvest_report.items.extend(await self.extract_items.execute(artifact.artifact_id))
            except HarvesterError as harvester_error:
                harvest_report.errors.append(f"{target.location}: {harvester_error}")
        return harvest_report
