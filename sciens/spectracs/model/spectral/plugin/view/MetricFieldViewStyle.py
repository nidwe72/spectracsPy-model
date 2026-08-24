class MetricFieldViewStyle:
    # Presentation style for a MetricFieldView, kept OUT of the view-model itself (SPEC_bench_small_screen_
    # refinements.md S5): the plugin owns the domain reason ("this metric is a dilution-independent ratio") and
    # expresses it as a style it attaches to the metric. Qt-free plain data — the actual QFont/QSS lives in
    # QtWorkflowRenderer. Built via the fluent Builder so adding attributes later doesn't churn call sites.
    # Predicate-form boolean (Edwin): the attribute reads as a boolean (`isLabelBold`) and the mutators are
    # fluent setters (`setLabelBold` / Builder.labelBold), so a reader never mistakes it for a value/enum.

    # ‡ extended (DOC_colour_geometry.md §11 D2 / §12.1, 2026-08-24): `isOutOfGamut` marks a colour chip whose
    # CHROMATICITY lies outside sRGB, so the drawn swatch is a per-channel CLAMP of it and not the colour the
    # numbers describe. It exists because retiring HSL makes the numbers gamut-free while the swatch stays
    # clamped — numbers and swatch disagreeing is worse than both being wrong together. Carried as STYLE and
    # not appended to the value text so it survives into the report JSON as a queryable fact.
    # ⚠ On real pumpkin oil this is the NORMAL case, not an edge case: every absorbed chromaticity in the
    # 88-run archive is out of gamut, and the complement is outside the SPECTRUM LOCUS on 15 % of them.

    def __init__(self, isLabelBold=False, isOutOfGamut=False):
        self.isLabelBold = isLabelBold
        self.isOutOfGamut = isOutOfGamut

    def setLabelBold(self, value=True):
        self.isLabelBold = value
        return self

    def setOutOfGamut(self, value=True):
        self.isOutOfGamut = value
        return self

    # --- serialization (D2): nested inside a MetricFieldView's JSON, so no "type" tag of its own. ---
    def toJson(self):
        return {"isLabelBold": self.isLabelBold, "isOutOfGamut": self.isOutOfGamut}

    @classmethod
    def fromJson(cls, entry):
        if entry is None:
            return None
        return cls(entry.get("isLabelBold", False), entry.get("isOutOfGamut", False))

    @staticmethod
    def builder():
        return MetricFieldViewStyle.Builder()

    class Builder:
        def __init__(self):
            self.__isLabelBold = False
            self.__isOutOfGamut = False

        def labelBold(self, value=True):
            self.__isLabelBold = value
            return self

        def outOfGamut(self, value=True):
            self.__isOutOfGamut = value
            return self

        def build(self):
            return MetricFieldViewStyle(self.__isLabelBold, self.__isOutOfGamut)
