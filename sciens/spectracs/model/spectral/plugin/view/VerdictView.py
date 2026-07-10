from sciens.spectracs.model.spectral.plugin.view.ReportableView import ReportableView


class VerdictView(ReportableView):
    # The roast verdict as a plain string (e.g. "PERFECT-ROASTED") + the measured hue in degrees, so the
    # saved-runs list reads verdict/hue off this model — no DB column, no string parse.
    # (SPEC_pumpkin_integration.md B.3 / SPEC_workflow_persistence.md P9)

    def __init__(self, roastState, hueDegrees=None):
        self.roastState = roastState
        self.hueDegrees = hueDegrees

    # --- serialization (SPEC_bench_pdf_export.md §5, D2) ---
    def toJson(self):
        return {"type": "verdict", "roastState": self.roastState, "hueDegrees": self.hueDegrees,
                "isShownInReport": self.isShownInReport}

    @classmethod
    def fromJson(cls, entry):
        view = cls(entry["roastState"], entry.get("hueDegrees"))
        view.isShownInReport = entry.get("isShownInReport", False)
        return view
