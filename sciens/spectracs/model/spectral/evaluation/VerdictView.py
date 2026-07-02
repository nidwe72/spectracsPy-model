class VerdictView:
    # The roast verdict as a plain string (e.g. "PERFECT-ROASTED") so the model layer needs no logic-layer
    # RoastState import. The plugin passes roastState.value. (SPEC_pumpkin_integration.md B.3 / P-B3)

    def __init__(self, roastState):
        self.roastState = roastState
