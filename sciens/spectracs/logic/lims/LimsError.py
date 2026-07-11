class LimsError(Exception):
    """Raised on any LIMS gateway failure (unreachable, auth rejected, create failed, unknown/unconfigured
    backend). `detail` holds a parsed error body or hint when available. See SPEC_lims_integration.md."""

    def __init__(self, message: str, detail=None):
        super().__init__(message)
        self.detail = detail
