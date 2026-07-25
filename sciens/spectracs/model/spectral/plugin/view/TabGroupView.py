from sciens.spectracs.model.spectral.plugin.view.ReportableView import ReportableView


class TabGroupView(ReportableView):
    # SPEC_simplified_plugin_navigation.md §7b/§7c (T1) — an EXPLICIT container view-model: a labelled group of
    # child view-models the plugin wants shown as SUB-TABS. The Qt renderer draws a QTabWidget (one sub-tab per
    # child, each rendered by a fresh QtWorkflowRenderer); the matplotlib report renderer stacks the children
    # under their tab headings (paper has no tabs). Grouping is plugin-DECLARED — no implicit "N consecutive
    # captures auto-group" heuristic, no `title` field on the child views.
    #
    # `tabs` is an ordered list of (label, childView) pairs. Children may be any view-model and serialize through
    # the ViewModelFactory, so a group round-trips faithfully (nested captures/plots included). Only descriptors
    # persist — a child SpectrumCaptureView carries no pixels (the host fills `.image` after dispatch, traversing
    # into the group), exactly as at top level.

    def __init__(self, tabs=None):
        self.tabs = list(tabs) if tabs else []   # [(label, childView), ...]

    def addTab(self, label, view):
        self.tabs.append((label, view))
        return self

    def children(self):
        return [view for _label, view in self.tabs]

    # --- serialization (recurse children through the ViewModelFactory; imported lazily to avoid the factory ↔
    # view-model import cycle) ---
    def toJson(self):
        return {"type": "tabgroup",
                "tabs": [{"label": label, "view": view.toJson()}
                         for label, view in self.tabs if hasattr(view, "toJson")],
                "isShownInReport": self.isShownInReport}

    @classmethod
    def fromJson(cls, entry):
        from sciens.spectracs.model.spectral.plugin.view.ViewModelFactory import ViewModelFactory
        view = cls()
        for tab in entry.get("tabs", []):
            child = ViewModelFactory.fromJson(tab.get("view") or {})
            if child is not None:
                view.addTab(tab.get("label"), child)
        view.isShownInReport = entry.get("isShownInReport", False)
        return view
