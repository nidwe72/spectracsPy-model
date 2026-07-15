class CaptureView:
    # SPEC_plugin_driven_convergence.md §2B/§3 (P6) — the interactive acquisition shell for a capture step.
    # Plugin-declared SHELL params only (prompt, button label, preview on/off, geometry hint); the HOST owns
    # the camera mechanics (live feed, burst, per-frame progress) and, on the bench, the dev chrome (exposure/
    # ROI) via decorateCapturePanel. Because it is interactive it does NOT flow through the passive visitor —
    # the host's capture path consumes it (WorkflowPhaseRenderer.__renderCapture).
    #
    # The plugin decides whether the dev capture chrome is exposed (Edwin): the frame-count control and the
    # exposure / auto-exposure controls are HIDDEN by default (an end-user plugin wants a bare Measure button;
    # auto-exposure still runs under the hood). The master dev-bench plugin opts them back in via the setters.

    def __init__(self, prompt=None, captureLabel="Measure", showLivePreview=True, geometry=None,
                 showFramesControl=False, showExposureControls=False,
                 wavelengthMinNm=None, wavelengthMaxNm=None):
        self.prompt = prompt                    # instruction shown to the user
        self.captureLabel = captureLabel        # Measure-button text
        self.showLivePreview = showLivePreview  # show the live camera feed
        self.geometry = geometry                # "transmission" | "reflection" (host may draw an overlay)
        self.showFramesControl = showFramesControl        # show the frame-count dropdown (default hidden)
        self.showExposureControls = showExposureControls  # show the exposure slider + auto-exposure checkbox
        # SPEC_capture_quality.md §9 (M1) — the usable wavelength window this plugin's lamp actually illuminates.
        # The HOST hard-clamps the captured ROI to it, so the dead lamp bands never enter the stored spectrum.
        # None/None => the host's legacy 400–700 default (non-plugin behaviour unchanged). Must be identical on
        # every capture step of one workflow (Reference and Sample) or T=S/R would divide mismatched domains.
        self.wavelengthMinNm = wavelengthMinNm
        self.wavelengthMaxNm = wavelengthMaxNm

    def setWavelengthWindow(self, wavelengthMinNm, wavelengthMaxNm):
        self.wavelengthMinNm = wavelengthMinNm
        self.wavelengthMaxNm = wavelengthMaxNm
        return self

    def setShowFramesControl(self, value=True):
        self.showFramesControl = value
        return self

    def setShowExposureControls(self, value=True):
        self.showExposureControls = value
        return self
