class LimsTarget:
    """Which LIMS backend a plugin wants, and under which config key its credentials live.

    Declared by the plugin (`plugin.getLimsTarget()`); resolved by `LimsGatewayFactory` to a concrete
    adapter. `configKey` selects the `.env` block `LIMS_<configKey>_BASE_URL/_USER/_PASSWORD`, so several
    backends coexist. LIMS-agnostic — no SENAITE terms. See SPEC_lims_integration.md §4.
    """

    def __init__(self, backend: str, configKey: str):
        self.backend = backend          # registry id, e.g. "senaite" / "mock"
        self.configKey = configKey      # .env key prefix, e.g. "SENAITE"

    def toDict(self) -> dict:
        return {"backend": self.backend, "configKey": self.configKey}

    def __repr__(self) -> str:
        return "LimsTarget(backend=%r, configKey=%r)" % (self.backend, self.configKey)
