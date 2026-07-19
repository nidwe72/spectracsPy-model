from sciens.spectracs.model.spectral.plugin.view.MetricFieldViewStyle import MetricFieldViewStyle
from sciens.spectracs.model.spectral.plugin.view.ReportableView import ReportableView


class MetricFieldView(ReportableView):
    # A form-row metric: a gray label chip + a read-only value field, with a click/hover tooltip carrying
    # the description. Rendered like a Spectrometer-setup field (SPEC_dev_measure_bench.md §17,
    # SPEC_pumpkin_peak_ratio_eval.md §6). Qt-free plain data — the widgets live in QtWorkflowRenderer.
    # `style` (a MetricFieldViewStyle) is optional presentation the plugin attaches; the view-model only carries
    # it, it holds no styling logic of its own (SPEC_bench_small_screen_refinements.md S5).
    #
    # ‡ extended (SPEC_plugin_driven_convergence.md §3, 2026-07-13): optional `color` = a plain (r,g,b) tuple of
    # 0-255 ints. The value cell then renders a filled swatch (field-height) — a labeled colour row that aligns in
    # the same metric grid. The plugin computes the colour (e.g. via EvaluationColorUtil).
    # ‡‡ extended (SPEC_color_retrieval.md, 2026-07-19): `color` and `value` may now BOTH be set — the value cell
    # renders the swatch AND a read-only field side-by-side (a colour chip with its HSL text). Three render cases:
    # color+value → swatch+field; color only → swatch; value only → field (see the renderers).

    def __init__(self, label, value=None, tooltip=None, style=None, color=None):
        self.label = label
        self.value = value
        self.tooltip = tooltip
        self.style = style
        self.color = tuple(color) if color is not None else None

    # --- serialization (SPEC_bench_pdf_export.md §5, D2): round-trips the nested style (isLabelBold) and the
    # optional colour too, so the report JSON and persisted-run reload no longer drop either. ---
    def toJson(self):
        return {"type": "metric", "label": self.label, "value": self.value, "tooltip": self.tooltip,
                "style": self.style.toJson() if self.style is not None else None,
                "color": list(self.color) if self.color is not None else None,
                "isShownInReport": self.isShownInReport}

    @classmethod
    def fromJson(cls, entry):
        color = entry.get("color")
        view = cls(entry["label"], entry.get("value"), entry.get("tooltip"),
                   MetricFieldViewStyle.fromJson(entry.get("style")),
                   tuple(color) if color is not None else None)
        view.isShownInReport = entry.get("isShownInReport", False)
        return view
