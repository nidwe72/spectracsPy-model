from typing import Optional


class LimsSampleRef:
    """What a successful `LimsGateway.submit()` returns: the created sample's id (e.g. "OIL-0001") and,
    when the LIMS exposes one, a URL to view it. LIMS-agnostic. See SPEC_lims_integration.md §4."""

    def __init__(self, sampleId: str, url: Optional[str] = None):
        self.sampleId = sampleId
        self.url = url

    def toDict(self) -> dict:
        return {"sampleId": self.sampleId, "url": self.url}

    def __repr__(self) -> str:
        return "LimsSampleRef(sampleId=%r, url=%r)" % (self.sampleId, self.url)
