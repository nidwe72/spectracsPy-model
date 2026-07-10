class CaptureView:
    # SPEC_plugin_driven_convergence.md §2B/§3 (P6) — the interactive acquisition shell for a capture step.
    # Plugin-declared SHELL params only (prompt, button label, preview on/off, geometry hint); the HOST owns
    # the camera mechanics (live feed, burst, per-frame progress) and, on the bench, the dev chrome (exposure/
    # ROI) via decorateCapturePanel. Because it is interactive it does NOT flow through the passive visitor —
    # the host's capture path consumes it (WorkflowPhaseRenderer.__renderCapture).

    def __init__(self, prompt=None, captureLabel="Measure", showLivePreview=True, geometry=None):
        self.prompt = prompt                    # instruction shown to the user
        self.captureLabel = captureLabel        # Measure-button text
        self.showLivePreview = showLivePreview  # show the live camera feed
        self.geometry = geometry                # "transmission" | "reflection" (host may draw an overlay)
