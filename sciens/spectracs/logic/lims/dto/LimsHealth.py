class LimsHealth:
    """Result of `LimsGateway.checkConnection()` — is the LIMS reachable and are the credentials
    accepted. `detail` carries a backend-specific hint on failure. See SPEC_lims_integration.md §4/§9."""

    def __init__(self, ok: bool, message: str = "", detail=None):
        self.ok = ok
        self.message = message
        self.detail = detail

    def toDict(self) -> dict:
        return {"ok": self.ok, "message": self.message, "detail": self.detail}

    def __repr__(self) -> str:
        return "LimsHealth(ok=%r, message=%r)" % (self.ok, self.message)
