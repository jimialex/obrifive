from dataclasses import dataclass, field

from src.domain.exceptions import NoExtractorError, UnsupportedSourceError
from src.domain.models import Artifact, SourceKind
from src.domain.ports import ItemExtractor, SourceAdapter


@dataclass
class SourceAdapterRegistry:
    adapters: list[SourceAdapter] = field(default_factory=list)

    def detect(self, location: str) -> SourceAdapter:
        for source_adapter in self.adapters:
            if source_adapter.can_handle(location):
                return source_adapter
        raise UnsupportedSourceError(location)

    def for_kind(self, kind: SourceKind) -> SourceAdapter:
        for source_adapter in self.adapters:
            if source_adapter.kind == kind:
                return source_adapter
        raise UnsupportedSourceError(kind.value)


@dataclass
class ItemExtractorRegistry:
    extractors: list[ItemExtractor] = field(default_factory=list)

    def for_artifact(self, artifact: Artifact) -> ItemExtractor:
        for item_extractor in self.extractors:
            if item_extractor.can_extract(artifact):
                return item_extractor
        raise NoExtractorError(artifact.content_type)
