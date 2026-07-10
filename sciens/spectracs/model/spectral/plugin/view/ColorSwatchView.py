from sciens.spectracs.model.spectral.plugin.view.ReportableView import ReportableView


class ColorSwatchView(ReportableView):
    # A filled colour block. `rgb` is a plain (r, g, b) tuple of 0-255 ints — Qt-free; the host converts
    # it to a widget. Used for the measured and target swatches. (SPEC_pumpkin_integration.md B.3)

    def __init__(self, rgb, label=None):
        self.rgb = rgb
        self.label = label

    # --- serialization (SPEC_bench_pdf_export.md §5, D2) ---
    def toJson(self):
        return {"type": "swatch", "rgb": list(self.rgb), "label": self.label,
                "isShownInReport": self.isShownInReport}

    @classmethod
    def fromJson(cls, entry):
        view = cls(tuple(entry["rgb"]), entry.get("label"))
        view.isShownInReport = entry.get("isShownInReport", False)
        return view
