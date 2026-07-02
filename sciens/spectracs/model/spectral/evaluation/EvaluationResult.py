class EvaluationResult:
    # A Qt-free, ordered container of renderable view-models (ColorSwatchView, VerdictView, LabelView,
    # SpectrumPlotView). The plugin fills it; the host renders each item into the EVALUATION tab.
    # Carries plain data only (rgb tuples, strings) — no Qt, no logic-layer imports.
    # (SPEC_pumpkin_integration.md B.3 / concept §9.3)

    def __init__(self):
        self.__items = []

    def addItem(self, item):
        self.__items.append(item)
        return self

    def getItems(self):
        return self.__items
