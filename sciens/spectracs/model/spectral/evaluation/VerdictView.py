class VerdictView:
    # The roast verdict as a plain string (e.g. "PERFECT-ROASTED") + the measured hue in degrees, so the
    # saved-runs list reads verdict/hue off this model — no DB column, no string parse.
    # (SPEC_pumpkin_integration.md B.3 / SPEC_workflow_persistence.md P9)

    def __init__(self, roastState, hueDegrees=None):
        self.roastState = roastState
        self.hueDegrees = hueDegrees
