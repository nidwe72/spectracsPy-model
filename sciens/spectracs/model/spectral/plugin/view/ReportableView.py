class ReportableView:
    # SPEC_bench_pdf_export.md §3 (D1) — the tiny mixin every renderable view-model inherits so the plugin can
    # opt content into the PDF report *wherever it builds it, in any phase*. Predicate-form flag (Edwin): the
    # attribute reads as a boolean (`isShownInReport`), the mutator is a fluent setter returning self.
    # Default False (class attribute) → an instance is out of the report until the plugin flags it. The
    # host's report renderer includes only items whose `isShownInReport` is True; the GUI ignores the flag.
    isShownInReport = False

    # ⭐ SPEC_settled_measurement.md §27.12/§27.13c (D2) — set by the HOST on a view that documents ONE
    # monitored capture, so re-measuring that role REPLACES the view instead of hanging a second, con-
    # tradictory provenance off the same step. ⛔ A CLASS-LEVEL DEFAULT is required, not an attribute the
    # engine invents: `toJson()` reads `self.isMonitorView` on views that were never tagged (the raster
    # group), and without the default that is an AttributeError (§27.14/W2).
    # ⚠ The flag is the HOST's, never the plugin's — a plugin returning a view says nothing about identity.
    isMonitorView = False

    def setShownInReport(self, value=True):
        self.isShownInReport = value
        return self
