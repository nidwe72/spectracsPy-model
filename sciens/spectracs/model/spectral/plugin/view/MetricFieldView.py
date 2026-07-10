from sciens.spectracs.model.spectral.plugin.view.MetricFieldViewStyle import MetricFieldViewStyle
from sciens.spectracs.model.spectral.plugin.view.ReportableView import ReportableView


class MetricFieldView(ReportableView):
    # A form-row metric: a gray label chip + a read-only value field, with a click/hover tooltip carrying
    # the description. Rendered like a Spectrometer-setup field (SPEC_dev_measure_bench.md §17,
    # SPEC_pumpkin_peak_ratio_eval.md §6). Qt-free plain data — the widgets live in QtWorkflowRenderer.
    # `style` (a MetricFieldViewStyle) is optional presentation the plugin attaches; the view-model only carries
    # it, it holds no styling logic of its own (SPEC_bench_small_screen_refinements.md S5).

    def __init__(self, label, value, tooltip=None, style=None):
        self.label = label
        self.value = value
        self.tooltip = tooltip
        self.style = style

    # --- serialization (SPEC_bench_pdf_export.md §5, D2): round-trips the nested style (isLabelBold) too, so the
    # report JSON and persisted-run reload no longer drop the bold-label flag. ---
    def toJson(self):
        return {"type": "metric", "label": self.label, "value": self.value, "tooltip": self.tooltip,
                "style": self.style.toJson() if self.style is not None else None,
                "isShownInReport": self.isShownInReport}

    @classmethod
    def fromJson(cls, entry):
        view = cls(entry["label"], entry["value"], entry.get("tooltip"),
                   MetricFieldViewStyle.fromJson(entry.get("style")))
        view.isShownInReport = entry.get("isShownInReport", False)
        return view
