class LimsPublishView:
    # SPEC_lims_integration.md §3 / L6 — the plugin's PUBLISHING declaration. A plugin adds a "Send to LIMS"
    # step carrying one of these in publishing(); the host renders it as a tab with a Publish button. On click
    # the host builds the M2 PDF and calls the server publish RPC with toPluginLimsInfo() — the client never
    # talks to the LIMS.
    #
    # PASSIVE descriptor (like ReportView — not a dispatchItem visitor node). Carries only the plugin-owned
    # facts: which LIMS to send to (backend + config key) and the sample's type + analyses. The identity half
    # (customer, instrument) is filled server-side from the authenticated AppUser + spectrometer graph.

    def __init__(self, title, sampleTypeName, sampleTypeCode, analyses=None,
                 backend="senaite", configKey="SENAITE"):
        self.title = title
        self.sampleTypeName = sampleTypeName
        self.sampleTypeCode = sampleTypeCode
        self.analyses = analyses or []      # list of {"name":..., "key":..., "group":...}
        self.backend = backend              # LimsGatewayFactory registry id
        self.configKey = configKey          # .env key prefix LIMS_<configKey>_*

    def toPluginLimsInfo(self) -> dict:
        # The plugin slice sent to publishSampleToLims(userId, pluginLimsInfo, pdfBytes).
        return {"target": {"backend": self.backend, "configKey": self.configKey},
                "sampleType": {"name": self.sampleTypeName, "code": self.sampleTypeCode},
                "analyses": [dict(analysis) for analysis in self.analyses]}
