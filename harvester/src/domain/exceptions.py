class HarvesterError(Exception):
    pass


class UnsupportedSourceError(HarvesterError):
    def __init__(self, location: str):
        super().__init__(f"No adapter can handle source: {location}")


class NoExtractorError(HarvesterError):
    def __init__(self, content_type: str):
        super().__init__(f"No extractor can read content type: {content_type}")


class ArtifactNotFoundError(HarvesterError):
    def __init__(self, artifact_id: str):
        super().__init__(f"Artifact not found: {artifact_id}")


class SourceAccessError(HarvesterError):
    pass
