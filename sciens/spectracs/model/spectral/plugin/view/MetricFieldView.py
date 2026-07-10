class MetricFieldView:
    # A form-row metric: a gray label chip + a read-only value field, with a click/hover tooltip carrying
    # the description. Rendered like a Spectrometer-setup field (SPEC_dev_measure_bench.md §17,
    # SPEC_pumpkin_peak_ratio_eval.md §6). Qt-free plain data — the widgets live in EvaluationResultRenderer.
    # `style` (a MetricFieldViewStyle) is optional presentation the plugin attaches; the view-model only carries
    # it, it holds no styling logic of its own (SPEC_bench_small_screen_refinements.md S5).

    def __init__(self, label, value, tooltip=None, style=None):
        self.label = label
        self.value = value
        self.tooltip = tooltip
        self.style = style
