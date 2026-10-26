import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import anyio

from src.domain.exceptions import ArtifactNotFoundError
from src.domain.models import Artifact, Target
from src.infrastructure.clock import utc_now

ARTIFACT_ID_LENGTH = 64


@dataclass
class FilesystemArtifactStore:
    root_dir: Path

    async def save(self, target: Target, content: bytes, content_type: str) -> Artifact:
        artifact_id = hashlib.sha256(target.location.encode() + b"\0" + content).hexdigest()
        artifact = Artifact(
            artifact_id=artifact_id,
            target=target,
            content_type=content_type,
            size_bytes=len(content),
            fetched_at=utc_now(),
        )
        artifact_dir = anyio.Path(self.root_dir) / artifact_id
        await artifact_dir.mkdir(parents=True, exist_ok=True)
        await (artifact_dir / "content").write_bytes(content)
        await (artifact_dir / "artifact.json").write_text(artifact.model_dump_json())
        return artifact

    async def get(self, artifact_id: str) -> Artifact:
        metadata_path = self._artifact_dir(artifact_id) / "artifact.json"
        if not await metadata_path.exists():
            raise ArtifactNotFoundError(artifact_id)
        return Artifact.model_validate(json.loads(await metadata_path.read_text()))

    async def read(self, artifact_id: str) -> bytes:
        content_path = self._artifact_dir(artifact_id) / "content"
        if not await content_path.exists():
            raise ArtifactNotFoundError(artifact_id)
        return await content_path.read_bytes()

    def _artifact_dir(self, artifact_id: str) -> anyio.Path:
        is_valid_id = len(artifact_id) == ARTIFACT_ID_LENGTH and all(
            character in "0123456789abcdef" for character in artifact_id
        )
        if not is_valid_id:
            raise ArtifactNotFoundError(artifact_id)
        return anyio.Path(self.root_dir) / artifact_id
