class ColorSwatchView:
    # A filled colour block. `rgb` is a plain (r, g, b) tuple of 0-255 ints — Qt-free; the host converts
    # it to a widget. Used for the measured and target swatches. (SPEC_pumpkin_integration.md B.3)

    def __init__(self, rgb, label=None):
        self.rgb = rgb
        self.label = label
