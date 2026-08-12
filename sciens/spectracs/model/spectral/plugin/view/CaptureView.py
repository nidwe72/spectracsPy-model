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
                 wavelengthMinNm=None, wavelengthMaxNm=None, croppedPreview=False,
                 levels=None, guardBandNm=None, guardTargetDn=None, guardColors=None):
        self.prompt = prompt                    # instruction shown to the user
        self.captureLabel = captureLabel        # Measure-button text
        self.showLivePreview = showLivePreview  # show the live camera feed
        self.geometry = geometry                # "transmission" | "reflection" (host may draw an overlay)
        # SPEC_simplified_plugin_navigation.md §5 (Change A): show ONLY the cropped ROI strip in the live preview
        # (default: the whole sensor frame with a dotted ROI box). Display-only; auto-exposure is unaffected.
        self.croppedPreview = croppedPreview
        self.showFramesControl = showFramesControl        # show the frame-count dropdown (default hidden)
        self.showExposureControls = showExposureControls  # show the exposure slider + auto-exposure checkbox
        # SPEC_capture_quality.md §9 (M1) — the usable wavelength window this plugin's lamp actually illuminates.
        # The HOST hard-clamps the captured ROI to it, so the dead lamp bands never enter the stored spectrum.
        # None/None => the host's legacy 400–700 default (non-plugin behaviour unchanged). Must be identical on
        # every capture step of one workflow (Reference and Sample) or T=S/R would divide mismatched domains.
        self.wavelengthMinNm = wavelengthMinNm
        self.wavelengthMaxNm = wavelengthMaxNm
        # SPEC_soret_448_trim.md §25.4 — horizontal guide lines for the LIVE capture preview, in exactly the
        # same shape as SpectrumPlotView's: (value, lowNm, highNm, label, color, style, number). So the DN
        # guard's value, caption, colour and style exist ONCE and the preview cannot drift from the report.
        #
        # ⭐ Why the capture shell carries display numbers at all: the DOSING DECISION IS MADE HERE. Guards on
        # the evaluation plot and in the PDF protect nothing at the moment that matters, and leaving this panel
        # with its own hard-coded 16 would have kept the most-read plot as the stale copy. These are
        # measurement constants the plugin already owns (§16.23.8), not styling.
        # ⚠ Read in DISPLAY DN, the space the live preview draws in. None => the host's legacy 16 DN line.
        # ⚠ Declared PER STEP: §16.23.8 states the guard on min(S) after the SAMPLE capture, so the reference
        # (a solvent blank judged against R ~ 88) declares none.
        self.levels = levels or []
        # SPEC_capture_quality.md §16.23.10f — the window the low-DN statistic is evaluated over, and the
        # colours the MEASURED reading is drawn in.
        #
        # ⭐ Why a window at all (§16.23.10a): the shipped statistic was min(S) over EVERY bin, which on this
        # lamp lands at 417 nm — the blue cutoff — on every single capture. That number is a property of the
        # LAMP, not of the fill, and no recipe changes it. A guard whose value is an instrument constant is
        # not a guard; it fired on all three `20260812_BillaClever` runs and pointed the wrong way.
        #
        # ⚠ COUPLED TO THE METRIC WINDOW (§16.23.10f, R2, Edwin's accepted trade): 448–460 is where the metric
        # reads, and the minimum inside it lands at the window START. Retrim the metric window and this guard
        # moves with it, silently. Recorded so it is not rediscovered as a bug.
        #
        # ⚠ The statistic is computed on the LINEAR spectrum and encoded ONCE for reporting. The thresholds
        # live in ENCODED (camera) DN — settled on `20260804A` in §16.23.10b, after the spec's own §16.23.6b /
        # §16.23.8 were found to quote LINEAR values while calling them DN. Do not re-encode a declared level.
        #
        # None => the host's legacy global-min behaviour, byte-identical, so a non-declaring plugin is unchanged.
        self.guardBandNm = guardBandNm
        # (lowDn, highDn) in ENCODED DN — the window the reading is judged against, DECLARED rather than
        # inferred from `levels`. Kept separate on purpose: `levels` is what gets DRAWN (values, captions,
        # colours, styles) and this is the RULE. A plugin builds both from one pair of constants, so they
        # cannot drift, and adding a decorative level later cannot silently move the verdict.
        #
        # ⚠ 20–50 is Edwin's working window (§16.23.10e) and is PROVISIONAL, not derived: it fits the oil
        # under test (BillaClever, band ratio 4.36) and would call 7 of the 8 correctly-dosed archive runs
        # "too dilute", because guard-at-correct-dilution tracks the OIL's band ratio at r = −0.985
        # (§16.23.10d). ⛔ A fixed DN band cannot carry a dilution verdict across oils — it is a gross-error
        # envelope. The real dilution criterion is `A_Q` ∈ 0.19–0.23, and it lives in EVALUATION.
        self.guardTargetDn = guardTargetDn
        # {"inside": "#RRGGBB", "outside": "#RRGGBB"} — the measured crosshair is green inside guardTargetDn
        # and red outside it (§16.23.10f). The PLUGIN owns the colours, as it owns the levels.
        self.guardColors = guardColors

    def addLevel(self, value, lowNm=None, highNm=None, label=None, color=None, style=None, number=None):
        self.levels.append((value, lowNm, highNm, label, color, style, number))
        return self

    def setGuardBand(self, lowNm, highNm, targetDn=None, colors=None):
        """The window `min(S)` is taken over, plus the target pair and colours it is judged by (§16.23.10f)."""
        self.guardBandNm = (float(lowNm), float(highNm))
        if targetDn is not None:
            self.guardTargetDn = (float(targetDn[0]), float(targetDn[1]))
        if colors is not None:
            self.guardColors = colors
        return self

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

    def setCroppedPreview(self, value=True):
        self.croppedPreview = value
        return self
