class ReportView:
    # SPEC_bench_pdf_export.md §1/§2 (D3) — the PDF-report descriptor. A plugin adds a REPORT step carrying one
    # of these in evaluation(); via M1's generic phase renderer it surfaces as a tab beside Metrics | Spectrum,
    # whose body the host renders with matplotlib (a preview that IS the PDF) + a Save action.
    #
    # Deliberately THIN: the report body is NOT listed here — it is gathered generically from the whole
    # workflow by the per-view-model `isShownInReport` flags, so the plugin curates the body by flagging content
    # as it builds it (in any phase), not by re-listing it here. This is a PASSIVE descriptor: it does NOT flow
    # through the dispatchItem visitor (like CaptureView, the host reads it to build the report frame).

    def __init__(self, title, subtitle=None, logo=None, embedMetadata=True):
        self.title = title                  # "Pumpkin-oil measurement report"
        self.subtitle = subtitle            # operator / run timestamp
        self.logo = logo                    # optional asset key; None -> host default (resource/logo.png)
        self.embedMetadata = embedMetadata  # attach the whole-Workflow JSON as a PDF /EmbeddedFiles entry (§5)
