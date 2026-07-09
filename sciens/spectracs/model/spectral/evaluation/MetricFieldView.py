class MetricFieldView:
    # A form-row metric: a gray label chip + a read-only value field, with a click/hover tooltip carrying
    # the description. Rendered like a Spectrometer-setup field (SPEC_dev_measure_bench.md §17,
    # SPEC_pumpkin_peak_ratio_eval.md §6). Qt-free plain data — the widgets live in EvaluationResultRenderer.

    def __init__(self, label, value, tooltip=None):
        self.label = label
        self.value = value
        self.tooltip = tooltip
