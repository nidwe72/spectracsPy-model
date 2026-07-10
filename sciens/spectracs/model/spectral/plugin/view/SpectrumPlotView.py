class SpectrumPlotView:
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
