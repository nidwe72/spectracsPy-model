from sciens.spectracs.model.spectral.plugin.view.GaugeRender import GaugeRender
from sciens.spectracs.model.spectral.plugin.view.ReportableView import ReportableView


class VerdictGaugeView(ReportableView):
    # SPEC_roast_ampel.md §8.3 — a generic "classified-metric band": one fixed metric value shown against an
    # ordered set of classes, with a continuous colour band + marker + a semantic verdict badge. Plain, Qt-free
    # data — no logic, no probe. The roast Ampel is one instance (the plugin's RoastGaugeView preset, §8.3a).
    #
    # Colours are 6-digit hex strings, consumed natively by both renderers (D8-colour-format). The plugin owns
    # the colours/labels/gradient (constructor injection, §8.3a). `verdictLabel`/`swatchColor` are CACHED at
    # construction by the plugin (it computes them via GaugeColorUtil — the model must not import core, §8.11 /
    # RD#12) so a saved-runs table reads them off the deserialised item with no maths and no re-run.
    #
    # Fields
    #   value            the fixed metric (read-only)
    #   bandLeft/Right   axis endpoints in metric units (may descend, e.g. 4.0 -> 2.0)
    #   gradientAnchors  ordered [(value, "#hex")] band ramp
    #   thresholds       [float] n class boundaries (n+1 classes)
    #   classes          [{ "label": str, "colors": {"text","bg"[, "printText","printBg"]} }]
    #   valueColor       "#hex" of the value printed ON the swatch (white for roast)
    #   render           a GaugeRender flag set (LABEL|BAND|SWATCH|VALUE)
    #   caption          optional caption
    #   verdictLabel     cached classes[classify(value)].label
    #   swatchColor      cached "#hex" = gradientColorAt(value)

    def __init__(self, value, render, caption=None, bandLeft=None, bandRight=None,
                 gradientAnchors=None, thresholds=None, classes=None, valueColor=None,
                 verdictLabel=None, swatchColor=None):
        self.value = value
        self.render = render if render is not None else GaugeRender(0)
        self.caption = caption
        self.bandLeft = bandLeft
        self.bandRight = bandRight
        self.gradientAnchors = gradientAnchors or []
        self.thresholds = thresholds or []
        self.classes = classes or []
        self.valueColor = valueColor
        self.verdictLabel = verdictLabel
        self.swatchColor = swatchColor

    # --- serialization (SPEC_bench_pdf_export.md §5, D2) — every field round-trips under the "gauge" tag.
    def toJson(self):
        return {"type": "gauge", "value": self.value,
                "bandLeft": self.bandLeft, "bandRight": self.bandRight,
                "gradientAnchors": [[v, c] for v, c in self.gradientAnchors],
                "thresholds": list(self.thresholds),
                "classes": [dict(entry) for entry in self.classes],
                "valueColor": self.valueColor,
                "render": self.render.toNames(),
                "caption": self.caption,
                "verdictLabel": self.verdictLabel, "swatchColor": self.swatchColor,
                "isShownInReport": self.isShownInReport}

    @classmethod
    def fromJson(cls, entry):
        view = cls(
            entry["value"], GaugeRender.fromNames(entry.get("render")), entry.get("caption"),
            bandLeft=entry.get("bandLeft"), bandRight=entry.get("bandRight"),
            gradientAnchors=[tuple(anchor) for anchor in entry.get("gradientAnchors", [])],
            thresholds=list(entry.get("thresholds", [])),
            classes=[dict(cls_) for cls_ in entry.get("classes", [])],
            valueColor=entry.get("valueColor"),
            verdictLabel=entry.get("verdictLabel"), swatchColor=entry.get("swatchColor"))
        view.isShownInReport = entry.get("isShownInReport", False)
        return view
