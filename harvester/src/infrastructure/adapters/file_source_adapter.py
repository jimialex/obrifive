from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

import anyio
import httpx

from src.domain.exceptions import SourceAccessError
from src.domain.models import Artifact, Source, SourceKind, Target
from src.domain.ports import ArtifactStore

INBOX_SCHEME = "inbox"
CONTENT_TYPES_BY_SUFFIX = {
    ".csv": "text/csv",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xls": "application/vnd.ms-excel",
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


@dataclass
class FileSourceAdapter:
    artifact_store: ArtifactStore
    http_client: httpx.AsyncClient
    inbox_dir: Path
    max_download_bytes: int
    kind: SourceKind = SourceKind.FILE

    def can_handle(self, location: str) -> bool:
        parsed_location = urlparse(location)
        if parsed_location.scheme not in (INBOX_SCHEME, "http", "https"):
            return False
        return self._suffix(location) in CONTENT_TYPES_BY_SUFFIX

    async def discover(self, source: Source, max_targets: int) -> list[Target]:
        return [Target(source=source, location=source.location, label=PurePosixPath(source.location).name)]

    async def fetch(self, target: Target) -> Artifact:
        content_type = CONTENT_TYPES_BY_SUFFIX[self._suffix(target.location)]
        if urlparse(target.location).scheme == INBOX_SCHEME:
            content = await self._read_inbox_file(target.location)
        else:
            content = await self._download(target.location)
        return await self.artifact_store.save(target, content, content_type)

    async def _read_inbox_file(self, location: str) -> bytes:
        relative_path = location.removeprefix(f"{INBOX_SCHEME}://")
        inbox_root = await anyio.Path(self.inbox_dir).resolve()
        file_path = await (inbox_root / relative_path).resolve()
        if not file_path.is_relative_to(inbox_root) or not await file_path.is_file():
            raise SourceAccessError(f"Inbox file not found: {relative_path}")
        if (await file_path.stat()).st_size > self.max_download_bytes:
            raise SourceAccessError(f"Inbox file exceeds {self.max_download_bytes} bytes: {relative_path}")
        return await file_path.read_bytes()

    async def _download(self, url: str) -> bytes:
        try:
            async with self.http_client.stream("GET", url, follow_redirects=True) as http_response:
                http_response.raise_for_status()
                downloaded_chunks = bytearray()
                async for chunk in http_response.aiter_bytes():
                    downloaded_chunks.extend(chunk)
                    if len(downloaded_chunks) > self.max_download_bytes:
                        raise SourceAccessError(f"Download exceeds {self.max_download_bytes} bytes: {url}")
                return bytes(downloaded_chunks)
        except httpx.HTTPError as http_error:
            raise SourceAccessError(f"Download failed for {url}: {http_error}")

    @staticmethod
    def _suffix(location: str) -> str:
        return PurePosixPath(urlparse(location).path or location).suffix.lower()
