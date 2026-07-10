class MetricFieldViewStyle:
    # Presentation style for a MetricFieldView, kept OUT of the view-model itself (SPEC_bench_small_screen_
    # refinements.md S5): the plugin owns the domain reason ("this metric is a dilution-independent ratio") and
    # expresses it as a style it attaches to the metric. Qt-free plain data — the actual QFont/QSS lives in
    # QtWorkflowRenderer. Built via the fluent Builder so adding attributes later doesn't churn call sites.
    # Predicate-form boolean (Edwin): the attribute reads as a boolean (`isLabelBold`) and the mutators are
    # fluent setters (`setLabelBold` / Builder.labelBold), so a reader never mistakes it for a value/enum.

    def __init__(self, isLabelBold=False):
        self.isLabelBold = isLabelBold

    def setLabelBold(self, value=True):
        self.isLabelBold = value
        return self

    # --- serialization (D2): nested inside a MetricFieldView's JSON, so no "type" tag of its own. ---
    def toJson(self):
        return {"isLabelBold": self.isLabelBold}

    @classmethod
    def fromJson(cls, entry):
        if entry is None:
            return None
        return cls(entry.get("isLabelBold", False))

    @staticmethod
    def builder():
        return MetricFieldViewStyle.Builder()

    class Builder:
        def __init__(self):
            self.__isLabelBold = False

        def labelBold(self, value=True):
            self.__isLabelBold = value
            return self

        def build(self):
            return MetricFieldViewStyle(self.__isLabelBold)
