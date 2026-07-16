import colorsys


class SpectralColor:
    """A Qt-free RGB colour (SPEC_project_structure.md S1b / §4d).

    Deliberately shaped like ``QColor``. It is not an homage — ``SpectralColorUtil`` moves to the Qt-free
    ``spectracsPy-core`` tier, but its *inputs* stay Qt: the camera pixels arrive as ``QColor`` via
    ``Spectrum.colorsByPixelIndices`` and reach ``hueSimilarity`` from the app-side calibration path. So a
    ``QColor`` and a ``SpectralColor`` must be interchangeable at every accessor those functions touch, and
    the API surface here is exactly what the call sites already demand — nothing was invented.

    **The achromatic convention is load-bearing: ``hueF()`` returns -1.0 when saturation is 0**, matching Qt.
    That is a *sentinel* ("no hue"), not a bug. It matters because the obvious replacement, ``colorsys``,
    signals the same state with 0.0 — which is a *real* hue there (red). Two colour types disagreeing about
    "no hue" inside one ``hueSimilarity`` call is a silent mis-identified emission line during wavelength
    calibration. Pinned by tests/test_spectral_color_util_characterisation.py.

    Not exported by ``plugin_sdk`` — plugins only ever see plain ``(r, g, b)`` tuples via
    ``EvaluationColorUtil``. So this type is not a contract and stays cheap to reshape (§1c).
    """

    __slots__ = ("_red", "_green", "_blue")

    def __init__(self, red: int, green: int, blue: int):
        self._red = self.__clamp(red)
        self._green = self.__clamp(green)
        self._blue = self.__clamp(blue)

    @staticmethod
    def __clamp(channel) -> int:
        return max(0, min(255, int(round(channel))))

    # --- construction (mirrors QColor's factories) ---
    @classmethod
    def fromRgb(cls, red: int, green: int, blue: int) -> "SpectralColor":
        return cls(red, green, blue)

    @classmethod
    def fromRgbF(cls, red: float, green: float, blue: float) -> "SpectralColor":
        return cls(red * 255.0, green * 255.0, blue * 255.0)

    @classmethod
    def fromHsvF(cls, hue: float, saturation: float, value: float) -> "SpectralColor":
        # Qt maps hue -1 to "achromatic"; colorsys has no such notion, so normalise it to 0 with sat 0.
        if hue < 0:
            hue, saturation = 0.0, 0.0
        red, green, blue = colorsys.hsv_to_rgb(hue, saturation, value)
        return cls.fromRgbF(red, green, blue)

    # --- 8-bit channels ---
    def red(self) -> int:
        return self._red

    def green(self) -> int:
        return self._green

    def blue(self) -> int:
        return self._blue

    # --- normalised channels ---
    def redF(self) -> float:
        return self._red / 255.0

    def greenF(self) -> float:
        return self._green / 255.0

    def blueF(self) -> float:
        return self._blue / 255.0

    # --- HSV ---
    def hueF(self) -> float:
        """Hue in [0, 1) — or **-1.0 when achromatic**, as QColor does. See the class docstring."""
        hue, saturation, _ = self.__hsv()
        return -1.0 if saturation == 0.0 else hue

    def saturationF(self) -> float:
        return self.__hsv()[1]

    def valueF(self) -> float:
        return self.__hsv()[2]

    def __hsv(self):
        return colorsys.rgb_to_hsv(self.redF(), self.greenF(), self.blueF())

    # --- misc (the calibration-lines view builds a stylesheet from this) ---
    def name(self) -> str:
        return "#%02x%02x%02x" % (self._red, self._green, self._blue)

    def isValid(self) -> bool:
        return True

    def __eq__(self, other) -> bool:
        if not isinstance(other, SpectralColor):
            return NotImplemented
        return (self._red, self._green, self._blue) == (other._red, other._green, other._blue)

    def __hash__(self) -> int:
        return hash((self._red, self._green, self._blue))

    def __repr__(self) -> str:
        return "SpectralColor(%d, %d, %d)" % (self._red, self._green, self._blue)
