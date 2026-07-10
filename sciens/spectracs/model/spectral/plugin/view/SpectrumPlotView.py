from sciens.spectracs.model.spectral.plugin.view.ReportableView import ReportableView


class SpectrumPlotView(ReportableView):
    # A spectrum plot the host draws (PROCESSING absorption, EVALUATION spectrum, reference+sample overlay).
    # SPEC_pumpkin_integration.md B.3 + SPEC_plugin_driven_convergence.md §3 (P2, additive):
    #   - single curve (back-compatible): SpectrumPlotView(spectrum, title)
    #   - overlay: SpectrumPlotView(title=...).addTrace(ref, "Reference", "c").addTrace(sample, "Sample", "y")
    #   - band annotations: pass bands=[(lo_nm, hi_nm, label), ...] (shaded vertical spans)

    def __init__(self, spectrum=None, title=None, traces=None, bands=None, markers=None):
        self.spectrum = spectrum   # primary curve (kept for existing single-spectrum callers)
        self.title = title
        self.traces = traces or []  # extra curves: (spectrum, label, color) tuples
        self.bands = bands or []    # measurement/annotation windows: (lo_nm, hi_nm, label) tuples
        self.markers = markers or []  # vertical annotation lines: (nm, label) tuples (e.g. the Q-peak)

    def addTrace(self, spectrum, label=None, color=None):
        self.traces.append((spectrum, label, color))
        return self

    def addBand(self, lowNm, highNm, label=None):
        self.bands.append((lowNm, highNm, label))
        return self

    def addMarker(self, nm, label=None):
        self.markers.append((nm, label))
        return self

    def allTraces(self):
        # Normalised list of (spectrum, label, color): the primary spectrum first (if any), then extra traces.
        result = []
        if self.spectrum is not None:
            result.append((self.spectrum, None, None))
        result.extend(self.traces)
        return result

    # --- serialization (SPEC_bench_pdf_export.md §5, D2): round-trips EVERY curve (primary + traces) plus the
    # band/marker annotations — the old central ladder kept only the primary spectrum + title. ---
    def toJson(self):
        return {"type": "plot", "title": self.title,
                "spectrum": self.spectrum.toJson() if self.spectrum is not None else None,
                "traces": [{"values": trace[0].toJson() if trace[0] is not None else {},
                            "label": trace[1], "color": trace[2]} for trace in self.traces],
                "bands": [list(band) for band in self.bands],
                "markers": [list(marker) for marker in self.markers],
                "isShownInReport": self.isShownInReport}

    @classmethod
    def fromJson(cls, entry):
        from sciens.spectracs.model.spectral.Spectrum import Spectrum
        primary = Spectrum().fromJson(entry["spectrum"]) if entry.get("spectrum") is not None else None
        view = cls(primary, entry.get("title"),
                   bands=[tuple(band) for band in entry.get("bands", [])],
                   markers=[tuple(marker) for marker in entry.get("markers", [])])
        for trace in entry.get("traces", []):
            view.addTrace(Spectrum().fromJson(trace.get("values", {})), trace.get("label"), trace.get("color"))
        view.isShownInReport = entry.get("isShownInReport", False)
        return view
