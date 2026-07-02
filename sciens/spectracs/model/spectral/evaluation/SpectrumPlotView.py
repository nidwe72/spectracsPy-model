class SpectrumPlotView:
    # A spectrum curve to plot (e.g. the absorption A(λ)). Carries the Spectrum + a title; the host draws
    # it. Reused by PROCESSING (absorption plot) and EVALUATION. (SPEC_pumpkin_integration.md B.3)

    def __init__(self, spectrum, title=None):
        self.spectrum = spectrum
        self.title = title
