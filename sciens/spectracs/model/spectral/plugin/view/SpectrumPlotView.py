from sciens.spectracs.model.spectral.plugin.view.ReportableView import ReportableView


class SpectrumPlotView(ReportableView):
    # A spectrum plot the host draws (PROCESSING absorption, EVALUATION spectrum, reference+sample overlay).
    # SPEC_pumpkin_integration.md B.3 + SPEC_plugin_driven_convergence.md §3 (P2, additive):
    #   - single curve (back-compatible): SpectrumPlotView(spectrum, title)
    #   - overlay: SpectrumPlotView(title=...).addTrace(ref, "Reference", "c").addTrace(sample, "Sample", "y")
    #   - band annotations: pass bands=[(lo_nm, hi_nm, label, color), ...] (shaded vertical spans)
    #   - LEVELS: horizontal annotations — addLevel(value) for a full-width guide line (the DN guards),
    #     addLevel(value, lo, hi) for a BAR spanning a band at that height (a band mean).

    #   - axis="dn": the curves are RAW capture spectra in linear light; draw them on a camera-DN axis instead
    #     (display-only inverse decode + the DN guard lines). SPEC_capture_quality.md §16.7.2e — a linear axis
    #     hides the dim-but-healthy range in its bottom 4% and has already caused a mis-dilution. Use it for
    #     REFERENCE/SAMPLE plots; NOT for absorbance or transmission, which are unitless ratios.
    def __init__(self, spectrum=None, title=None, traces=None, bands=None, markers=None, axis=None,
                 levels=None, legendPosition=None, legendPadding=None):
        self.spectrum = spectrum   # primary curve (kept for existing single-spectrum callers)
        self.title = title
        self.traces = traces or []  # extra curves: (spectrum, label, color, style) tuples
        self.bands = bands or []    # measurement/annotation windows: (lo_nm, hi_nm, label, color) tuples
        self.markers = markers or []  # vertical annotation lines: (nm, label) tuples (e.g. the Q-peak)
        self.levels = levels or []  # horizontal annotations: (value, lo, hi, label, color, style, number)
        self.axis = axis            # None = plot the values as given; "dn" = draw on a camera-DN axis
        # SPEC_soret_448_trim.md §25.2 — the declared legend. None => no legend box (every plot before
        # 2026-08-10). Style (border, fill alpha, badge colours, text colour) is RENDERER-owned: the same
        # view-model is drawn on a dark screen AND on white paper.
        self.legendPosition = legendPosition
        self.legendPadding = legendPadding   # a MAGNITUDE in points; the renderer derives the signs

    def addTrace(self, spectrum, label=None, color=None, style=None):
        # style: None (solid) | "dashed" | "dotted" — SPEC_soret_448_trim.md §12.2. Needed for the FITTED
        # BASELINE, which must read as construction rather than as another measured curve.
        self.traces.append((spectrum, label, color, style))
        return self

    def addBand(self, lowNm, highNm, label=None, color=None):
        self.bands.append((lowNm, highNm, label, color))
        return self

    def addMarker(self, nm, label=None):
        self.markers.append((nm, label))
        return self

    def setLegend(self, position, padding=None):
        """Declare a legend box: which corner (a LegendPosition) and how far in from it (a magnitude).

        The rows are DERIVED — numbered levels first (ascending), then labelled traces in declaration order.
        ⛔ Never a parallel list: a badge and its legend row must be the same fact, or they drift apart the
        first time someone renumbers (SPEC_soret_448_trim.md §23.3).
        """
        self.legendPosition = position
        self.legendPadding = padding
        return self

    def legendRows(self):
        """[(number|None, label, color)] in reading order — the single source of the legend's content.

        A NUMBERED level renders as a badge row (the renderer paints the badge as the sample). A labelled
        TRACE renders as coloured text with no badge: a curve is named by its colour, a measured value by its
        number (§25.2).
        """
        rows = [(level[6], level[3], level[4])
                for level in self.levels if len(level) > 6 and level[6] is not None]
        rows.sort(key=lambda row: row[0])
        for trace in self.allTraces():
            if trace[1]:
                rows.append((None, trace[1], trace[2]))
        return rows

    def addLevel(self, value, lowNm=None, highNm=None, label=None, color=None, style=None, number=None):
        """A horizontal annotation at y=`value` (SPEC_soret_448_trim.md §12.2).

        lowNm/highNm omitted -> a FULL-WIDTH guide line (the 16/60 DN guards, the 20/40 target pair).
        lowNm/highNm given   -> a BAR spanning that band, i.e. a band MEAN drawn where it is measured.

        One primitive rather than two: a band bar IS a level line clipped to an x-range, and keeping them
        together means one renderer branch and one serialised list. It is deliberately NOT a field on
        addBand — a level is a VALUE (it moves with the data) while a band is a WINDOW (a constant of the
        method), and bundling them would make "a guide line with no band" unexpressible.

        ⚠ On an axis="dn" plot the value is read in DISPLAY DN and is NOT gamma-encoded again — the curve is
        decoded for drawing, a declared level is already in that space.

        `number` (§25.2): draw a numbered BADGE on the level and give it a legend row. Declared, never derived
        from position — Edwin's own order is 1 Soret, 2 Q, 3 red anchor, 4 quiet anchor, which is NOT
        wavelength order, and auto-numbering would renumber it to 1,4,2,3 and destroy the grouping.
        """
        self.levels.append((value, lowNm, highNm, label, color, style, number))
        return self

    def allTraces(self):
        # Normalised list of (spectrum, label, color, style): the primary spectrum first (if any), then extras.
        # ⚠ Tolerates 3-tuples from a pre-`style` saved run (fromJson pads, but a hand-built view might not).
        result = []
        if self.spectrum is not None:
            result.append((self.spectrum, None, None, None))
        for trace in self.traces:
            result.append(tuple(trace) + (None,) * (4 - len(trace)))
        return result

    # --- serialization (SPEC_bench_pdf_export.md §5, D2): round-trips EVERY curve (primary + traces) plus the
    # band/marker/level annotations — the old central ladder kept only the primary spectrum + title.
    # ⚠ BACK-COMPAT: `fromJson` must tolerate a missing "levels" and a missing trace "style"/band colour —
    # every DbMeasurement blob written before 2026-08-10 has neither. ---
    def toJson(self):
        return {"type": "plot", "title": self.title,
                "spectrum": self.spectrum.toJson() if self.spectrum is not None else None,
                "traces": [{"values": trace[0].toJson() if trace[0] is not None else {},
                            "label": trace[1], "color": trace[2],
                            "style": trace[3] if len(trace) > 3 else None} for trace in self.traces],
                "bands": [list(band) for band in self.bands],
                "markers": [list(marker) for marker in self.markers],
                "levels": [list(level) for level in self.levels],
                "axis": self.axis,
                "legendPosition": (self.legendPosition.value
                                   if hasattr(self.legendPosition, "value") else self.legendPosition),
                "legendPadding": self.legendPadding,
                "isShownInReport": self.isShownInReport}

    @classmethod
    def fromJson(cls, entry):
        from sciens.spectracs.model.spectral.Spectrum import Spectrum
        from sciens.spectracs.model.spectral.plugin.view.LegendPosition import LegendPosition
        primary = Spectrum().fromJson(entry["spectrum"]) if entry.get("spectrum") is not None else None
        view = cls(primary, entry.get("title"),
                   bands=[cls.__padded(band, 4) for band in entry.get("bands", [])],
                   markers=[tuple(marker) for marker in entry.get("markers", [])],
                   levels=[cls.__padded(level, 7) for level in entry.get("levels", [])],
                   axis=entry.get("axis"),
                   legendPosition=LegendPosition.parse(entry.get("legendPosition")),
                   legendPadding=entry.get("legendPadding"))
        for trace in entry.get("traces", []):
            view.addTrace(Spectrum().fromJson(trace.get("values", {})), trace.get("label"),
                          trace.get("color"), trace.get("style"))
        view.isShownInReport = entry.get("isShownInReport", False)
        return view

    @staticmethod
    def __padded(entry, length):
        # A pre-2026-08-10 blob stores 3-element bands and has no levels at all; pad to today's arity so the
        # renderers can index positionally without guarding every field.
        return tuple(entry) + (None,) * (length - len(entry))
