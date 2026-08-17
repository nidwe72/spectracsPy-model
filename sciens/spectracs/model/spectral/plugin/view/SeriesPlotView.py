from sciens.spectracs.model.spectral.plugin.view.ReportableView import ReportableView


class SeriesPlotView(ReportableView):
    """A TIME-SERIES plot with stacked panels (SPEC_settled_measurement.md §18.3).

    ⭐⭐ BUILT ONCE, USED THREE TIMES: the live convergence trace during a monitored acquisition (§13.2),
    the Settling step-tab afterwards (§18), and the page that goes into the PDF. That triple use is what
    makes a new view type worth its two renderers (screen + matplotlib).

    ⛔ IT IS NOT `SpectrumPlotView` WITH MINUTES SMUGGLED IN AS NANOMETRES. That lie would surface as a
    wavelength axis in the PDF and in every renderer downstream.

    ⭐ GENERIC: it carries plain numbers under labels the PLUGIN chose. The host renders a series it
    cannot interpret and never learns that "turbidity" is `A_valley` over 500-560 nm — the same boundary
    §10.1a-bis holds in the SDK and §15.2 holds in persistence.

    TWO RENDERING RULES, both found by mocking it before building it (§18.7):
      ⛔ a panel's y-range AUTOSCALES to its data. Drawing the 12-22 domain band as axis levels forces a
         10-unit axis around a 0.5-unit trajectory and the curve collapses to a flat line — the domain
         belongs in the HEADER as a status chip.
      ⭐ per-panel `scale`: `A_valley` falls by a factor of 40, so on a linear axis the settling tail —
         the very thing the gate judges — lives in the bottom 3 % of the panel. It wants "log"; `Q%`
         wants "linear".
    """

    def __init__(self, title=None, xLabel=None, header=None):
        self.title = title
        self.xLabel = xLabel or "minutes"
        self.header = header or []      # [(label, value)] — outcome, answer, duration, clearing time
        self.panels = []                # [{"key", "label", "scale", "series": [], "levels": [],
                                        #   "markers": [], "points": []}]
        self.footer = []                # [(label, value)] — ⭐ policy + evaluator version + exposure:
                                        # without it a saved graph is a picture, not a record (§18.7)

    # --- structure ---

    def addPanel(self, key, label=None, scale="linear"):
        self.panels.append({"key": key, "label": label or key, "scale": scale,
                            "series": [], "levels": [], "markers": [], "points": []})
        return self

    def __panel(self, key):
        for panel in self.panels:
            if panel["key"] == key:
                return panel
        raise KeyError("no panel %r — addPanel() it first" % key)

    # --- content ---

    def addSeries(self, panelKey, xs, ys, label=None, color=None, style=None):
        self.__panel(panelKey)["series"].append(
            {"xs": list(xs), "ys": list(ys), "label": label, "color": color, "style": style})
        return self

    def addLevel(self, panelKey, value, label=None, color=None, style="dashed"):
        # A horizontal guide: the gate threshold, or a domain edge when the value actually approaches one.
        self.__panel(panelKey)["levels"].append(
            {"value": value, "label": label, "color": color, "style": style})
        return self

    def addMarker(self, panelKey, x, label=None, color=None):
        # ⭐ A vertical EVENT line: "gate fired", "re-clouded". Without these the two panels are just
        # wiggly lines — the annotation is where the diagnosis lives.
        self.__panel(panelKey)["markers"].append({"x": x, "label": label, "color": color})
        return self

    def addPoint(self, panelKey, x, y, label=None, color=None):
        # ⭐ THE LATCHED ANSWER. Without it a reader cannot see WHICH row became the number.
        self.__panel(panelKey)["points"].append({"x": x, "y": y, "label": label, "color": color})
        return self

    # --- surround ---

    def addHeaderField(self, label, value):
        self.header.append((label, value))
        return self

    def addFooterField(self, label, value):
        self.footer.append((label, value))
        return self

    # --- serialization (SPEC_bench_pdf_export.md §5, D2). ⭐ Plain data all the way down: the panels hold
    # numbers and labels the PLUGIN chose, so a round-trip needs no knowledge of what any of them mean.
    # ⚠ Without this a saved run would silently DROP the settling curves — the report/persistence path
    # only serializes items that have a toJson(). ---
    def toJson(self):
        return {"type": "series", "title": self.title, "xLabel": self.xLabel,
                "header": [list(field) for field in self.header],
                "footer": [list(field) for field in self.footer],
                "panels": self.panels, "isShownInReport": self.isShownInReport}

    @classmethod
    def fromJson(cls, entry):
        view = cls(title=entry.get("title"), xLabel=entry.get("xLabel"),
                   header=[tuple(field) for field in entry.get("header") or []])
        view.footer = [tuple(field) for field in entry.get("footer") or []]
        view.panels = entry.get("panels") or []
        view.isShownInReport = entry.get("isShownInReport", False)
        return view
