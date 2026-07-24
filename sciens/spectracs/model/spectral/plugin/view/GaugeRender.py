from enum import Flag, auto


class GaugeRender(Flag):
    # SPEC_roast_ampel.md §8.4 — which components of a VerdictGaugeView a renderer draws. Additive (OR-able);
    # there is NO `FULL` (Edwin 2026-07-23). Serialises as a stable list of lowercase names (D8-render), so the
    # persisted setup reads e.g. ["band","label","swatch"] in workflow.json.
    LABEL = auto()      # the verdict pill
    BAND = auto()       # the gradient band + marker
    SWATCH = auto()     # the solid colour chip, with the value printed on it
    VALUE = auto()      # the numeric metric as standalone text

    def toNames(self):
        return [member.name.lower() for member in GaugeRender if member in self]

    @classmethod
    def fromNames(cls, names):
        result = cls(0)
        for name in (names or []):
            member = cls.__members__.get(name.upper())
            if member is not None:
                result |= member
        return result
