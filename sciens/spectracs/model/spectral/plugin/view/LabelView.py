from sciens.spectracs.model.spectral.plugin.view.ReportableView import ReportableView


class LabelView(ReportableView):
    # A plain text caption (e.g. "hue 72°"). (SPEC_pumpkin_integration.md B.3)

    def __init__(self, text):
        self.text = text

    # --- serialization (SPEC_bench_pdf_export.md §5, D2): each view-model owns its own toJson/fromJson so the
    # whole-Workflow report JSON can never drift lossy. The "type" tag routes reconstruction via the factory. ---
    def toJson(self):
        return {"type": "label", "text": self.text, "isShownInReport": self.isShownInReport}

    @classmethod
    def fromJson(cls, entry):
        view = cls(entry["text"])
        view.isShownInReport = entry.get("isShownInReport", False)
        return view
