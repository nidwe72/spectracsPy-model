class MetricFieldViewStyle:
    # Presentation style for a MetricFieldView, kept OUT of the view-model itself (SPEC_bench_small_screen_
    # refinements.md S5): the plugin owns the domain reason ("this metric is a dilution-independent ratio") and
    # expresses it as a style it attaches to the metric. Qt-free plain data — the actual QFont/QSS lives in
    # EvaluationResultRenderer. Built via the fluent Builder so adding attributes later doesn't churn call sites.

    def __init__(self, labelBold=False):
        self.labelBold = labelBold

    @staticmethod
    def builder():
        return MetricFieldViewStyle.Builder()

    class Builder:
        def __init__(self):
            self.__labelBold = False

        def labelBold(self, value=True):
            self.__labelBold = value
            return self

        def build(self):
            return MetricFieldViewStyle(self.__labelBold)
