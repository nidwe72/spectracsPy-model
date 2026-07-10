class ReportableView:
    # SPEC_bench_pdf_export.md §3 (D1) — the tiny mixin every renderable view-model inherits so the plugin can
    # opt content into the PDF report *wherever it builds it, in any phase*. Predicate-form flag (Edwin): the
    # attribute reads as a boolean (`isShownInReport`), the mutator is a fluent setter returning self.
    # Default False (class attribute) → an instance is out of the report until the plugin flags it. The
    # host's report renderer includes only items whose `isShownInReport` is True; the GUI ignores the flag.
    isShownInReport = False

    def setShownInReport(self, value=True):
        self.isShownInReport = value
        return self
