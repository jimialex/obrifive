from typing import Protocol

from src.domain.models import Artifact, CatalogItem, Source, SourceKind, Target


class SourceAdapter(Protocol):
    kind: SourceKind

    def can_handle(self, location: str) -> bool: ...

    async def discover(self, source: Source, max_targets: int) -> list[Target]: ...

    async def fetch(self, target: Target) -> Artifact: ...


class ItemExtractor(Protocol):
    def can_extract(self, artifact: Artifact) -> bool: ...

    async def extract(self, artifact: Artifact, content: bytes) -> list[CatalogItem]: ...


class ArtifactStore(Protocol):
    async def save(self, target: Target, content: bytes, content_type: str) -> Artifact: ...

    async def get(self, artifact_id: str) -> Artifact: ...

    async def read(self, artifact_id: str) -> bytes: ...
