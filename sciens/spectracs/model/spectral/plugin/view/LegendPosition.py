from enum import Enum


class LegendPosition(str, Enum):
    # SPEC_soret_448_trim.md §25.2 — which corner of the plot a declared legend box is anchored to.
    #
    # A plugin declares the CORNER and a padding MAGNITUDE; the RENDERER derives the offset signs from this
    # enum. ⛔ A plugin that supplied a signed offset (say (-14, 14), which is correct at NORTH_EAST) would
    # push its legend clean off-screen the moment the corner changed — the trap §23.2 walked into with the
    # first pyqtgraph probe.
    NORTH_EAST = 'NORTH_EAST'
    NORTH_WEST = 'NORTH_WEST'
    SOUTH_EAST = 'SOUTH_EAST'
    SOUTH_WEST = 'SOUTH_WEST'

    def corner(self):
        """(x, y) in 0..1 — the corner of the box that is pinned, which is the same corner of the plot."""
        return {LegendPosition.NORTH_EAST: (1.0, 0.0), LegendPosition.NORTH_WEST: (0.0, 0.0),
                LegendPosition.SOUTH_EAST: (1.0, 1.0), LegendPosition.SOUTH_WEST: (0.0, 1.0)}[self]

    def paddingSigns(self):
        """(sx, sy) multipliers for the padding magnitude, so it always points INTO the plot.

        ⚠ y is expressed in SCREEN direction (down-positive), which is what both renderers' offsets use:
        at a north corner the box moves DOWN (+), at a south corner UP (-).
        """
        x, y = self.corner()
        return (-1.0 if x == 1.0 else 1.0, 1.0 if y == 0.0 else -1.0)

    @classmethod
    def parse(cls, value):
        """Tolerant lookup — a serialised plot carries the plain name; None stays None (no legend)."""
        if value is None or isinstance(value, cls):
            return value
        try:
            return cls(str(value))
        except ValueError:
            return None
